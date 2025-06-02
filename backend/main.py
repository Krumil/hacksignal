#!/usr/bin/env python3
"""Main Orchestrator Program

Coordinates the entire tweet collection, scoring, and notification pipeline.
Calls functions from ingestion.py and scoring.py in sequence.
"""

import sys
import os
from datetime import datetime
import dotenv

dotenv.load_dotenv()    

# Add the current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion import poll_sources
from scoring import score_tweets_from_raw_data, save_scored_tweets, print_scoring_summary, send_top_tweets_to_telegram, archive_previous_top_tweets_and_clear_raw_data


def main():
    """Main orchestrator function that runs the complete pipeline."""
    print("🚀 Starting HackSignal Tweet Processing Pipeline")
    print("=" * 50)
    
    try:
        
        # Step 0: Archive previous top tweets and clear raw data
        print("\n📁 Step 0: Archiving previous top tweets and clearing raw data...")
        archive_previous_top_tweets_and_clear_raw_data()
        
        # Step 1: Poll sources and collect tweets
        print("\n🔍 Step 1: Collecting tweets from configured sources...")
        tweets = poll_sources()
        
        if not tweets:
            print("⚠️  No tweets collected. Check your sources configuration or API limits.")
            return False
        
        print(f"✅ Collected {len(tweets)} unique tweets and stored in data/raw/")
        
        # Step 2: Score the collected tweets
        print("\n🎯 Step 2: Scoring tweets for relevance...")
        scored_tweets = score_tweets_from_raw_data()
        
        if not scored_tweets:
            print("❌ No tweets were successfully scored.")
            return False
        
        print(f"✅ Successfully scored {len(scored_tweets)} tweets")
        
        # Step 3: Save scored results
        print("\n💾 Step 3: Saving scored results...")
        save_scored_tweets(scored_tweets)
        
        # Save top 20 tweets separately
        top_tweets = scored_tweets[:20]
        save_scored_tweets(top_tweets, "data/enriched/top_scored_tweets.json")
        print("✅ Scored tweets saved to data/enriched/")
        
        # Step 4: Display summary
        print("\n📊 Step 4: Generating summary...")
        print_scoring_summary(scored_tweets, top_n=10)
        
        # Step 5: Send to Telegram
        print("\n📤 Step 5: Sending top tweets to Telegram...")
        send_top_tweets_to_telegram(scored_tweets)
        
        print("\n🎉 Pipeline completed successfully!")
        print(f"📈 Final Stats:")
        print(f"   • Tweets collected: {len(tweets)}")
        print(f"   • Tweets scored: {len(scored_tweets)}")
        print(f"   • Top score: {scored_tweets[0]['score']:.3f}" if scored_tweets else "   • No scores available")
        print(f"   • Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️  Pipeline interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {e}")
        print("Check the logs above for more details.")
        return False


def run_quick_test():
    """Run a quick test to verify the pipeline works with minimal data."""
    print("🧪 Running Quick Test Mode")
    print("=" * 30)
    
    try:
        # Just test authentication and scoring existing data
        print("\n1. Testing scoring on existing data...")
        scored_tweets = score_tweets_from_raw_data()
        
        if scored_tweets:
            print(f"✅ Scoring works! Found {len(scored_tweets)} scored tweets")
            print(f"   Top score: {scored_tweets[0]['score']:.3f}")
            return True
        else:
            print("⚠️  No existing tweets to score. Run full pipeline first.")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    print("HackSignal Tweet Processing Pipeline")
    print("Choose an option:")
    print("1. Run full pipeline (default)")
    print("2. Run quick test")
    
    # Check for command line argument
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        success = run_quick_test()
    else:
        success = main()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1) 