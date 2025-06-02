"""Data Ingestion Module

Handles authentication with platform, polling defined sources, and storing raw tweet data.
Implements exponential back-off for rate-limit handling.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
import requests


def authenticate() -> bool:
    """Handle platform authentication using credentials from environment variables.
    
    Returns:
        True if authentication successful, False otherwise
        
    Raises:
        EnvironmentError: When required credentials are missing
        ConnectionError: When authentication fails
    """
    try:
        api_key = os.getenv('RAPID_API_KEY')
        if not api_key:
            raise EnvironmentError("RAPID_API_KEY environment variable is required")
        
        # Test authentication with a simple API call
        url = "https://twitter154.p.rapidapi.com/search/search"
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "twitter154.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        
        # Test with minimal payload
        test_payload = {
            "query": "#test",
            "limit": 1,
            "section": "top"
        }
        
        response = requests.post(url, json=test_payload, headers=headers, timeout=10)
        
        if response.status_code == 401:
            raise ConnectionError("Authentication failed - invalid API key")
        elif response.status_code == 403:
            raise ConnectionError("Authentication failed - access forbidden")
        elif response.status_code >= 400:
            raise ConnectionError(f"Authentication test failed with status {response.status_code}")
        
        return True
        
    except requests.RequestException as e:
        raise ConnectionError(f"Authentication test failed: {e}")


def poll_sources() -> List[Dict[str, Any]]:
    """Fetch tweets from configured sources based on catalog.json settings.
    
    Returns:
        List of raw tweet objects with metadata
        
    Raises:
        RateLimitError: When rate limit is exceeded
        APIError: When platform API returns errors
    """
    try:
        # Load configuration and sources
        config = load_config()
        sources = load_sources()
        
        # Get API credentials
        api_key = os.getenv('RAPID_API_KEY')
        if not api_key:
            raise EnvironmentError("RAPID_API_KEY environment variable is required")
        
        url = "https://twitter154.p.rapidapi.com/search/search"
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "twitter154.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        
        all_tweets = []
        
        # Search by hashtags
        for hashtag_info in sources.get('hashtags', []):
            hashtag = hashtag_info['tag']
            if hashtag_info['relevance'] in ['High', 'Medium']:  # Only fetch high/medium relevance
                tweets = _fetch_tweets_by_query(url, headers, hashtag, config)
                all_tweets.extend(tweets)
                time.sleep(1)  # Small delay between requests
        
        # Search by keywords
        for keyword in sources.get('keywords', []):
            # Focus on hackathon-specific keywords
            if any(term in keyword.lower() for term in ['hackathon', 'challenge', 'competition', 'sprint']):
                tweets = _fetch_tweets_by_query(url, headers, keyword, config)
                all_tweets.extend(tweets)
                time.sleep(1)  # Small delay between requests
        
        # Remove duplicates based on tweet_id
        unique_tweets = {}
        for tweet in all_tweets:
            tweet_id = tweet.get('id')
            if tweet_id and tweet_id not in unique_tweets:
                unique_tweets[tweet_id] = tweet

        # save the data in data/raw/ directory
        for tweet in unique_tweets.values():
            store_raw_tweet(tweet)
        
        return list(unique_tweets.values())
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        else:
            raise APIError(f"API error: {e}")
    except Exception as e:
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

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    payload = {
        "query": query,
        "limit": 5, 
        "section": "top",
        "language": "en",
        "min_likes": 5, 
        "min_retweets": 2, 
        "start_date": yesterday
    }
    
    max_retries = config.get('api', {}).get('max_retries', 3)
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 429:
                # Rate limit hit, implement backoff
                wait_time = handle_rate_limit(attempt)
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            data = response.json()
            
            # Transform API response to match our expected format
            tweets = []
            for result in data.get('results', []):
                tweet = _transform_tweet_format(result)
                tweets.append(tweet)
            
            return tweets
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise APIError(f"Failed to fetch tweets for query '{query}': {e}")
            time.sleep(2)  # Brief pause before retry
    
    return []


def _transform_tweet_format(api_tweet: Dict[str, Any]) -> Dict[str, Any]:
    """Transform Twitter API response format to our internal format.
    
    Args:
        api_tweet: Tweet object from Twitter API
        
    Returns:
        Transformed tweet object matching our schema
    """
    return {
        "id": api_tweet.get("tweet_id"),
        "text": api_tweet.get("text", ""),
        "user": {
            "screen_name": api_tweet.get("user", {}).get("username", ""),
            "followers_count": api_tweet.get("user", {}).get("follower_count", 0),
            "name": api_tweet.get("user", {}).get("name", ""),
            "verified": api_tweet.get("user", {}).get("is_verified", False)
        },
        "created_at": api_tweet.get("creation_date", ""),
        "favorite_count": api_tweet.get("favorite_count", 0),
        "retweet_count": api_tweet.get("retweet_count", 0),
        "reply_count": api_tweet.get("reply_count", 0),
        "lang": api_tweet.get("language", "en"),
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
        raise ValueError("Tweet object must be a non-empty dictionary")
    
    if not tweet.get('id'):
        raise ValueError("Tweet object must contain an 'id' field")
    
    try:
        # Create timestamp and filename
        timestamp = datetime.now().isoformat()
        tweet_id = tweet['id']
        filename = f"tweet_{tweet_id}_{timestamp.replace(':', '-')}.json"
        filepath = os.path.join("data", "raw", filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Add metadata
        tweet_with_metadata = {
            "collected_at": timestamp,
            "tweet_data": tweet
        }
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(tweet_with_metadata, f, indent=2, ensure_ascii=False)
        
        return filename
        
    except (OSError, IOError) as e:
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
    config = load_config()
    max_retries = config.get('api', {}).get('max_retries', 3)
    backoff_factor = config.get('api', {}).get('backoff_factor', 2)
    
    if retry_count >= max_retries:
        raise MaxRetriesExceededError(f"Maximum retry attempts ({max_retries}) exceeded")
    
    # Exponential backoff: 2^retry_count * backoff_factor
    wait_time = (backoff_factor ** retry_count) * 2
    
    return min(wait_time, 60)  # Cap at 60 seconds


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json file.
    
    Returns:
        Configuration dictionary with all settings
        
    Raises:
        FileNotFoundError: When config.json is missing
        ValueError: When config.json contains invalid JSON
    """
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("config.json not found in project root")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config.json: {e}")


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