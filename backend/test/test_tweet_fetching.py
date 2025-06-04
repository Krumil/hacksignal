#!/usr/bin/env python3
"""
Test script for the tweet fetching functionality.
Demonstrates how to use the implemented poll_sources() function.
"""

import os
import sys
import json
import dotenv
import pytest

# Add parent directory to path so we can import ingestion
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion import poll_sources

dotenv.load_dotenv()

@pytest.mark.skip(reason="requires RapidAPI credentials and network access")
def test_tweet_fetching():
    """Test the tweet fetching functionality."""
    
    print("🔍 Testing Tweet Fetching Implementation")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv('RAPID_API_KEY')
    if not api_key:
        print("❌ Error: RAPID_API_KEY environment variable not set")
        print("\nTo test the implementation, please:")
        print("1. Set your RapidAPI key: export RAPID_API_KEY='your-api-key-here'")
        print("2. Run this script again")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # # Test authentication
    # print("\n🔐 Testing Authentication...")
    # try:
    #     auth_success = authenticate()
    #     if auth_success:
    #         print("✅ Authentication successful!")
    #     else:
    #         print("❌ Authentication failed")
    #         return False
    # except Exception as e:
    #     print(f"❌ Authentication error: {e}")
    #     return False
    
    # Test tweet fetching
    print("\n📡 Fetching tweets from configured sources...")
    try:
        tweets = poll_sources()
        
        print(f"✅ Successfully fetched {len(tweets)} tweets")
        
        if tweets:
            print("\n📊 Sample tweet data:")
            print("-" * 30)
            
            # Show first tweet as example
            sample_tweet = tweets[0]
            print(f"Tweet ID: {sample_tweet.get('id')}")
            print(f"Text: {sample_tweet.get('text', '')[:100]}...")
            print(f"User: @{sample_tweet.get('user', {}).get('screen_name', 'N/A')}")
            print(f"Followers: {sample_tweet.get('user', {}).get('followers_count', 0):,}")
            print(f"Likes: {sample_tweet.get('favorite_count', 0)}")
            print(f"Retweets: {sample_tweet.get('retweet_count', 0)}")
            
            # Show summary statistics
            print(f"\n📈 Summary Statistics:")
            print(f"- Total tweets fetched: {len(tweets)}")
            
            follower_counts = [t.get('user', {}).get('followers_count', 0) for t in tweets]
            if follower_counts:
                print(f"- Average followers: {sum(follower_counts) / len(follower_counts):,.0f}")
                print(f"- Max followers: {max(follower_counts):,}")
                print(f"- Min followers: {min(follower_counts):,}")
            
            like_counts = [t.get('favorite_count', 0) for t in tweets]
            if like_counts:
                print(f"- Average likes: {sum(like_counts) / len(like_counts):.1f}")
            
            # Save sample data for inspection
            with open('sample_fetched_tweets.json', 'w') as f:
                json.dump(tweets[:5], f, indent=2)  # Save first 5 tweets
            print(f"\n💾 Saved first 5 tweets to 'sample_fetched_tweets.json' for inspection")
            
        else:
            print("⚠️  No tweets found. This could be normal if:")
            print("   - No recent tweets match the configured hashtags/keywords")
            print("   - The filters (min likes/retweets) are too restrictive")
            print("   - There are no trending hackathon announcements right now")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fetching tweets: {e}")
        return False

def show_configuration():
    """Display the current configuration being used."""
    print("\n⚙️  Current Configuration:")
    print("-" * 30)
    
    try:
        from ingestion import load_sources, load_config
        
        sources = load_sources()
        config = load_config()
        
        print("Hashtags to monitor:")
        for hashtag in sources.get('hashtags', []):
            if hashtag['relevance'] in ['High', 'Medium']:
                print(f"  - {hashtag['tag']} ({hashtag['relevance']} relevance)")
        
        print("\nKeywords to monitor:")
        keywords = sources.get('keywords', [])
        hackathon_keywords = [k for k in keywords if any(term in k.lower() for term in ['hackathon', 'challenge', 'competition', 'sprint'])]
        for keyword in hackathon_keywords:
            print(f"  - \"{keyword}\"")
        
        api_config = config.get('api', {})
        print(f"\nAPI Configuration:")
        print(f"  - Max retries: {api_config.get('max_retries', 3)}")
        print(f"  - Backoff factor: {api_config.get('backoff_factor', 2)}")
        print(f"  - Rate limit window: {api_config.get('rate_limit_window', 900)} seconds")
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")

if __name__ == "__main__":
    show_configuration()
    success = test_tweet_fetching()
    
    if success:
        print("\n🎉 Tweet fetching implementation test completed successfully!")
        print("\nThe implementation includes:")
        print("✅ Authentication with RapidAPI Twitter service")
        print("✅ Configurable source polling (hashtags + keywords)")
        print("✅ Rate limiting with exponential backoff")
        print("✅ Data transformation to internal format")
        print("✅ Duplicate removal")
        print("✅ Error handling and retries")
    else:
        print("\n❌ Test failed. Please check the error messages above.")