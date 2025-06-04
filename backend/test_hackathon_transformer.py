#!/usr/bin/env python3
"""Test script for hackathon transformer functionality."""

import json
import os
from typing import List, Dict, Any
from hackathon_transformer import (
    transform_tweet_to_hackathon,
    transform_tweets_batch,
    validate_hackathon_data,
    save_hackathons
)


def create_sample_tweets() -> List[Dict[str, Any]]:
    """Create sample scored tweet data for testing."""
    sample_tweets = [
        {
            "tweet_id": "1234567890",
            "score": 0.85,
            "account_followers": 15000,
            "keyword_matches": ["ai", "hackathon", "machine learning"],
            "follower_fit": 1,
            "expanded_url": "https://x.com/tech_user/status/1234567890",
            "source_file": "tweet_1234567890.json",
            "collected_at": "2024-01-15T10:30:00Z"
        },
        {
            "tweet_id": "1234567891",
            "score": 0.72,
            "account_followers": 8500,
            "keyword_matches": ["web3", "blockchain", "challenge", "defi"],
            "follower_fit": 1,
            "expanded_url": "https://x.com/crypto_dev/status/1234567891",
            "source_file": "tweet_1234567891.json",
            "collected_at": "2024-01-15T11:15:00Z"
        },
        {
            "tweet_id": "1234567892",
            "score": 0.93,
            "account_followers": 25000,
            "keyword_matches": ["cross-chain", "interoperability", "competition"],
            "follower_fit": 1,
            "expanded_url": "https://x.com/protocol_labs/status/1234567892",
            "source_file": "tweet_1234567892.json",
            "collected_at": "2024-01-15T12:00:00Z"
        },
        {
            "tweet_id": "1234567893",
            "score": 0.58,
            "account_followers": 3200,
            "keyword_matches": ["nft", "gaming", "gamefi"],
            "follower_fit": 1,
            "expanded_url": "https://x.com/game_dev/status/1234567893",
            "source_file": "tweet_1234567893.json",
            "collected_at": "2024-01-15T13:45:00Z"
        },
        {
            "tweet_id": "1234567894",
            "score": 0.67,
            "account_followers": 12000,
            "keyword_matches": ["infrastructure", "dao", "developer"],
            "follower_fit": 1,
            "expanded_url": "https://x.com/dev_tools/status/1234567894",
            "source_file": "tweet_1234567894.json",
            "collected_at": "2024-01-15T14:20:00Z"
        }
    ]
    return sample_tweets


def test_single_transformation():
    """Test transforming a single tweet to hackathon format."""
    print("🧪 Testing single tweet transformation...")
    
    sample_tweet = {
        "tweet_id": "test123",
        "score": 0.8,
        "account_followers": 12000,
        "keyword_matches": ["ai", "hackathon", "innovation"],
        "follower_fit": 1,
        "expanded_url": "https://x.com/test_user/status/test123"
    }
    
    hackathon = transform_tweet_to_hackathon(sample_tweet)
    
    print("✅ Transformation successful!")
    print(f"   Title: {hackathon['title']}")
    print(f"   Organizer: {hackathon['organizer']}")
    print(f"   Prize Pool: ${hackathon['prizePool']:,}")
    print(f"   Duration: {hackathon['duration']} days")
    print(f"   Relevance Score: {hackathon['relevanceScore']}")
    print(f"   Tags: {', '.join(hackathon['tags'])}")
    print(f"   Location: {hackathon['location']}")
    
    # Validate the result
    if validate_hackathon_data(hackathon):
        print("✅ Validation passed!")
    else:
        print("❌ Validation failed!")
        return False
    
    return True


def test_batch_transformation():
    """Test transforming multiple tweets to hackathon format."""
    print("\n🧪 Testing batch transformation...")
    
    sample_tweets = create_sample_tweets()
    hackathons = transform_tweets_batch(sample_tweets)
    
    print(f"✅ Batch transformation successful!")
    print(f"   Input: {len(sample_tweets)} tweets")
    print(f"   Output: {len(hackathons)} hackathons")
    
    # Check if all hackathons are valid
    valid_count = 0
    for i, hackathon in enumerate(hackathons):
        if validate_hackathon_data(hackathon):
            valid_count += 1
        else:
            print(f"❌ Hackathon {i} failed validation")
    
    print(f"✅ {valid_count}/{len(hackathons)} hackathons passed validation")
    
    # Show top 3 hackathons
    print("\n🏆 Top 3 hackathons:")
    for i, hackathon in enumerate(hackathons[:3]):
        print(f"   #{i+1}: {hackathon['title']} (Score: {hackathon['relevanceScore']})")
    
    return valid_count == len(hackathons)


def test_save_and_load():
    """Test saving and loading hackathon data."""
    print("\n🧪 Testing save and load functionality...")
    
    sample_tweets = create_sample_tweets()
    hackathons = transform_tweets_batch(sample_tweets)
    
    # Save to test file
    test_file = "data/enriched/test_hackathons.json"
    save_hackathons(hackathons, test_file)
    
    # Check if file was created and has correct structure
    if os.path.exists(test_file):
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'hackathons' in data and 'metadata' in data:
            print("✅ File saved with correct structure!")
            print(f"   Hackathons: {data['metadata']['count']}")
            print(f"   Last updated: {data['metadata']['last_updated']}")
            
            # Clean up test file
            os.remove(test_file)
            return True
        else:
            print("❌ File structure invalid!")
            return False
    else:
        print("❌ File was not created!")
        return False


def test_api_integration():
    """Test that the transformation integrates with the API structure."""
    print("\n🧪 Testing API integration...")
    
    sample_tweets = create_sample_tweets()
    hackathons = transform_tweets_batch(sample_tweets)
    
    # Test the structure that the API would return
    api_response = {
        "hackathons": hackathons,
        "metadata": {
            "count": len(hackathons),
            "returned_count": len(hackathons),
            "total_count": len(hackathons),
            "limit_applied": 50
        }
    }
    
    # Verify API response structure
    required_fields = ["hackathons", "metadata"]
    if all(field in api_response for field in required_fields):
        print("✅ API response structure is correct!")
        
        # Check that frontend interface fields are present
        frontend_fields = ["title", "organizer", "prizePool", "duration", "relevanceScore", "tags"]
        if hackathons:
            first_hackathon = hackathons[0]
            missing_fields = [field for field in frontend_fields if field not in first_hackathon]
            if not missing_fields:
                print("✅ All frontend interface fields are present!")
                return True
            else:
                print(f"❌ Missing frontend fields: {missing_fields}")
                return False
        else:
            print("❌ No hackathons in response!")
            return False
    else:
        print("❌ API response structure is incorrect!")
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("🚀 Starting hackathon transformer tests...\n")
    
    tests = [
        ("Single Transformation", test_single_transformation),
        ("Batch Transformation", test_batch_transformation),
        ("Save and Load", test_save_and_load),
        ("API Integration", test_api_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Hackathon transformer is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs("data/enriched", exist_ok=True)
    
    success = run_all_tests()
    exit(0 if success else 1) 