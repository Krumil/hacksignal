#!/usr/bin/env python3
"""Test Pipeline Compatibility

Tests the complete data flow from ingestion to hackathon transformation
to ensure compatibility after Twitter API changes.
"""

import json
import sys
import os
from typing import Dict, Any

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion import _transform_tweet_format
from hackathon_transformer import transform_tweet_to_hackathon, validate_hackathon_data


def _twitter_api_compatibility():
    """Test that new Twitter API response transforms correctly."""
    
    # Sample response from new Twitter API (twitter-api45.p.rapidapi.com)
    sample_api_tweet = {
        "type": "tweet",
        "tweet_id": "1703108627035254988",
        "screen_name": "hackathon_labs",
        "bookmarks": 15,
        "favorites": 241,
        "created_at": "Sat Sep 16 18:08:33 +0000 2023",
        "text": "🚀 Join our AI Builder Summit! Build innovative AI solutions. Prize pool: $50K. Register now: https://hackathon.example.com #AI #hackathon #innovation",
        "lang": "en",
        "quotes": 14,
        "replies": 42,
        "retweets": 19,
        "media": {
            "photo": [
                {
                    "media_url_https": "https://pbs.twimg.com/media/example.jpg"
                }
            ]
        }
    }
    
    print("1. Testing Twitter API response transformation...")
    
    # Transform using updated function
    transformed_tweet = _transform_tweet_format(sample_api_tweet)
    
    # Check required fields for hackathon transformer
    required_fields = ['id', 'text', 'user', 'expanded_url']
    for field in required_fields:
        assert field in transformed_tweet, f"Missing field: {field}"
        
    print(f"✓ Transformed tweet ID: {transformed_tweet['id']}")
    print(f"✓ Extracted URL: {transformed_tweet['expanded_url']}")
    print(f"✓ Estimated followers: {transformed_tweet['user']['followers_count']}")
    
    return transformed_tweet


def _scoring_compatibility(transformed_tweet):
    """Test that the transformed tweet works with scoring pipeline."""
    
    print("\n2. Testing scoring pipeline compatibility...")
    
    # Simulate scored tweet data (what scoring.py would produce)
    scored_tweet = {
        'tweet_id': transformed_tweet['id'],
        'text': transformed_tweet['text'],
        'score': 0.85,  # High relevance score
        'account_followers': transformed_tweet['user']['followers_count'],
        'keyword_matches': ['AI', 'hackathon', 'innovation', 'builder'],
        'expanded_url': transformed_tweet['expanded_url'],
        'created_at': transformed_tweet['created_at'],
        'favorites': transformed_tweet['favorite_count'],
        'retweets': transformed_tweet['retweet_count']
    }
    
    print(f"✓ Score: {scored_tweet['score']}")
    print(f"✓ Keywords: {scored_tweet['keyword_matches']}")
    print(f"✓ Followers: {scored_tweet['account_followers']}")
    
    return scored_tweet


def _hackathon_transformation(scored_tweet):
    """Test hackathon transformation and frontend compatibility."""
    
    print("\n3. Testing hackathon transformation...")
    
    # Transform to hackathon format
    hackathon = transform_tweet_to_hackathon(scored_tweet)
    
    # Validate hackathon data structure
    is_valid = validate_hackathon_data(hackathon)
    assert is_valid, "Hackathon data validation failed"
    
    print(f"✓ Title: {hackathon['title']}")
    print(f"✓ Organizer: {hackathon['organizer']}")
    print(f"✓ Prize Pool: ${hackathon['prizePool']:,}")
    print(f"✓ Duration: {hackathon['duration']} days")
    print(f"✓ Relevance: {hackathon['relevanceScore']}%")
    print(f"✓ Tags: {hackathon['tags']}")
    print(f"✓ Registration URL: {hackathon['registrationUrl']}")
    
    return hackathon


def _frontend_compatibility(hackathon):
    """Test that hackathon data matches frontend interface."""
    
    print("\n4. Testing frontend interface compatibility...")
    
    # Required fields from HackathonCardProps interface
    required_props = [
        'title', 'organizer', 'prizePool', 'duration', 
        'relevanceScore', 'tags'
    ]
    
    # Optional fields
    optional_props = [
        'id', 'description', 'deadline', 'registrationUrl', 
        'website', 'location', 'sourceScore', 'sourceFollowers', 
        'sourceKeywords', 'lastUpdated'
    ]
    
    # Check required fields
    for prop in required_props:
        assert prop in hackathon, f"Missing required prop: {prop}"
        assert hackathon[prop] is not None, f"Required prop is None: {prop}"
    
    # Check optional fields are present (they should all be there)
    for prop in optional_props:
        if prop in hackathon:
            print(f"✓ Optional prop present: {prop}")
    
    # Type checks
    assert isinstance(hackathon['prizePool'], int), "prizePool must be integer"
    assert isinstance(hackathon['duration'], int), "duration must be integer"
    assert isinstance(hackathon['relevanceScore'], int), "relevanceScore must be integer"
    assert isinstance(hackathon['tags'], list), "tags must be list"
    assert 0 <= hackathon['relevanceScore'] <= 100, "relevanceScore must be 0-100"
    
    print("✓ All frontend interface requirements met")
    
    return True


def test_pipeline_compatibility():
    """Run the full pipeline and assert compatibility."""
    transformed = _twitter_api_compatibility()
    scored = _scoring_compatibility(transformed)
    hackathon = _hackathon_transformation(scored)
    assert _frontend_compatibility(hackathon)

