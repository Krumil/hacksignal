"""End-to-End Demo & Validation

Executes full pipeline: ingestion → scoring → enrichment → alerting
Uses static fixture data for consistent output validation.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any

import ingestion
import scoring
import enrichment
import alert


def main() -> None:
    """Execute complete hackathon monitoring pipeline demo.
    
    Demonstrates:
    1. Data ingestion from fixture files
    2. Relevance scoring of tweets
    3. Event enrichment and ROI calculation
    4. Alert generation and delivery
    
    Expected to match demo_expected_output.txt for CI validation.
    """
    print("🚀 Hackathon Monitor - Demo Run")
    print("=" * 50)
    print(f"Started at: {datetime.now().isoformat()}")
    print()
    
    start_time = time.time()
    
    try:
        # Step 1: Load fixture data
        print("📥 Step 1: Loading fixture data...")
        tweets = load_fixture_tweets()
        print(f"   Loaded {len(tweets)} sample tweets")
        
        # Step 2: Score tweets for relevance
        print("🎯 Step 2: Scoring tweets for relevance...")
        scored_tweets = []
        for tweet in tweets:
            try:
                score_data = scoring.calculate_relevance_score(tweet)
                if score_data:
                    scored_tweets.append(score_data)
            except Exception as e:
                print(f"   Warning: Failed to score tweet {tweet.get('id', 'unknown')}: {e}")
        
        print(f"   Scored {len(scored_tweets)} tweets")
        
        # Step 3: Enrich high-scoring tweets
        print("💰 Step 3: Enriching events with prize and ROI data...")
        enriched_events = []
        relevance_threshold = get_relevance_threshold()
        
        for scored_tweet in scored_tweets:
            if scored_tweet.get('score', 0) >= relevance_threshold:
                try:
                    enriched = enrichment.enrich_event(scored_tweet)
                    if enriched:
                        enriched_events.append(enriched)
                except Exception as e:
                    print(f"   Warning: Failed to enrich tweet {scored_tweet.get('tweet_id', 'unknown')}: {e}")
        
        print(f"   Enriched {len(enriched_events)} events above threshold ({relevance_threshold})")
        
        # Step 4: Generate alerts
        print("🚨 Step 4: Generating alerts...")
        immediate_alerts = 0
        digest_queued = 0
        
        for event in enriched_events:
            roi_score = event.get('roi_score', 0)
            
            if alert.check_alert_threshold(roi_score):
                try:
                    if alert.send_immediate_alert(event):
                        immediate_alerts += 1
                except Exception as e:
                    print(f"   Warning: Failed to send immediate alert: {e}")
            else:
                try:
                    if alert.queue_for_digest(event):
                        digest_queued += 1
                except Exception as e:
                    print(f"   Warning: Failed to queue for digest: {e}")
        
        print(f"   Sent {immediate_alerts} immediate alerts")
        print(f"   Queued {digest_queued} events for daily digest")
        
        # Step 5: Show top results
        print("🏆 Step 5: Top Alert Summary")
        show_top_alert(enriched_events)
        
        # Step 6: Performance metrics
        processing_time = time.time() - start_time
        print("📊 Step 6: Performance Metrics")
        show_performance_metrics(tweets, scored_tweets, enriched_events, processing_time)
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        raise


def load_fixture_tweets() -> List[Dict[str, Any]]:
    """Load sample tweets from fixtures directory.
    
    Returns:
        List of fixture tweet objects
        
    Raises:
        FileNotFoundError: When fixture files are missing
    """
    try:
        with open('fixtures/sample_tweets.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Create minimal fixture data if file doesn't exist
        print("   Creating minimal fixture data...")
        return create_minimal_fixtures()


def create_minimal_fixtures() -> List[Dict[str, Any]]:
    """Create minimal fixture data for demo purposes.
    
    Returns:
        List of sample tweet objects
    """
    fixtures = [
        {
            "id": "1234567890",
            "text": "🚀 AI Hackathon this weekend! $10.8k prize pool, 48-hour sprint. Solo developers welcome! Register by Friday. #AIHack #IndieDevs",
            "user": {
                "screen_name": "TechEvents",
                "followers_count": 15000
            },
            "created_at": "2024-12-01T10:00:00Z"
        },
        {
            "id": "1234567891", 
            "text": "Crypto hackathon next month - $5000 prize, weekend format. Perfect for solo builders! #CryptoHackathon #SoloBuilders",
            "user": {
                "screen_name": "CryptoCompetitions",
                "followers_count": 8000
            },
            "created_at": "2024-12-01T11:00:00Z"
        },
        {
            "id": "1234567892",
            "text": "Major enterprise hackathon - $100k prize pool but requires teams of 10+. Probably not for indie developers.",
            "user": {
                "screen_name": "BigCorpEvents", 
                "followers_count": 150000
            },
            "created_at": "2024-12-01T12:00:00Z"
        }
    ]
    
    # Save fixtures for future runs
    try:
        with open('fixtures/sample_tweets.json', 'w') as f:
            json.dump(fixtures, f, indent=2)
    except Exception as e:
        print(f"   Warning: Could not save fixtures: {e}")
    
    return fixtures


def get_relevance_threshold() -> float:
    """Get relevance threshold from configuration.
    
    Returns:
        Relevance threshold value
    """
    try:
        config = ingestion.load_config()
        return config['thresholds']['relevance_threshold']
    except Exception:
        return 0.6  # Default threshold


def show_top_alert(events: List[Dict[str, Any]]) -> None:
    """Display details of the top ROI event.
    
    Args:
        events: List of enriched events
    """
    if not events:
        print("   No events to display")
        return
    
    # Sort by ROI score descending
    top_event = max(events, key=lambda x: x.get('roi_score', 0))
    
    print(f"   Top Event (ROI: {top_event.get('roi_score', 0):.2f} USD/hour)")
    print(f"   - Tweet: @{top_event.get('user', {}).get('screen_name', 'Unknown')}")
    print(f"   - Prize: {top_event.get('prize_value', 0)} {top_event.get('currency_detected', 'USD')}")
    print(f"   - Duration: {top_event.get('duration_hours', 0)} hours")
    if top_event.get('registration_deadline'):
        print(f"   - Deadline: {top_event.get('registration_deadline')}")


def show_performance_metrics(tweets: List[Dict[str, Any]], 
                           scored_tweets: List[Dict[str, Any]],
                           enriched_events: List[Dict[str, Any]], 
                           processing_time: float) -> None:
    """Display processing performance metrics.
    
    Args:
        tweets: Original tweet list
        scored_tweets: Scored tweet list  
        enriched_events: Enriched event list
        processing_time: Total processing time in seconds
    """
    total_tweets = len(tweets)
    scored_count = len(scored_tweets)
    enriched_count = len(enriched_events)
    
    print(f"   Processing time: {processing_time:.2f} seconds")
    print(f"   Tweets processed: {total_tweets}")
    print(f"   Tweets scored: {scored_count} ({(scored_count/total_tweets*100) if total_tweets > 0 else 0:.1f}%)")
    print(f"   Events enriched: {enriched_count} ({(enriched_count/scored_count*100) if scored_count > 0 else 0:.1f}%)")
    
    if enriched_events:
        roi_scores = [event.get('roi_score', 0) for event in enriched_events]
        avg_roi = sum(roi_scores) / len(roi_scores)
        max_roi = max(roi_scores)
        min_roi = min(roi_scores)
        
        print(f"   ROI Score - Avg: {avg_roi:.2f}, Max: {max_roi:.2f}, Min: {min_roi:.2f}")


if __name__ == "__main__":
    main() 