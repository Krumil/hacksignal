"""Data Ingestion Module

Handles authentication with platform, polling defined sources, and storing raw tweet data.
Implements exponential back-off for rate-limit handling.
"""

import json
import time
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
import os
import requests
import re
from urllib.parse import quote
from config import load_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def authenticate() -> bool:
    """Handle platform authentication using credentials from environment variables.
    
    Returns:
        True if authentication successful, False otherwise
        
    Raises:
        EnvironmentError: When required credentials are missing
        ConnectionError: When authentication fails
    """
    logger.info("Starting authentication process...")
    
    try:
        api_key = os.getenv('RAPID_API_KEY')
        if not api_key:
            logger.error("RAPID_API_KEY environment variable is missing")
            raise EnvironmentError("RAPID_API_KEY environment variable is required")
        
        logger.info("API key found, testing authentication...")
        
        # Test authentication with a simple API call
        url = "https://twitter-api45.p.rapidapi.com/search.php"
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "twitter-api45.p.rapidapi.com"
        }
        
        # Test with minimal payload
        test_params = {
            "query": "#test",
            "search_type": "Top"
        }
        
        logger.debug(f"Testing authentication with URL: {url}")
        response = requests.get(url, headers=headers, params=test_params, timeout=10)
        logger.debug(f"Authentication test response status: {response.status_code}")
        
        if response.status_code == 401:
            logger.error("Authentication failed - invalid API key")
            raise ConnectionError("Authentication failed - invalid API key")
        elif response.status_code == 403:
            logger.error("Authentication failed - access forbidden")
            raise ConnectionError("Authentication failed - access forbidden")
        elif response.status_code >= 400:
            logger.error(f"Authentication test failed with status {response.status_code}")
            raise ConnectionError(f"Authentication test failed with status {response.status_code}")
        
        logger.info("Authentication successful!")
        return True
        
    except requests.RequestException as e:
        logger.error(f"Authentication test failed due to request exception: {e}")
        raise ConnectionError(f"Authentication test failed: {e}")


def poll_sources() -> List[Dict[str, Any]]:
    """Fetch tweets from configured sources based on catalog.json settings.
    
    Returns:
        List of raw tweet objects with metadata
        
    Raises:
        RateLimitError: When rate limit is exceeded
        APIError: When platform API returns errors
    """
    logger.info("Starting source polling pipeline...")
    
    try:
        # Load configuration and sources
        logger.info("Loading configuration and sources...")
        config = _load_config()
        sources = load_sources()
        logger.info(f"Configuration loaded successfully")
        logger.info(f"Sources loaded: {len(sources.get('hashtags', []))} hashtags, {len(sources.get('keywords', []))} keywords")
        
        # Get API credentials
        api_key = os.getenv('RAPID_API_KEY')
        if not api_key:
            logger.error("RAPID_API_KEY environment variable is missing")
            raise EnvironmentError("RAPID_API_KEY environment variable is required")
        
        logger.debug("API credentials retrieved successfully")
        
        url = "https://twitter-api45.p.rapidapi.com/search.php"
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "twitter-api45.p.rapidapi.com"
        }
        
        # Collect all queries to concatenate
        query_terms = []
        logger.info("Building query terms from sources...")
        
        # Add hashtags with high/medium relevance
        hashtag_count = 0
        for hashtag_info in sources.get('hashtags', []):
            hashtag = hashtag_info['tag']
            relevance = hashtag_info['relevance']
            if relevance in ['High', 'Medium']:  # Only fetch high/medium relevance
                query_terms.append(hashtag)
                hashtag_count += 1
                logger.debug(f"Added hashtag: {hashtag} (relevance: {relevance})")
        
        logger.info(f"Added {hashtag_count} hashtags with High/Medium relevance")
        
        # Add hackathon-related keywords
        keyword_count = 0
        for keyword in sources.get('keywords', []):
            # Focus on hackathon-specific keywords
            if any(term in keyword.lower() for term in ['hackathon', 'challenge', 'competition', 'sprint']):
                query_terms.append(keyword)
                keyword_count += 1
                logger.debug(f"Added hackathon keyword: {keyword}")
        
        logger.info(f"Added {keyword_count} hackathon-related keywords")
        
        # Make single API call with concatenated query
        all_tweets = []
        if query_terms:
            logger.info(f"Original query terms: {query_terms}")
            # URL encode each query term to handle spaces properly
            encoded_terms = [quote(term) for term in query_terms]
            concatenated_query = ",".join(encoded_terms)
            logger.info(f"Making API call with encoded query: '{concatenated_query}'")
            logger.info(f"Total query terms: {len(query_terms)}")
            
            tweets = _fetch_tweets_by_query(url, headers, concatenated_query, config)
            all_tweets.extend(tweets)
            logger.info(f"API call completed. Retrieved {len(tweets)} tweets")
        else:
            logger.warning("No query terms found to search for!")
        
        # Remove duplicates based on tweet_id
        logger.info("Processing tweets and removing duplicates...")
        unique_tweets = {}
        duplicate_count = 0
        for tweet in all_tweets:
            tweet_id = tweet.get('id')
            if tweet_id and tweet_id not in unique_tweets:
                unique_tweets[tweet_id] = tweet
            elif tweet_id:
                duplicate_count += 1
                logger.debug(f"Duplicate tweet found: {tweet_id}")

        logger.info(f"Deduplication complete. {len(unique_tweets)} unique tweets, {duplicate_count} duplicates removed")

        # save the data in data/raw/ directory
        logger.info("Storing tweets to data/raw/ directory...")
        stored_count = 0
        for tweet in unique_tweets.values():
            try:
                filename = store_raw_tweet(tweet)
                stored_count += 1
                logger.debug(f"Stored tweet {tweet.get('id')} as {filename}")
            except Exception as e:
                logger.error(f"Failed to store tweet {tweet.get('id')}: {e}")
        
        logger.info(f"Pipeline completed successfully. Stored {stored_count} tweets")
        return list(unique_tweets.values())
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            logger.error("Rate limit exceeded during polling")
            raise RateLimitError("Rate limit exceeded")
        else:
            logger.error(f"HTTP error during polling: {e}")
            raise APIError(f"API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during polling pipeline: {e}")
        raise APIError(f"Unexpected error during polling: {e}")


def _fetch_tweets_by_query(url: str, headers: Dict[str, str], query: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Internal function to fetch tweets for a specific query.
    
    Args:
        url: API endpoint URL
        headers: Request headers with authentication
        query: Search query (hashtag or keyword)
        config: Configuration dictionary
        
    Returns:
        List of tweet objects
    """
    logger.debug(f"Fetching tweets for query: '{query}'")

    querystring = {
        "query": query,
        "search_type": "Latest"
    }
    
    max_retries = config.get('api', {}).get('max_retries', 3)
    logger.debug(f"Max retries configured: {max_retries}")
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"API call attempt {attempt + 1}/{max_retries}")
            response = requests.get(url, headers=headers, params=querystring, timeout=30)
            logger.debug(f"API response status: {response.status_code}")
            
            if response.status_code == 429:
                # Rate limit hit, implement backoff
                logger.warning(f"Rate limit hit on attempt {attempt + 1}")
                wait_time = handle_rate_limit(attempt)
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            data = response.json()
            logger.debug(f"API response received with {len(data.get('timeline', []))} timeline items")
            
            # Transform API response to match our expected format
            tweets = []
            tweet_count = 0
            for result in data.get('timeline', []):
                if result.get('type') == 'tweet':  # Filter out promoted tweets and other types
                    tweet = _transform_tweet_format(result)
                    tweets.append(tweet)
                    tweet_count += 1
                    logger.debug(f"Processed tweet {tweet.get('id')}")
            
            logger.info(f"Successfully processed {tweet_count} tweets from API response")
            return tweets
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                logger.error(f"All retry attempts exhausted for query '{query}'")
                raise APIError(f"Failed to fetch tweets for query '{query}': {e}")
            logger.info(f"Retrying in 2 seconds...")
            time.sleep(2)  # Brief pause before retry
    
    logger.warning(f"No tweets retrieved for query '{query}'")
    return []


def _transform_tweet_format(api_tweet: Dict[str, Any]) -> Dict[str, Any]:
    """Transform Twitter API response format to our internal format.
    
    Args:
        api_tweet: Tweet object from Twitter API
        
    Returns:
        Transformed tweet object matching our schema
    """
    tweet_text = api_tweet.get("text", "")
    
    # Extract URLs from tweet text
    url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    urls = re.findall(url_pattern, tweet_text)
    expanded_url = urls[0] if urls else ""
    
    # Get follower count - use bookmarks as a proxy since follower_count isn't available
    # This is an approximation for engagement scoring
    proxy_followers = api_tweet.get("bookmarks", 0) * 100  # Rough estimation
    
    return {
        "id": api_tweet.get("tweet_id"),
        "text": tweet_text,
        "user": {
            "screen_name": api_tweet.get("screen_name", ""),
            "followers_count": proxy_followers,  # Use bookmark-based estimation
            "name": api_tweet.get("screen_name", ""),  # Use screen_name as fallback
            "verified": False  # Not available in new API
        },
        "created_at": api_tweet.get("created_at", ""),
        "favorite_count": api_tweet.get("favorites", 0),
        "retweet_count": api_tweet.get("retweets", 0),
        "reply_count": api_tweet.get("replies", 0),
        "lang": api_tweet.get("lang", "en"),
        "expanded_url": expanded_url,  # Add extracted URL
        # Store original API response for reference
        "_raw_api_response": api_tweet
    }


def store_raw_tweet(tweet: Dict[str, Any]) -> str:
    """Persist tweet data with timestamps in /data/raw/ directory.
    
    Args:
        tweet: Raw tweet object from platform API
        
    Returns:
        Filename of stored tweet data
        
    Raises:
        IOError: When file write operations fail
        ValueError: When tweet object is invalid
    """
    if not tweet or not isinstance(tweet, dict):
        logger.error("Invalid tweet object: must be a non-empty dictionary")
        raise ValueError("Tweet object must be a non-empty dictionary")
    
    if not tweet.get('id'):
        logger.error("Invalid tweet object: missing 'id' field")
        raise ValueError("Tweet object must contain an 'id' field")
    
    tweet_id = tweet['id']
    logger.debug(f"Storing tweet {tweet_id}...")
    
    try:
        # Create timestamp and filename
        timestamp = datetime.now(timezone.utc).isoformat()
        filename = f"tweet_{tweet_id}_{timestamp.replace(':', '-')}.json"
        filepath = os.path.join("data", "raw", filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        logger.debug(f"Ensured directory exists: {os.path.dirname(filepath)}")
        
        # Add metadata
        tweet_with_metadata = {
            "collected_at": timestamp,
            "tweet_data": tweet
        }
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(tweet_with_metadata, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Successfully stored tweet {tweet_id} to {filename}")
        return filename
        
    except (OSError, IOError) as e:
        logger.error(f"Failed to store tweet {tweet_id}: {e}")
        raise IOError(f"Failed to store tweet {tweet.get('id', 'unknown')}: {e}")


def handle_rate_limit(retry_count: int) -> float:
    """Implement exponential back-off for rate limit handling.
    
    Args:
        retry_count: Number of previous retry attempts
        
    Returns:
        Wait time in seconds before next retry
        
    Raises:
        MaxRetriesExceededError: When max retries reached
    """
    logger.debug(f"Handling rate limit for retry attempt {retry_count}")
    
    config = _load_config()
    max_retries = config.get('api', {}).get('max_retries', 3)
    backoff_factor = config.get('api', {}).get('backoff_factor', 2)
    
    logger.debug(f"Rate limit config - max_retries: {max_retries}, backoff_factor: {backoff_factor}")
    
    if retry_count >= max_retries:
        logger.error(f"Maximum retry attempts ({max_retries}) exceeded")
        raise MaxRetriesExceededError(f"Maximum retry attempts ({max_retries}) exceeded")
    
    # Exponential backoff: 2^retry_count * backoff_factor
    wait_time = (backoff_factor ** retry_count) * 2
    capped_wait_time = min(wait_time, 60)  # Cap at 60 seconds
    
    logger.info(f"Rate limit backoff: retry {retry_count}, calculated wait: {wait_time}s, capped wait: {capped_wait_time}s")
    
    return capped_wait_time


def _load_config() -> Dict[str, Any]:
    """Load configuration using the new environment-aware config system.
    
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: When config.json is missing
        ValueError: When required environment variables are missing
    """
    return load_config()


def load_sources() -> Dict[str, Any]:
    """Load source catalog from sources/catalog.json file.
    
    Returns:
        Source catalog with hashtags, accounts, and keywords
        
    Raises:
        FileNotFoundError: When catalog.json is missing
        ValueError: When catalog.json contains invalid JSON
    """
    try:
        with open('sources/catalog.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("sources/catalog.json not found")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in catalog.json: {e}")


# Custom exception classes
class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""
    pass


class APIError(Exception):
    """Raised when platform API returns errors."""
    pass


class MaxRetriesExceededError(Exception):
    """Raised when maximum retry attempts are exceeded."""
    pass 