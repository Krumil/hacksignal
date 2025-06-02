"""Unit tests for scoring module.

Tests score ordering with mocked tweets, follower count filtering,
and keyword matching accuracy.
"""

import unittest
from unittest.mock import patch, mock_open
import json
import os
import sys

# Add parent directory to path so we can import scoring
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import scoring


class TestScoring(unittest.TestCase):
    """Test cases for scoring module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_tweet = {
            "id": "1234567890",
            "text": "AI Hackathon this weekend! $10.8k prize pool, 48-hour sprint. Solo developers welcome! #AIHack",
            "user": {
                "screen_name": "TechEvents",
                "followers_count": 15000
            },
            "created_at": "2024-12-01T10:00:00Z",
            "expanded_url": "https://x.com/TechEvents/status/1234567890"
        }
        
        self.sample_config = {
            "thresholds": {
                "follower_min": 2000,
                "follower_max": 50000,
                "relevance_threshold": 0.6
            }
        }
    
    def test_check_follower_fit_within_range(self):
        """Test follower count validation within target range."""
        with patch('scoring._load_config', return_value=self.sample_config):
            result = scoring.check_follower_fit(15000)
            self.assertEqual(result, 1)
    
    def test_check_follower_fit_below_minimum(self):
        """Test follower count below minimum threshold."""
        with patch('scoring._load_config', return_value=self.sample_config):
            result = scoring.check_follower_fit(1000)
            self.assertEqual(result, 0)
    
    def test_check_follower_fit_above_maximum(self):
        """Test follower count above maximum threshold."""
        with patch('scoring._load_config', return_value=self.sample_config):
            result = scoring.check_follower_fit(100000)
            self.assertEqual(result, 0)
    
    def test_check_follower_fit_edge_cases(self):
        """Test follower count at exact boundaries."""
        with patch('scoring._load_config', return_value=self.sample_config):
            # Test minimum boundary
            result_min = scoring.check_follower_fit(2000)
            self.assertEqual(result_min, 1)
            
            # Test maximum boundary  
            result_max = scoring.check_follower_fit(50000)
            self.assertEqual(result_max, 1)
    
    def test_check_follower_fit_negative_count(self):
        """Test follower count validation with negative values."""
        with patch('scoring._load_config', return_value=self.sample_config):
            with self.assertRaises(ValueError):
                scoring.check_follower_fit(-100)
    
    def test_extract_keywords_valid_text(self):
        """Test keyword extraction from valid tweet text."""
        keywords = scoring.extract_keywords(self.sample_tweet["text"])
        expected_keywords = ["hackathon", "hack"]
        for keyword in expected_keywords:
            self.assertIn(keyword.lower(), [k.lower() for k in keywords])
    
    def test_extract_keywords_invalid_input(self):
        """Test keyword extraction with invalid input types."""
        with self.assertRaises(TypeError):
            scoring.extract_keywords(123)  # Non-string input
        
        with self.assertRaises(TypeError):
            scoring.extract_keywords(None)  # None input
    
    def test_extract_keywords_empty_text(self):
        """Test keyword extraction from empty text."""
        keywords = scoring.extract_keywords("")
        self.assertEqual(keywords, [])
    
    def test_assess_topic_confidence_ai_content(self):
        """Test topic confidence assessment for AI-related content."""
        ai_text = "AI hackathon with machine learning challenges"
        confidence = scoring.assess_topic_confidence(ai_text)
        self.assertGreater(confidence, 0.2)  # Should have some confidence for AI content
    
    def test_assess_topic_confidence_crypto_content(self):
        """Test topic confidence assessment for crypto-related content."""
        crypto_text = "Blockchain hackathon with DeFi and Web3 focus"
        confidence = scoring.assess_topic_confidence(crypto_text)
        self.assertGreater(confidence, 0.2)  # Should have some confidence for crypto content
    
    def test_assess_topic_confidence_irrelevant_content(self):
        """Test topic confidence assessment for irrelevant content."""
        irrelevant_text = "Cooking recipes and gardening tips"
        confidence = scoring.assess_topic_confidence(irrelevant_text)
        self.assertEqual(confidence, 0.0)  # Should have no confidence for irrelevant content
    
    def test_assess_topic_confidence_invalid_input(self):
        """Test topic confidence with invalid input types."""
        with self.assertRaises(TypeError):
            scoring.assess_topic_confidence(123)  # Non-string input
        
        with self.assertRaises(TypeError):
            scoring.assess_topic_confidence(None)  # None input
    
    def test_calculate_relevance_score_structure(self):
        """Test relevance score calculation returns correct structure."""
        score_data = scoring.calculate_relevance_score(self.sample_tweet)
        
        # Check required fields in output schema
        required_fields = ["tweet_id", "score", "account_followers", "keyword_matches", "follower_fit", "expanded_url"]
        for field in required_fields:
            self.assertIn(field, score_data)
        
        # Check data types
        self.assertIsInstance(score_data["tweet_id"], str)
        self.assertIsInstance(score_data["score"], (int, float))
        self.assertIsInstance(score_data["account_followers"], int)
        self.assertIsInstance(score_data["keyword_matches"], list)
        self.assertIsInstance(score_data["follower_fit"], int)
        self.assertIsInstance(score_data["expanded_url"], str)
    
    def test_calculate_relevance_score_invalid_tweet(self):
        """Test relevance score calculation with invalid tweet object."""
        with self.assertRaises(ValueError):
            scoring.calculate_relevance_score({})  # Empty tweet
        
        with self.assertRaises(ValueError):
            scoring.calculate_relevance_score({"id": "123"})  # Missing required fields
    
    def test_validate_tweet_object_valid(self):
        """Test tweet object validation with valid tweet."""
        result = scoring.validate_tweet_object(self.sample_tweet)
        self.assertTrue(result)
    
    def test_validate_tweet_object_missing_fields(self):
        """Test tweet object validation with missing required fields."""
        invalid_tweet = {"id": "123"}  # Missing text and user
        result = scoring.validate_tweet_object(invalid_tweet)
        self.assertFalse(result)
    
    def test_validate_tweet_object_empty(self):
        """Test tweet object validation with empty object."""
        result = scoring.validate_tweet_object({})
        self.assertFalse(result)
    
    def test_score_keywords_presence(self):
        """Test keyword presence scoring."""
        keywords = ["hackathon", "AI", "$10.8k"]
        score = scoring.score_keywords_presence(keywords)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
    
    def test_load_keyword_patterns(self):
        """Test loading keyword patterns from catalog."""
        sample_catalog = {
            "keywords": ["blockchain hackathon", "AI challenge", "crypto bounty"]
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(sample_catalog))):
            keywords = scoring._load_keyword_patterns()
            self.assertEqual(len(keywords), 3)
            self.assertIn("blockchain hackathon", keywords)
    
    def test_load_keyword_patterns_missing_file(self):
        """Test loading keyword patterns when catalog file is missing."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                scoring._load_keyword_patterns()


class TestScoringIntegration(unittest.TestCase):
    """Integration tests for scoring module."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.tweets = [
            {
                "id": "1", "text": "AI hackathon $10.8k prize",
                "user": {"followers_count": 15000}
            },
            {
                "id": "2", "text": "Blockchain challenge $5000",
                "user": {"followers_count": 8000}
            },
            {
                "id": "3", "text": "Random tech conference",
                "user": {"followers_count": 100000}
            }
        ]
    
    def test_score_ordering_consistency(self):
        """Test that scoring produces consistent ordering."""
        scores = []
        for tweet in self.tweets:
            score_data = scoring.calculate_relevance_score(tweet)
            scores.append((tweet["id"], score_data["score"]))
        
        # AI hackathon should score higher than conference
        ai_score = next(score for tid, score in scores if tid == "1")
        conf_score = next(score for tid, score in scores if tid == "3")
        self.assertGreater(ai_score, conf_score)


def run_scoring_on_raw_data():
    """Main function to score tweets from data/raw folder."""
    print("🚀 Starting tweet scoring process...")
    
    try:
        # Score all tweets from raw data
        scored_tweets = scoring.score_tweets_from_raw_data()
        
        if scored_tweets:
            # Save results
            scoring.save_scored_tweets(scored_tweets)
            
            # Print summary
            scoring.print_scoring_summary(scored_tweets)
            
            # Save a summary file with top tweets
            top_tweets = scored_tweets[:20]  # Top 20 tweets
            scoring.save_scored_tweets(top_tweets, "data/enriched/top_scored_tweets.json")
            print(f"\n✅ Top 20 tweets saved to data/enriched/top_scored_tweets.json")

             # Send top tweets to Telegram
            scoring.send_top_tweets_to_telegram(scored_tweets)
        else:
            print("❌ No tweets were successfully scored.")
            
    except Exception as e:
        print(f"❌ Error in scoring process: {e}")


if __name__ == '__main__':
    # When called directly, run the scoring function
    run_scoring_on_raw_data()