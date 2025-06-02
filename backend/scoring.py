"""Relevance Scoring Engine

Converts raw tweet objects into numeric Relevance Scores.
Pure, side-effect-free scoring functions with centralized scoring formula.
"""

import json
import os
import glob
import asyncio
import telegram
import shutil
import re
import aiohttp
from typing import Dict, List, Any, Tuple, Union, Optional
from datetime import datetime
from config import load_config, get_telegram_config, get_thresholds_config


def _find_project_root() -> str:
    """Find the project root directory by looking for config.json."""
    # Start from the current file's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Look for config.json in current directory and parent directories
    while current_dir != os.path.dirname(current_dir):  # Not at filesystem root
        config_path = os.path.join(current_dir, 'config.json')
        if os.path.exists(config_path):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    
    # If not found, default to the directory containing this script
    return os.path.dirname(os.path.abspath(__file__))


def calculate_relevance_score(tweet: Dict[str, Any]) -> Dict[str, Any]:
    """Main scoring algorithm that converts tweet to relevance score.
    
    Args:
        tweet: Raw tweet object from platform API
        
    Returns:
        Score object with tweet_id, score, account_followers, keyword_matches, follower_fit, expanded_url
        
    Raises:
        ValueError: When tweet object is missing required fields
        TypeError: When tweet data types are invalid
    """
    if not validate_tweet_object(tweet):
        raise ValueError("Tweet object missing required fields")
    
    # Basic implementation to get started
    tweet_id = tweet["id"]
    text = tweet["text"]
    follower_count = tweet["user"]["followers_count"]
    
    # Component scores
    follower_fit = check_follower_fit(follower_count)
    keywords = extract_keywords(text)
    topic_confidence = assess_topic_confidence(text)
    keyword_score = score_keywords_presence(keywords)
    
    # Weighted scoring formula with keyword quality weighting
    # Scale keyword_score to reasonable range (typical 0-5, scale by 0.02 to get ~0.1 max contribution)
    normalized_keyword_score = min(keyword_score * 0.02, 0.2)
    score = (follower_fit * 0.3) + normalized_keyword_score + (topic_confidence * 0.5)
    
    return {
        "tweet_id": tweet_id,
        "score": min(score, 1.0),  # Cap at 1.0
        "account_followers": follower_count,
        "keyword_matches": keywords,
        "follower_fit": follower_fit,
        "expanded_url": tweet.get('expanded_url', '')
    }


def check_follower_fit(follower_count: int) -> int:
    """Binary follower count validation within 2K-50K range.
    
    Args:
        follower_count: Number of followers for the account
        
    Returns:
        1 if within range (2000-50000), 0 otherwise
        
    Raises:
        ValueError: When follower_count is negative
    """
    config = _load_config()
    min_followers = config['thresholds']['follower_min']
    max_followers = config['thresholds']['follower_max']
    
    if follower_count < 0:
        raise ValueError("Follower count cannot be negative")
    
    return 1 if min_followers <= follower_count <= max_followers else 0


def extract_keywords(text: str) -> List[str]:
    """Identify hackathon-related terms in tweet text.
    
    Args:
        text: Tweet text content to analyze
        
    Returns:
        List of matched hackathon-related keywords
        
    Raises:
        TypeError: When text is not a string
    """
    if not isinstance(text, str):
        raise TypeError("Text must be a string")
    
    # Load keywords from catalog
    keywords_to_check = _load_keyword_patterns()
    found_keywords = []
    
    text_lower = text.lower()
    for keyword in keywords_to_check:
        if keyword.lower() in text_lower:
            found_keywords.append(keyword)
    
    # Also check for common patterns
    hackathon_indicators = ["hackathon", "hack", "challenge", "competition", "sprint"]
    for indicator in hackathon_indicators:
        if indicator in text_lower and indicator not in found_keywords:
            found_keywords.append(indicator)
    
    return found_keywords


def assess_topic_confidence(text: str) -> float:
    """Calculate AI/crypto topic relevance strength.
    
    Args:
        text: Tweet text content to analyze
        
    Returns:
        Confidence score between 0.0 and 1.0 for topic relevance
        
    Raises:
        TypeError: When text is not a string
    """
    if not isinstance(text, str):
        raise TypeError("Text must be a string")
    
    # Simple keyword-based confidence
    ai_terms = ["ai", "artificial intelligence", "machine learning", "ml", "neural", "deep learning"]
    crypto_terms = ["crypto", "blockchain", "bitcoin", "ethereum", "defi", "web3", "nft"]
    
    text_lower = text.lower()
    ai_score = sum(1 for term in ai_terms if term in text_lower)
    crypto_score = sum(1 for term in crypto_terms if term in text_lower)
    
    max_score = max(ai_score, crypto_score)
    return min(max_score * 0.2, 1.0)  # Scale and cap at 1.0


def _load_config() -> Dict[str, Any]:
    """Load configuration using the new environment-aware config system.
    
    Returns:
        Configuration dictionary with thresholds
        
    Raises:
        FileNotFoundError: When config.json is missing
        ValueError: When required environment variables are missing
    """
    return load_config()


def _load_keyword_patterns() -> List[str]:
    """Load keyword patterns from sources catalog.
    
    Returns:
        List of keyword patterns for matching
        
    Raises:
        FileNotFoundError: When catalog.json is missing
    """
    # Get the directory where this script is located
    script_dir = _find_project_root()
    catalog_path = os.path.join(script_dir, 'sources', 'catalog.json')
    
    try:
        with open(catalog_path, 'r') as f:
            catalog = json.load(f)
            return catalog.get('keywords', [])
    except FileNotFoundError:
        raise FileNotFoundError("sources/catalog.json not found")


def score_keywords_presence(keywords: List[str]) -> float:
    """Calculate weighted score for keyword presence.
    
    Args:
        keywords: List of matched keywords
        
    Returns:
        Weighted score based on keyword importance (0.0 to ~10.0 range)
        
    Raises:
        TypeError: When keywords is not a list
    """
    if not isinstance(keywords, list):
        raise TypeError("Keywords must be a list")
    
    if not keywords:
        return 0.0
    
    # Load catalog data for weighting
    try:
        catalog = _load_catalog_data()
        keyword_weights = _build_keyword_weights(catalog)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to simple counting if catalog unavailable
        return float(len(keywords))
    
    # Calculate weighted score
    total_score = 0.0
    for keyword in keywords:
        keyword_lower = keyword.lower()
        
        # Check for exact matches first
        if keyword_lower in keyword_weights:
            total_score += keyword_weights[keyword_lower]
        # Check for partial matches (e.g., hashtags)
        elif keyword.startswith('#'):
            tag_match = next((weight for tag, weight in keyword_weights.items() 
                             if tag.startswith('#') and tag.lower() == keyword_lower), 0.4)
            total_score += tag_match
        else:
            # Default weight for unrecognized but detected keywords
            total_score += 0.4
    
    return total_score


def _load_catalog_data() -> Dict[str, Any]:
    """Load catalog data from sources/catalog.json.
    
    Returns:
        Catalog dictionary with hashtags, accounts, and keywords
        
    Raises:
        FileNotFoundError: When catalog.json is missing
        JSONDecodeError: When catalog.json is invalid
    """
    # Get the directory where this script is located
    script_dir = _find_project_root()
    catalog_path = os.path.join(script_dir, 'sources', 'catalog.json')
    
    try:
        with open(catalog_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("sources/catalog.json not found")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in catalog.json: {e}")


def _build_keyword_weights(catalog: Dict[str, Any]) -> Dict[str, float]:
    """Build keyword weight mapping from catalog data.
    
    Args:
        catalog: Catalog data with hashtags, keywords, etc.
        
    Returns:
        Dictionary mapping keywords to their weight scores
    """
    weights = {}
    
    # Process hashtags with relevance-based weighting
    for hashtag in catalog.get('hashtags', []):
        tag = hashtag['tag'].lower()
        relevance = hashtag.get('relevance', 'Medium')
        
        if relevance == 'High':
            weights[tag] = 2.0
        elif relevance == 'Medium':
            weights[tag] = 1.2
        else:
            weights[tag] = 0.8
    
    # Process catalog keywords with high weight
    for keyword in catalog.get('keywords', []):
        weights[keyword.lower()] = 1.6
    
    # Add common hackathon indicators with moderate weight
    hackathon_indicators = {
        'hackathon': 1.0,
        'hack': 0.8,
        'challenge': 0.8,
        'competition': 0.8,
        'sprint': 0.8,
        'bounty': 1.0,
        'contest': 0.6
    }
    weights.update(hackathon_indicators)
    
    return weights


def validate_tweet_object(tweet: Dict[str, Any]) -> bool:
    """Validate that tweet object has required fields for scoring.
    
    Args:
        tweet: Tweet object to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['id', 'text', 'user']
    return all(field in tweet for field in required_fields)


def archive_previous_top_tweets_and_clear_raw_data() -> None:
    """
    Archives the raw files of the top 10 previously scored tweets to a history folder
    and then clears all tweet_*.json files from the data/raw directory.
    """
    project_root = _find_project_root()
    enriched_scored_tweets_path = os.path.join(project_root, "data", "enriched", "scored_tweets.json")
    raw_data_dir = os.path.join(project_root, "data", "raw")
    history_base_dir = os.path.join(project_root, "data", "history")

    print("Starting archival of previous top tweets and clearing raw data...")

    if not os.path.exists(enriched_scored_tweets_path):
        print(f"No previous scored tweets file found at {enriched_scored_tweets_path}. Skipping archival.")
    else:
        try:
            with open(enriched_scored_tweets_path, 'r', encoding='utf-8') as f:
                previous_scored_tweets = json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {enriched_scored_tweets_path}. Skipping archival.")
            previous_scored_tweets = []
        except Exception as e:
            print(f"Error reading {enriched_scored_tweets_path}: {e}. Skipping archival.")
            previous_scored_tweets = []

        if previous_scored_tweets:
            # Ensure tweets are sorted by score to get the actual top tweets
            previous_scored_tweets.sort(key=lambda x: x.get('score', 0.0), reverse=True)
            top_10_tweets = previous_scored_tweets[:10]

            if top_10_tweets:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                current_history_dir = os.path.join(history_base_dir, timestamp)
                os.makedirs(current_history_dir, exist_ok=True)
                print(f"Archiving top {len(top_10_tweets)} tweets to {current_history_dir}")

                archived_count = 0
                for tweet_data in top_10_tweets:
                    if 'source_file' in tweet_data and tweet_data['source_file']:
                        source_file_name = tweet_data['source_file']
                        source_path = os.path.join(raw_data_dir, source_file_name)
                        destination_path = os.path.join(current_history_dir, source_file_name)

                        if os.path.exists(source_path):
                            try:
                                shutil.copy2(source_path, destination_path)
                                archived_count += 1
                            except Exception as e:
                                print(f"Error copying {source_path} to {destination_path}: {e}")
                        else:
                            print(f"Source file {source_path} for tweet ID {tweet_data.get('tweet_id')} not found in raw data. Skipping.")
                    else:
                        print(f"Tweet ID {tweet_data.get('tweet_id')} missing 'source_file' information. Skipping archival for this tweet.")
                print(f"Archived {archived_count} tweet files.")
            else:
                print("No top tweets to archive from previous run (based on data in enriched/scored_tweets.json).")
        else:
            print(f"No previous scored tweets data found in {enriched_scored_tweets_path} to process for archival.")

    # Delete all tweet_*.json files from data/raw
    print(f"Clearing tweet_*.json files from {raw_data_dir}...")
    raw_tweet_files_pattern = os.path.join(raw_data_dir, "tweet_*.json")
    files_to_delete = glob.glob(raw_tweet_files_pattern)
    
    deleted_count = 0
    if not files_to_delete:
        print(f"No {os.path.basename(raw_tweet_files_pattern)} files found in {raw_data_dir} to delete.")
    else:
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
        print(f"Deleted {deleted_count} {os.path.basename(raw_tweet_files_pattern)} files from {raw_data_dir}.")
    print("Archival and raw data clearing step completed.")


def score_tweets_from_raw_data(raw_data_dir: str = "data/raw") -> List[Dict[str, Any]]:
    """Score all tweets from the raw data directory.
    
    Args:
        raw_data_dir: Path to directory containing raw tweet JSON files
        
    Returns:
        List of score objects sorted by score (highest first)
        
    Raises:
        FileNotFoundError: When raw data directory doesn't exist
    """
    # Get the directory where this script is located (project root)
    script_dir = _find_project_root()
    
    # If raw_data_dir is relative, make it relative to the script directory
    if not os.path.isabs(raw_data_dir):
        raw_data_dir = os.path.join(script_dir, raw_data_dir)
    
    if not os.path.exists(raw_data_dir):
        raise FileNotFoundError(f"Raw data directory '{raw_data_dir}' not found")
    
    scored_tweets = []
    tweet_files = glob.glob(os.path.join(raw_data_dir, "tweet_*.json"))
    
    print(f"Found {len(tweet_files)} tweet files to process...")
    
    for file_path in tweet_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extract tweet_data from the file structure
            if 'tweet_data' in data:
                tweet = data['tweet_data']
                
                # Normalize the tweet structure for our scoring function
                normalized_tweet = _normalize_tweet_structure(tweet)
                
                if validate_tweet_object(normalized_tweet):
                    score_data = calculate_relevance_score(normalized_tweet)
                    score_data['source_file'] = os.path.basename(file_path)
                    score_data['collected_at'] = data.get('collected_at', '')
                    scored_tweets.append(score_data)
                else:
                    print(f"Invalid tweet structure in {file_path}")
                    
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON in {file_path}: {e}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Sort by score (highest first)
    scored_tweets.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"Successfully scored {len(scored_tweets)} tweets")
    return scored_tweets


def _normalize_tweet_structure(tweet: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize tweet structure to match our scoring expectations.
    
    Args:
        tweet: Raw tweet data from file
        
    Returns:
        Normalized tweet object compatible with calculate_relevance_score
    """
    # Handle different possible structures from the raw data
    normalized = {
        'id': tweet.get('id', ''),
        'text': tweet.get('text', ''),
        'user': {
            'screen_name': tweet.get('user', {}).get('screen_name', ''),
            'followers_count': tweet.get('user', {}).get('followers_count', 0)
        },
        'created_at': tweet.get('created_at', '')
    }
    
    # Extract expanded_url and construct tweet URL
    expanded_url = None
    username = normalized['user']['screen_name']
    tweet_id = normalized['id']
    
    # Try to get expanded_url from _raw_api_response
    if '_raw_api_response' in tweet:
        raw_response = tweet['_raw_api_response']
        
        # Update follower count from raw response if available
        if 'user' in raw_response:
            normalized['user']['followers_count'] = raw_response['user'].get('follower_count', 
                                                                           normalized['user']['followers_count'])
        
        # Get expanded_url, but clean it up if it's a media URL
        if 'expanded_url' in raw_response:
            expanded_url = raw_response['expanded_url']
            # If it's a media URL, construct the main tweet URL
            if expanded_url and ('/photo/' in expanded_url or '/video/' in expanded_url):
                expanded_url = f"https://x.com/{username}/status/{tweet_id}"
            elif not expanded_url:
                # If expanded_url is None or empty, construct tweet URL
                expanded_url = f"https://x.com/{username}/status/{tweet_id}"
        else:
            # Construct tweet URL from username and ID
            expanded_url = f"https://x.com/{username}/status/{tweet_id}"
    else:
        # Construct tweet URL from username and ID as fallback
        expanded_url = f"https://x.com/{username}/status/{tweet_id}"
    
    normalized['expanded_url'] = expanded_url
    
    return normalized


def save_scored_tweets(scored_tweets: List[Dict[str, Any]], output_file: str = "data/enriched/scored_tweets.json") -> None:
    """Save scored tweets to output file.
    
    Args:
        scored_tweets: List of scored tweet objects
        output_file: Path to output file
    """
    # Get the directory where this script is located (project root)
    script_dir = _find_project_root()
    
    # If output_file is relative, make it relative to the script directory
    if not os.path.isabs(output_file):
        output_file = os.path.join(script_dir, output_file)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(scored_tweets, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(scored_tweets)} scored tweets to {output_file}")


def print_scoring_summary(scored_tweets: List[Dict[str, Any]], top_n: int = 10) -> None:
    """Print a summary of scoring results.
    
    Args:
        scored_tweets: List of scored tweet objects
        top_n: Number of top tweets to display details for
    """
    if not scored_tweets:
        print("No tweets were scored.")
        return
    
    print(f"\n=== SCORING SUMMARY ===")
    print(f"Total tweets scored: {len(scored_tweets)}")
    print(f"Average score: {sum(t['score'] for t in scored_tweets) / len(scored_tweets):.3f}")
    print(f"Highest score: {scored_tweets[0]['score']:.3f}")
    print(f"Lowest score: {scored_tweets[-1]['score']:.3f}")
    
    # Count tweets by score ranges
    high_relevance = sum(1 for t in scored_tweets if t['score'] >= 0.8)
    medium_relevance = sum(1 for t in scored_tweets if 0.5 <= t['score'] < 0.8)
    low_relevance = sum(1 for t in scored_tweets if t['score'] < 0.5)
    
    print(f"\nScore Distribution:")
    print(f"  High relevance (≥0.8): {high_relevance} tweets")
    print(f"  Medium relevance (0.5-0.8): {medium_relevance} tweets")
    print(f"  Low relevance (<0.5): {low_relevance} tweets")
    
    print(f"\n=== TOP {min(top_n, len(scored_tweets))} TWEETS ===")
    for i, tweet in enumerate(scored_tweets[:top_n], 1):
        print(f"\n#{i} (Score: {tweet['score']:.3f})")
        print(f"URL: {tweet.get('expanded_url', 'N/A')}")
        print(f"Followers: {tweet['account_followers']:,}")
        print(f"Keywords: {', '.join(tweet['keyword_matches']) if tweet['keyword_matches'] else 'None'}")
        
        # Get text from source if available
        if 'source_file' in tweet:
            try:
                # Get the directory where this script is located (project root)
                script_dir = _find_project_root()
                file_path = os.path.join(script_dir, "data", "raw", tweet['source_file'])
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    text = data.get('tweet_data', {}).get('text', '')[:200] + "..."
                    print(f"Text: {text}")
            except:
                pass


async def send_telegram_message(bot_token: str, channel_id: str, message: str) -> bool:
    """Send a message to a Telegram channel using python-telegram-bot.
    
    Args:
        bot_token: Telegram bot token
        channel_id: Channel ID (can start with @ or be numeric)
        message: Message text to send
        
    Returns:
        True if message was sent successfully, False otherwise
    """
    try:
        bot = telegram.Bot(token=bot_token)
        async with bot:
            await bot.send_message(
                chat_id=channel_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
        return True
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False


def format_tweet_for_telegram(tweet: Dict[str, Any], rank: int) -> str:
    """Format a tweet for Telegram message.
    
    Args:
        tweet: Scored tweet object
        rank: Tweet ranking position
        
    Returns:
        Formatted message string for Telegram
    """
    score = tweet['score']
    followers = tweet['account_followers']
    keywords = tweet.get('keyword_matches', [])
    url = tweet.get('expanded_url', '')
    
    # Create emoji based on score
    if score >= 0.9:
        emoji = "🔥"
    elif score >= 0.8:
        emoji = "⭐"
    elif score >= 0.7:
        emoji = "✨"
    else:
        emoji = "📝"
    
    message = f"{emoji} <b>#{rank} Tweet (Score: {score:.3f})</b>\n\n"
    
    if keywords:
        message += f"🏷️ <b>Keywords:</b> {', '.join(keywords)}\n"
    
    message += f"👥 <b>Followers:</b> {followers:,}\n"
    
    if url:
        message += f"🔗 <a href='{url}'>View Tweet</a>\n"
    
    return message


async def send_top_tweets_to_telegram_async(scored_tweets: List[Dict[str, Any]]) -> None:
    """Send top scored tweets to Telegram channel using async python-telegram-bot.
    
    Args:
        scored_tweets: List of scored tweet objects (sorted by score)
    """
    try:
        config = _load_config()
        telegram_config = config.get('telegram', {})
        
        if not telegram_config.get('enabled', False):
            print("Telegram integration is disabled in config")
            return
        
        bot_token = telegram_config.get('bot_token')
        channel_id = telegram_config.get('channel_id')
        max_tweets = telegram_config.get('max_tweets_to_send', 10)
        min_score = telegram_config.get('min_score_to_send', 0.7)
        
        if not bot_token or not channel_id:
            print("Telegram bot token or channel ID not configured")
            return
        
        if bot_token == "YOUR_BOT_TOKEN_HERE" or channel_id == "YOUR_CHANNEL_ID_HERE":
            print("Please configure your Telegram bot token and channel ID in config.json")
            return
        
        # Filter tweets by minimum score
        filtered_tweets = [t for t in scored_tweets if t['score'] >= min_score]
        
        if not filtered_tweets:
            print(f"No tweets meet the minimum score threshold of {min_score}")
            return
        
        # Limit to max tweets
        tweets_to_send = filtered_tweets[:max_tweets]
        
        print(f"Sending {len(tweets_to_send)} top tweets to Telegram...")
        print(f"Using channel ID: {channel_id}")
        
        # Create bot instance with timeout
        bot = telegram.Bot(token=bot_token)
        
        try:
            # Test the bot connection first
            async with bot:
                me = await bot.get_me()
                print(f"Bot connected successfully: @{me.username}")
                
                # Send header message
                header_message = f"🎯 <b>Top {len(tweets_to_send)} Hackathon Tweets</b>\n\n"
                header_message += f"📊 Found {len(scored_tweets)} total tweets\n"
                header_message += f"✅ {len(filtered_tweets)} tweets above score {min_score}\n"
                header_message += f"⏰ Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                print("Sending header message...")
                try:
                    await bot.send_message(
                        chat_id=channel_id,
                        text=header_message,
                        parse_mode='HTML',
                        disable_web_page_preview=False
                    )
                    print("Header message sent successfully!")
                except Exception as header_error:
                    print(f"Error sending header message: {header_error}")
                    # Try sending without HTML parse mode as fallback
                    try:
                        print("Retrying without HTML parse mode...")
                        await bot.send_message(
                            chat_id=channel_id,
                            text=header_message.replace('<b>', '').replace('</b>', '')
                        )
                        print("Header message sent successfully (plain text)!")
                    except Exception as plain_error:
                        print(f"Failed to send even plain text: {plain_error}")
                        raise
                
                # Send individual tweets
                success_count = 0
                for i, tweet in enumerate(tweets_to_send, 1):
                    try:
                        message = format_tweet_for_telegram(tweet, i)
                        print(f"Sending tweet #{i}...")
                        await bot.send_message(
                            chat_id=channel_id,
                            text=message,
                            parse_mode='HTML',
                            disable_web_page_preview=False
                        )
                        success_count += 1
                        print(f"Tweet #{i} sent successfully!")
                        
                        # Add small delay to avoid hitting rate limits
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        print(f"Failed to send tweet #{i}: {e}")
                
                print(f"\nSuccessfully sent {success_count}/{len(tweets_to_send)} tweets to Telegram")
        
        except telegram.error.Unauthorized as e:
            print(f"\nERROR: Bot unauthorized. Please check:")
            print("1. The bot token is correct")
            print("2. The bot is added as an admin to the channel")
            print(f"Error details: {e}")
        except telegram.error.BadRequest as e:
            print(f"\nERROR: Bad request. Please check:")
            print("1. The channel ID is correct (including the negative sign)")
            print("2. The channel exists and is accessible")
            print(f"Error details: {e}")
        except asyncio.TimeoutError:
            print("\nERROR: Connection timeout. Please check your internet connection.")
        except Exception as e:
            print(f"\nERROR: Unexpected error: {type(e).__name__}: {e}")
        
    except Exception as e:
        print(f"Error in Telegram integration setup: {e}")


def send_top_tweets_to_telegram(scored_tweets: List[Dict[str, Any]]) -> None:
    """Synchronous wrapper for async Telegram functionality.
    
    Args:
        scored_tweets: List of scored tweet objects (sorted by score)
    """
    try:
        # Create a new event loop with timeout
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run with a 30-second timeout
        try:
            loop.run_until_complete(
                asyncio.wait_for(
                    send_top_tweets_to_telegram_async(scored_tweets),
                    timeout=30.0
                )
            )
        except asyncio.TimeoutError:
            print("\nERROR: Telegram operation timed out after 30 seconds.")
            print("Possible issues:")
            print("1. Network connectivity problems")
            print("2. Telegram API is unreachable")
            print("3. Invalid bot token or channel ID")
        finally:
            loop.close()
            
    except Exception as e:
        print(f"Error running Telegram integration: {e}")


# Removed main function - main.py handles orchestration 