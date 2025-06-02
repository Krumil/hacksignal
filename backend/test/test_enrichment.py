"""Unit tests for enrichment module.

Tests prize amount extraction from various formats, duration parsing edge cases,
and currency conversion accuracy.
"""

import unittest
from unittest.mock import patch

import enrichment


class TestEnrichment(unittest.TestCase):
    """Test cases for enrichment module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_texts = {
            "usd_prize": "Join our AI hackathon! $10,800 prize pool awaits!",
            "usd_prize_alt": "Crypto challenge with $5,000 in prizes",
            "k_format": "Win $10.8k this weekend at our blockchain hackathon",
            "eth_prize": "DeFi hackathon offering 5.5 ETH as grand prize",
            "btc_prize": "Build on Bitcoin! 0.1 BTC reward for best dapp",
            "weekend_duration": "48-hour weekend sprint hackathon",
            "explicit_hours": "Join our 72-hour coding marathon",
            "day_format": "3-day blockchain hackathon starting Friday"
        }
    
    def test_extract_prize_amount_eur_format(self):
        """Test prize extraction from EUR format."""
        # TODO: Implement when extract_prize_amount() function is completed
        # prize, currency = enrichment.extract_prize_amount(self.sample_texts["eur_prize"])
        # self.assertEqual(prize, 10000.0)
        # self.assertEqual(currency, "EUR")
        pass
    
    def test_extract_prize_amount_usd_format(self):
        """Test prize extraction from USD format."""
        # TODO: Implement when extract_prize_amount() function is completed
        # prize, currency = enrichment.extract_prize_amount(self.sample_texts["usd_prize"])
        # self.assertEqual(prize, 10800.0)
        # self.assertEqual(currency, "USD")
        pass
    
    def test_extract_prize_amount_alt_usd_format(self):
        """Test prize extraction from alternate USD format with conversion."""
        # TODO: Implement when extract_prize_amount() function is completed
        # prize, currency = enrichment.extract_prize_amount(self.sample_texts["usd_prize_alt"])
        # self.assertGreater(prize, 0)  # Should be converted to USD
        # self.assertEqual(currency, "USD")
        pass
    
    def test_extract_prize_amount_k_format(self):
        """Test prize extraction from 'k' abbreviated format."""
        # TODO: Implement when extract_prize_amount() function is completed
        # prize, currency = enrichment.extract_prize_amount(self.sample_texts["k_format"])
        # self.assertEqual(prize, 10800.0)
        # self.assertEqual(currency, "USD")
        pass
    
    def test_extract_prize_amount_crypto_currencies(self):
        """Test prize extraction from cryptocurrency formats."""
        # TODO: Implement when extract_prize_amount() function is completed
        # Test ETH
        # eth_prize, eth_currency = enrichment.extract_prize_amount(self.sample_texts["eth_prize"])
        # self.assertGreater(eth_prize, 0)  # Should be converted to USD
        # self.assertEqual(eth_currency, "ETH")
        # 
        # # Test BTC
        # btc_prize, btc_currency = enrichment.extract_prize_amount(self.sample_texts["btc_prize"])
        # self.assertGreater(btc_prize, 0)  # Should be converted to USD
        # self.assertEqual(btc_currency, "BTC")
        pass
    
    def test_extract_prize_amount_no_prize(self):
        """Test prize extraction when no prize is mentioned."""
        # TODO: Implement when extract_prize_amount() function is completed
        # with self.assertRaises(ValueError):
        #     enrichment.extract_prize_amount("Just a regular tech meetup")
        pass
    
    def test_extract_prize_amount_invalid_input(self):
        """Test prize extraction with invalid input types."""
        with self.assertRaises(TypeError):
            enrichment.extract_prize_amount(123)  # Non-string input
        
        with self.assertRaises(TypeError):
            enrichment.extract_prize_amount(None)  # None input
    
    def test_parse_duration_explicit_hours(self):
        """Test duration parsing from explicit hour mentions."""
        # TODO: Implement when parse_duration() function is completed
        # duration = enrichment.parse_duration(self.sample_texts["explicit_hours"])
        # self.assertEqual(duration, 72)
        pass
    
    def test_parse_duration_weekend_sprint(self):
        """Test duration parsing for weekend sprint format."""
        # TODO: Implement when parse_duration() function is completed
        # duration = enrichment.parse_duration(self.sample_texts["weekend_duration"])
        # self.assertEqual(duration, 48)  # Weekend = 48 hours
        pass
    
    def test_parse_duration_day_format(self):
        """Test duration parsing from day format."""
        # TODO: Implement when parse_duration() function is completed
        # duration = enrichment.parse_duration(self.sample_texts["day_format"])
        # self.assertEqual(duration, 72)  # 3 days = 72 hours
        pass
    
    def test_parse_duration_no_duration(self):
        """Test duration parsing when no duration is mentioned."""
        # TODO: Implement when parse_duration() function is completed
        # with self.assertRaises(ValueError):
        #     enrichment.parse_duration("Just an announcement about hackathons")
        pass
    
    def test_parse_duration_invalid_input(self):
        """Test duration parsing with invalid input types."""
        with self.assertRaises(TypeError):
            enrichment.parse_duration(123)  # Non-string input
        
        with self.assertRaises(TypeError):
            enrichment.parse_duration(None)  # None input
    
    def test_calculate_roi_valid_inputs(self):
        """Test ROI calculation with valid inputs."""
        roi = enrichment.calculate_roi(10000.0, 48)
        expected_roi = 10000.0 / 48
        self.assertAlmostEqual(roi, expected_roi, places=2)
    
    def test_calculate_roi_zero_duration(self):
        """Test ROI calculation with zero duration."""
        with self.assertRaises(ValueError):
            enrichment.calculate_roi(10000.0, 0)
    
    def test_calculate_roi_negative_duration(self):
        """Test ROI calculation with negative duration."""
        with self.assertRaises(ValueError):
            enrichment.calculate_roi(10000.0, -10)
    
    def test_calculate_roi_invalid_types(self):
        """Test ROI calculation with invalid input types."""
        with self.assertRaises(TypeError):
            enrichment.calculate_roi("10000", 48)  # String prize value
        
        with self.assertRaises(TypeError):
            enrichment.calculate_roi(10000.0, "48")  # String duration
    
    def test_detect_deadline_iso_format(self):
        """Test deadline detection and conversion to ISO format."""
        # TODO: Implement when detect_deadline() function is completed
        # deadline_text = "Register by December 31st, 2024 at midnight"
        # deadline = enrichment.detect_deadline(deadline_text)
        # self.assertIsNotNone(deadline)
        # self.assertTrue(deadline.endswith("Z"))  # ISO format with Z
        pass
    
    def test_detect_deadline_no_deadline(self):
        """Test deadline detection when no deadline is mentioned."""
        # TODO: Implement when detect_deadline() function is completed
        # deadline = enrichment.detect_deadline("Hackathon announcement without deadline")
        # self.assertIsNone(deadline)
        pass
    
    def test_detect_deadline_invalid_input(self):
        """Test deadline detection with invalid input types."""
        with self.assertRaises(TypeError):
            enrichment.detect_deadline(123)  # Non-string input
        
        with self.assertRaises(TypeError):
            enrichment.detect_deadline(None)  # None input
    
    def test_enrich_event_complete_data(self):
        """Test event enrichment with complete tweet data."""
        # TODO: Implement when enrich_event() function is completed
        # sample_tweet = {
        #     "tweet_id": "1234567890",
        #     "text": "AI Hackathon this weekend! €10k prize pool, 48-hour sprint. Register by Friday!",
        #     "score": 0.85
        # }
        # 
        # enriched = enrichment.enrich_event(sample_tweet)
        # 
        # # Check required fields
        # required_fields = ["tweet_id", "prize_value", "duration_hours", "roi_score", "currency_detected"]
        # for field in required_fields:
        #     self.assertIn(field, enriched)
        # 
        # # Validate data types and values
        # self.assertEqual(enriched["tweet_id"], "1234567890")
        # self.assertGreater(enriched["prize_value"], 0)
        # self.assertGreater(enriched["duration_hours"], 0)
        # self.assertGreater(enriched["roi_score"], 0)
        pass
    
    def test_enrich_event_missing_data(self):
        """Test event enrichment with incomplete tweet data."""
        # TODO: Implement when enrich_event() function is completed
        # incomplete_tweet = {"tweet_id": "123", "text": "Just a tech announcement"}
        # 
        # with self.assertRaises(ValueError):
        #     enrichment.enrich_event(incomplete_tweet)
        pass
    
    def test_get_currency_conversion_rate_supported(self):
        """Test currency conversion for supported currencies."""
        usd_rate = enrichment._get_currency_conversion_rate("USD")
        self.assertIsInstance(usd_rate, float)
        self.assertGreater(usd_rate, 0)
        
        usd_base_rate = enrichment._get_currency_conversion_rate("USD", "USD")
        self.assertEqual(usd_base_rate, 1.0)  # USD to USD = 1.0
    
    def test_get_currency_conversion_rate_unsupported(self):
        """Test currency conversion for unsupported currencies."""
        with self.assertRaises(enrichment.CurrencyNotSupportedError):
            enrichment._get_currency_conversion_rate("XYZ")
    
    def test_parse_prize_patterns(self):
        """Test prize detection patterns."""
        patterns = enrichment._parse_prize_patterns()
        self.assertIsInstance(patterns, list)
        self.assertGreater(len(patterns), 0)
        
        # Check pattern structure
        for pattern, currency in patterns:
            self.assertIsInstance(pattern, str)
            self.assertIsInstance(currency, str)
    
    def test_parse_duration_patterns(self):
        """Test duration detection patterns."""
        patterns = enrichment._parse_duration_patterns()
        self.assertIsInstance(patterns, list)
        self.assertGreater(len(patterns), 0)
        
        # Check pattern structure
        for pattern, multiplier in patterns:
            self.assertIsInstance(pattern, str)
            self.assertIsInstance(multiplier, int)
            self.assertGreater(multiplier, 0)
    
    def test_validate_enrichment_data_valid(self):
        """Test validation of valid enrichment data."""
        valid_data = {
            "tweet_id": "1234567890",
            "prize_value": 10800.0,
            "duration_hours": 48,
            "roi_score": 225.0,
            "currency_detected": "USD"
        }
        
        result = enrichment.validate_enrichment_data(valid_data)
        self.assertTrue(result)
    
    def test_validate_enrichment_data_missing_fields(self):
        """Test validation of enrichment data with missing fields."""
        incomplete_data = {
            "tweet_id": "1234567890",
            "prize_value": 10000.0
            # Missing duration_hours and roi_score
        }
        
        result = enrichment.validate_enrichment_data(incomplete_data)
        self.assertFalse(result)
    
    def test_validate_enrichment_data_empty(self):
        """Test validation of empty enrichment data."""
        result = enrichment.validate_enrichment_data({})
        self.assertFalse(result)


class TestEnrichmentIntegration(unittest.TestCase):
    """Integration tests for enrichment module."""
    
    def test_full_enrichment_pipeline(self):
        """Test complete enrichment pipeline with realistic data."""
        # TODO: Implement when all enrichment functions are completed
        # text = "🚀 AI Hackathon this weekend! $10.8k prize pool, 48-hour sprint. Solo developers welcome! Register by Friday midnight."
        # 
        # # Test individual components
        # prize, currency = enrichment.extract_prize_amount(text)
        # duration = enrichment.parse_duration(text)
        # roi = enrichment.calculate_roi(prize, duration)
        # deadline = enrichment.detect_deadline(text)
        # 
        # # Verify results make sense
        # self.assertEqual(prize, 10800.0)
        # self.assertEqual(currency, "USD")
        # self.assertEqual(duration, 48)
        # self.assertAlmostEqual(roi, 225.0, places=1)
        # self.assertIsNotNone(deadline)
        pass


class TestCustomExceptions(unittest.TestCase):
    """Test custom exception classes."""
    
    def test_currency_not_supported_error(self):
        """Test CurrencyNotSupportedError exception."""
        with self.assertRaises(enrichment.CurrencyNotSupportedError):
            raise enrichment.CurrencyNotSupportedError("Currency XYZ not supported")
    
    def test_api_error(self):
        """Test APIError exception."""
        with self.assertRaises(enrichment.APIError):
            raise enrichment.APIError("External API unavailable")


if __name__ == '__main__':
    unittest.main() 