#!/usr/bin/env python3
"""Main Orchestrator Program

Coordinates the entire tweet collection, scoring, and notification pipeline.
Calls functions from ingestion.py and scoring.py in sequence.
"""

import sys
import os
from datetime import datetime
import dotenv

# Fix encoding issues on Windows
if os.name == 'nt':  # Windows
    import codecs
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

dotenv.load_dotenv()    

# Add the current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion import poll_sources
from scoring import send_top_tweets_to_telegram, archive_previous_top_tweets_and_clear_raw_data, print_scoring_summary
from hackathon_transformer import process_raw_tweets_with_llm_scoring, save_hackathons


def safe_print(text):
    """Print text with Unicode emoji fallback for Windows compatibility."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback: replace emojis with ASCII equivalents
        fallback_text = text.replace("🚀", "[ROCKET]").replace("📁", "[FOLDER]").replace("🔍", "[SEARCH]").replace("⚠️", "[WARNING]").replace("✅", "[CHECK]").replace("🎯", "[TARGET]").replace("❌", "[X]").replace("💾", "[DISK]").replace("📊", "[CHART]").replace("📤", "[OUTBOX]").replace("🎉", "[PARTY]").replace("📈", "[GRAPH]").replace("⏹️", "[STOP]").replace("🧪", "[TEST]")
        print(fallback_text)


def main():
    """Main orchestrator function that runs the complete pipeline."""
    safe_print("🚀 Starting HackSignal Tweet Processing Pipeline")
    print("=" * 50)
    
    try:
        
        # Step 0: Archive previous top tweets and clear raw data
        safe_print("\n📁 Step 0: Archiving previous top tweets and clearing raw data...")
        archive_previous_top_tweets_and_clear_raw_data()
        
        # Step 1: Poll sources and collect tweets
        safe_print("\n🔍 Step 1: Collecting tweets from configured sources...")
        tweets = poll_sources()
        
        if not tweets:
            safe_print("⚠️  No tweets collected. Check your sources configuration or API limits.")
            return False
        
        safe_print(f"✅ Collected {len(tweets)} unique tweets and stored in data/raw/")
        
        # Step 2: Score the collected tweets
        safe_print("\n🎯 Step 2: Scoring tweets for relevance with LLM...")
        scored_tweets, hackathons = process_raw_tweets_with_llm_scoring()
        
        if not scored_tweets:
            safe_print("❌ No tweets were successfully scored.")
            return False
        
        safe_print(f"✅ Successfully scored {len(scored_tweets)} tweets with LLM")
        
        # Step 3: Save scored results
        safe_print("\n💾 Step 3: Saving scored results...")
        save_scored_tweets_with_llm(scored_tweets)
        save_hackathons(hackathons)
        
        # Save top 20 tweets separately
        top_tweets = scored_tweets[:20]
        top_hackathons = hackathons[:20]
        save_scored_tweets_with_llm(top_tweets, "data/enriched/top_scored_tweets.json")
        save_hackathons(top_hackathons, "data/enriched/top_hackathons.json")
        safe_print("✅ Scored tweets and hackathons saved to data/enriched/")
        
        # Step 4: Display summary
        safe_print("\n📊 Step 4: Generating summary...")
        print_scoring_summary(scored_tweets, top_n=10)
        
        # Step 5: Send to Telegram
        safe_print("\n📤 Step 5: Sending top tweets to Telegram...")
        send_top_tweets_to_telegram(scored_tweets)
        
        safe_print("\n🎉 Pipeline completed successfully!")
        safe_print(f"📈 Final Stats:")
        print(f"   • Tweets collected: {len(tweets)}")
        print(f"   • Tweets scored: {len(scored_tweets)}")
        print(f"   • Top score: {scored_tweets[0]['score']:.3f}" if scored_tweets else "   • No scores available")
        print(f"   • Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except KeyboardInterrupt:
        safe_print("\n⏹️  Pipeline interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {e}")
        print("Check the logs above for more details.")
        return False


def run_quick_test():
    """Run a quick test to verify the pipeline works with minimal data."""
    safe_print("🧪 Running Quick Test Mode")
    print("=" * 30)
    
    try:
        # Just test authentication and scoring existing data
        print("\n1. Testing LLM scoring on existing data...")
        scored_tweets, hackathons = process_raw_tweets_with_llm_scoring()
        
        if scored_tweets:
            safe_print(f"✅ LLM scoring works! Found {len(scored_tweets)} scored tweets")
            print(f"   Top score: {scored_tweets[0]['score']:.3f}")
            print(f"   Generated {len(hackathons)} hackathon entries")
            return True
        else:
            safe_print("⚠️  No existing tweets to score. Run full pipeline first.")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def save_scored_tweets_with_llm(scored_tweets, output_file: str = "data/enriched/scored_tweets.json"):
    """Save scored tweets from LLM processing to output file."""
    import os
    import json
    from datetime import datetime
    
    # Get project root
    from scoring import _find_project_root
    script_dir = _find_project_root()
    
    # If output_file is relative, make it relative to the script directory
    if not os.path.isabs(output_file):
        output_file = os.path.join(script_dir, output_file)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(scored_tweets, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(scored_tweets)} scored tweets to {output_file}")


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