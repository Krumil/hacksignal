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
    
    assert validate_hackathon_data(hackathon)


def test_batch_transformation():
    """Test transforming multiple tweets to hackathon format."""
    print("\n🧪 Testing batch transformation...")
    
    sample_tweets = create_sample_tweets()
    hackathons = transform_tweets_batch(sample_tweets)
    
    print(f"✅ Batch transformation successful!")
    print(f"   Input: {len(sample_tweets)} tweets")
    print(f"   Output: {len(hackathons)} hackathons")
    
    # Check if all hackathons are valid
    valid_count = sum(1 for h in hackathons if validate_hackathon_data(h))
    print(f"✅ {valid_count}/{len(hackathons)} hackathons passed validation")
    
    # Show top 3 hackathons
    print("\n🏆 Top 3 hackathons:")
    for i, hackathon in enumerate(hackathons[:3]):
        print(f"   #{i+1}: {hackathon['title']} (Score: {hackathon['relevanceScore']})")
    
    assert valid_count == len(hackathons)


def test_save_and_load():
    """Test saving and loading hackathon data."""
    print("\n🧪 Testing save and load functionality...")
    
    sample_tweets = create_sample_tweets()
    hackathons = transform_tweets_batch(sample_tweets)
    
    # Save to test file
    test_file = "data/enriched/test_hackathons.json"
    save_hackathons(hackathons, test_file)

    from scoring import _find_project_root
    project_root = _find_project_root()
    expected_path = os.path.join(project_root, test_file)

    # Check if file was created and has correct structure
    assert os.path.exists(expected_path)
    with open(expected_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert 'hackathons' in data and 'metadata' in data
    os.remove(expected_path)


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
        assert hackathons
        first_hackathon = hackathons[0]
        missing_fields = [field for field in frontend_fields if field not in first_hackathon]
        assert not missing_fields
    else:
        assert False, "API response structure is incorrect"

