"""Test script for the new structured output hackathon transformer.

This script tests the new single LLM call approach with structured outputs.
"""

import json
import os
from hackathon_transformer import transform_tweet_to_hackathon, validate_hackathon_data

# Sample tweet data for testing
SAMPLE_TWEETS = [
    {
        'tweet_id': '12345',
        'text': 'Join our AI hackathon this weekend! Build the future of machine learning. $50k in prizes! #AI #MachineLearning #Innovation',
        'score': 0.85,
        'account_followers': 15000,
        'keyword_matches': ['AI', 'MachineLearning', 'Innovation'],
        'expanded_url': 'https://example.com/ai-hackathon'
    },
    {
        'tweet_id': '67890',
        'text': 'Web3 builders unite! Create the next generation of decentralized apps. Open to all developers worldwide. #Web3 #DeFi #Blockchain',
        'score': 0.72,
        'account_followers': 8000,
        'keyword_matches': ['Web3', 'DeFi', 'Blockchain'],
        'expanded_url': 'https://example.com/web3-challenge'
    },
    {
        'tweet_id': '11111',
        'text': 'Small startup competition for cross-chain infrastructure tools. Remote participation welcome.',
        'score': 0.45,
        'account_followers': 1200,
        'keyword_matches': ['cross-chain', 'infrastructure'],
        'expanded_url': 'https://example.com/startup-challenge'
    }
]


def test_structured_transformer():
    """Test the structured output transformer with sample data."""
    print("Testing Structured Output Hackathon Transformer")
    print("=" * 50)
    
    # Test each sample tweet
    for i, tweet_data in enumerate(SAMPLE_TWEETS, 1):
        print(f"\nTest {i}: Processing tweet {tweet_data['tweet_id']}")
        print(f"Tweet: {tweet_data['text'][:80]}...")
        
        try:
            # Transform tweet to hackathon
            hackathon = transform_tweet_to_hackathon(tweet_data)
            
            # Validate the result
            is_valid = validate_hackathon_data(hackathon)
            
            print(f"✅ Successfully generated hackathon data (Valid: {is_valid})")
            print(f"   Title: {hackathon['title']}")
            print(f"   Organizer: {hackathon['organizer']}")
            print(f"   Prize Pool: ${hackathon['prizePool']:,}")
            print(f"   Duration: {hackathon['duration']} days")
            print(f"   Relevance Score: {hackathon['relevanceScore']}")
            print(f"   Tags: {', '.join(hackathon['tags'])}")
            print(f"   Location: {hackathon['location']}")
            
            if 'reasoning' in hackathon:
                print(f"   Reasoning: {hackathon['reasoning'][:100]}...")
            
        except Exception as e:
            print(f"❌ Error processing tweet: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")


def test_batch_processing():
    """Test batch processing of multiple tweets."""
    print("\nTesting Batch Processing")
    print("=" * 30)
    
    try:
        from hackathon_transformer import transform_tweets_batch
        
        # Process all sample tweets at once
        hackathons = transform_tweets_batch(SAMPLE_TWEETS)
        
        print(f"✅ Successfully processed {len(hackathons)} hackathons")
        print(f"   Sorted by relevance score (highest first)")
        
        for i, hackathon in enumerate(hackathons, 1):
            print(f"   {i}. {hackathon['title']} (Score: {hackathon['relevanceScore']})")
        
    except Exception as e:
        print(f"❌ Error in batch processing: {e}")


def test_save_functionality():
    """Test saving hackathons to file."""
    print("\nTesting Save Functionality")
    print("=" * 30)
    
    try:
        from hackathon_transformer import transform_tweets_batch, save_hackathons
        
        # Generate hackathons
        hackathons = transform_tweets_batch(SAMPLE_TWEETS)
        
        # Save to test file
        test_output_file = "data/enriched/test_hackathons.json"
        save_hackathons(hackathons, test_output_file)
        
        print(f"✅ Successfully saved hackathons to {test_output_file}")
        
        # Verify file was created and has correct structure
        if os.path.exists(test_output_file):
            with open(test_output_file, 'r') as f:
                data = json.load(f)
                print(f"   File contains {data['metadata']['count']} hackathons")
                print(f"   Version: {data['metadata']['version']}")
        
    except Exception as e:
        print(f"❌ Error in save functionality: {e}")


if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY not set. Tests will use fallback generation.")
        print("   Set OPENAI_API_KEY environment variable to test structured outputs.\n")
    
    # Run all tests
    test_structured_transformer()
    test_batch_processing()
    test_save_functionality()
    
    print("\n🎉 All tests completed!") 