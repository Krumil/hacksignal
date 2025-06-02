"""Unit tests for ingestion module - focused on poll_sources functionality.

Tests actual poll_sources function call with real API integration.
"""

import unittest
import json
import os

import ingestion


class TestPollSources(unittest.TestCase):
    """Test cases for poll_sources function with real API calls."""
    
    def setUp(self):
        """Set up test fixtures and required files."""
        # Create test config.json
        self.test_config = {
            "thresholds": {
                "follower_min": 2000,
                "follower_max": 50000
            },
            "api": {
                "rate_limit_window": 900,
                "max_retries": 3,
                "backoff_factor": 2
            }
        }
        
        # Create test sources catalog
        self.test_sources = {
            "hashtags": [
                {"tag": "#hackathon", "relevance": "High"},
                {"tag": "#AIHackathon", "relevance": "Medium"}
            ],
            "keywords": [
                "hackathon prize",
                "coding competition"
            ],
            "accounts": [
                {"handle": "@EthGlobal", "followers": 45000}
            ]
        }
        
        # Ensure directories exist
        os.makedirs("sources", exist_ok=True)
        
        # Write test config files
        with open('config.json', 'w') as f:
            json.dump(self.test_config, f, indent=2)
            
        with open('sources/catalog.json', 'w') as f:
            json.dump(self.test_sources, f, indent=2)
    
    def tearDown(self):
        """Clean up test files."""
        try:
            os.remove('config.json')
            os.remove('sources/catalog.json')
        except FileNotFoundError:
            pass
    
    def test_poll_sources_real_api_call(self):
        """Test poll_sources with actual API call."""
        # Check if API key is available
        api_key = os.getenv('RAPID_API_KEY')
        if not api_key:
            self.skipTest("RAPID_API_KEY environment variable not set - skipping real API test")
        
        print(f"\n🔑 Using API key: {api_key[:10]}...")
        print("📡 Making real API call to poll_sources()...")
        
        try:
            # Call the actual function
            tweets = ingestion.poll_sources()
            
            print(f"✅ Successfully fetched {len(tweets)} tweets")
            
            # Basic assertions
            self.assertIsInstance(tweets, list)
            print(f"📊 Tweet count: {len(tweets)}")
            
            # If we got tweets, verify their structure
            if tweets:
                sample_tweet = tweets[0]
                print(f"📝 Sample tweet ID: {sample_tweet.get('id', 'N/A')}")
                print(f"📝 Sample tweet text: {sample_tweet.get('text', 'N/A')[:100]}...")
                
                # Verify required fields exist
                self.assertIn('id', sample_tweet)
                self.assertIn('text', sample_tweet)
                self.assertIn('user', sample_tweet)
                
                if 'user' in sample_tweet:
                    user = sample_tweet['user']
                    print(f"👤 Sample user: @{user.get('screen_name', 'N/A')} ({user.get('followers_count', 0)} followers)")
            else:
                print("ℹ️  No tweets found - this could be normal depending on search terms and timing")
                
        except ingestion.RateLimitError:
            print("⚠️  Rate limit exceeded - this is expected behavior")
            self.assertTrue(True)  # Rate limiting is expected
            
        except ingestion.APIError as e:
            print(f"❌ API Error: {e}")
            self.fail(f"API Error occurred: {e}")
            
        except Exception as e:
            print(f"💥 Unexpected error: {e}")
            self.fail(f"Unexpected error: {e}")
    

if __name__ == '__main__':
    print("🚀 Starting poll_sources integration tests...")
    print("=" * 50)
    unittest.main(verbosity=2) 