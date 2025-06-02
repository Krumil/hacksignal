"""Threshold Optimization CLI Tool

Reads user feedback from /data/feedback/feedback.csv,
calculates precision/recall metrics, and suggests new threshold constants.
"""

import csv
import json
import argparse
from typing import Dict, List, Any, Tuple
from pathlib import Path


def main() -> None:
    """Main CLI entry point for threshold tuning."""
    parser = argparse.ArgumentParser(description='Hackathon Monitor - Threshold Optimization')
    parser.add_argument('--analyze-feedback', action='store_true',
                       help='Analyze feedback data and show metrics')
    parser.add_argument('--suggest-thresholds', action='store_true', 
                       help='Suggest new threshold values based on feedback')
    parser.add_argument('--feedback-file', default='data/feedback/feedback.csv',
                       help='Path to feedback CSV file')
    parser.add_argument('--output-config', action='store_true',
                       help='Output suggested config.json with new thresholds')
    
    args = parser.parse_args()
    
    if not any([args.analyze_feedback, args.suggest_thresholds]):
        parser.print_help()
        return
    
    print("🔧 Hackathon Monitor - Threshold Optimization")
    print("=" * 50)
    
    try:
        # Load feedback data
        feedback_data = load_feedback_data(args.feedback_file)
        print(f"📊 Loaded {len(feedback_data)} feedback entries")
        
        if args.analyze_feedback:
            analyze_feedback(feedback_data)
        
        if args.suggest_thresholds:
            suggestions = suggest_new_thresholds(feedback_data)
            display_threshold_suggestions(suggestions)
            
            if args.output_config:
                update_config_with_suggestions(suggestions)
                print("\n✅ Updated config.json with suggested thresholds")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("💡 Tip: Create feedback data by running the demo or real monitoring")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise


def load_feedback_data(feedback_file: str) -> List[Dict[str, Any]]:
    """Load user feedback from CSV file.
    
    Args:
        feedback_file: Path to feedback CSV file
        
    Returns:
        List of feedback entries with categories and metadata
        
    Raises:
        FileNotFoundError: When feedback file doesn't exist
    """
    feedback_path = Path(feedback_file)
    
    if not feedback_path.exists():
        # Create sample feedback data for demonstration
        create_sample_feedback(feedback_file)
    
    feedback_data = []
    with open(feedback_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            feedback_data.append(row)
    
    return feedback_data


def create_sample_feedback(feedback_file: str) -> None:
    """Create sample feedback data for demonstration.
    
    Args:
        feedback_file: Path where to create sample feedback
    """
    feedback_path = Path(feedback_file)
    feedback_path.parent.mkdir(parents=True, exist_ok=True)
    
    sample_data = [
        {
            'tweet_id': '1234567890',
            'relevance_score': '0.85',
            'roi_score': '208.33',
            'prize_value': '10000',
            'duration_hours': '48',
            'follower_count': '15000',
            'feedback_category': 'useful',
            'user_comment': 'Perfect match for indie developer',
            'timestamp': '2024-12-01T10:00:00Z'
        },
        {
            'tweet_id': '1234567891',
            'relevance_score': '0.72',
            'roi_score': '104.17',
            'prize_value': '5000',
            'duration_hours': '48',
            'follower_count': '8000',
            'feedback_category': 'useful',
            'user_comment': 'Good opportunity for solo developers',
            'timestamp': '2024-12-01T11:00:00Z'
        },
        {
            'tweet_id': '1234567892',
            'relevance_score': '0.45',
            'roi_score': '1388.89',
            'prize_value': '100000',
            'duration_hours': '72',
            'follower_count': '150000',
            'feedback_category': 'too_big',
            'user_comment': 'Prize too large, likely requires large teams',
            'timestamp': '2024-12-01T12:00:00Z'
        },
        {
            'tweet_id': '1234567893',
            'relevance_score': '0.65',
            'roi_score': '27.78',
            'prize_value': '1000',
            'duration_hours': '36',
            'follower_count': '5000',
            'feedback_category': 'low_prize',
            'user_comment': 'Prize too small to be worth the effort',
            'timestamp': '2024-12-01T13:00:00Z'
        },
        {
            'tweet_id': '1234567894',
            'relevance_score': '0.80',
            'roi_score': '0',
            'prize_value': '0',
            'duration_hours': '0',
            'follower_count': '25000',
            'feedback_category': 'irrelevant',
            'user_comment': 'Not actually a hackathon, just conference announcement',
            'timestamp': '2024-12-01T14:00:00Z'
        }
    ]
    
    with open(feedback_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = sample_data[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_data)
    
    print(f"📝 Created sample feedback data at {feedback_file}")


def analyze_feedback(feedback_data: List[Dict[str, Any]]) -> None:
    """Analyze feedback data and display metrics.
    
    Args:
        feedback_data: List of feedback entries
    """
    print("\n📈 Feedback Analysis")
    print("-" * 30)
    
    # Categorize feedback
    categories = {}
    for entry in feedback_data:
        category = entry.get('feedback_category', 'unknown')
        categories[category] = categories.get(category, 0) + 1
    
    print("Feedback Categories:")
    for category, count in categories.items():
        percentage = (count / len(feedback_data)) * 100
        print(f"  {category}: {count} ({percentage:.1f}%)")
    
    # Calculate precision/recall metrics
    useful_count = categories.get('useful', 0)
    total_positive = useful_count + categories.get('too_big', 0) + categories.get('low_prize', 0)
    total_negative = categories.get('irrelevant', 0)
    
    precision = useful_count / max(total_positive, 1)
    recall = useful_count / max(useful_count + total_negative, 1)
    f1_score = 2 * (precision * recall) / max(precision + recall, 0.01)
    
    print(f"\nMetrics:")
    print(f"  Precision: {precision:.2f}")
    print(f"  Recall: {recall:.2f}")
    print(f"  F1 Score: {f1_score:.2f}")


def suggest_new_thresholds(feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate suggested threshold values based on feedback.
    
    Args:
        feedback_data: List of feedback entries
        
    Returns:
        Dictionary with suggested threshold values
    """
    useful_events = [entry for entry in feedback_data if entry.get('feedback_category') == 'useful']
    too_big_events = [entry for entry in feedback_data if entry.get('feedback_category') == 'too_big']
    low_prize_events = [entry for entry in feedback_data if entry.get('feedback_category') == 'low_prize']
    
    suggestions = {}
    
    if useful_events:
        # Analyze useful events for optimal ranges
        useful_scores = [float(entry.get('relevance_score', 0)) for entry in useful_events]
        useful_prizes = [float(entry.get('prize_value', 0)) for entry in useful_events]
        useful_durations = [int(entry.get('duration_hours', 0)) for entry in useful_events]
        useful_followers = [int(entry.get('follower_count', 0)) for entry in useful_events]
        
        # Suggest relevance threshold as 10th percentile of useful events
        if useful_scores:
            suggestions['relevance_threshold'] = max(0.5, min(useful_scores) - 0.1)
        
        # Suggest prize range based on useful events
        if useful_prizes:
            suggestions['prize_min_usd'] = max(1080, int(min(useful_prizes) * 0.8))
            suggestions['prize_max_usd'] = min(54000, int(max(useful_prizes) * 1.2))
    
    # Adjust based on negative feedback
    if too_big_events:
        too_big_prizes = [float(entry.get('prize_value', 0)) for entry in too_big_events if float(entry.get('prize_value', 0)) > 0]
        too_big_followers = [int(entry.get('follower_count', 0)) for entry in too_big_events]
        
        if too_big_prizes and 'prize_max_usd' in suggestions:
            suggestions['prize_max_usd'] = min(suggestions['prize_max_usd'], int(min(too_big_prizes) * 0.9))
        
        if too_big_followers:
            suggestions['follower_max'] = min(50000, min(too_big_followers) * 0.9)
    
    if low_prize_events:
        low_prizes = [float(entry.get('prize_value', 0)) for entry in low_prize_events if float(entry.get('prize_value', 0)) > 0]
        
        if low_prizes and 'prize_min_usd' in suggestions:
            suggestions['prize_min_usd'] = max(suggestions['prize_min_usd'], int(max(low_prizes) * 1.1))
    
    return suggestions


def display_threshold_suggestions(suggestions: Dict[str, Any]) -> None:
    """Display suggested threshold changes.
    
    Args:
        suggestions: Dictionary with suggested values
    """
    print("\n🎯 Threshold Suggestions")
    print("-" * 30)
    
    # Load current config
    try:
        with open('config.json', 'r') as f:
            current_config = json.load(f)
        current_thresholds = current_config.get('thresholds', {})
    except Exception:
        current_thresholds = {}
    
    if not suggestions:
        print("No threshold changes suggested based on current feedback.")
        return
    
    for key, suggested_value in suggestions.items():
        current_value = current_thresholds.get(key, 'not set')
        
        if isinstance(suggested_value, float):
            print(f"  {key}: {current_value} → {suggested_value:.2f}")
        else:
            print(f"  {key}: {current_value} → {suggested_value}")


def update_config_with_suggestions(suggestions: Dict[str, Any]) -> None:
    """Update config.json with suggested threshold values.
    
    Args:
        suggestions: Dictionary with suggested values
    """
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {"thresholds": {}}
    
    if 'thresholds' not in config:
        config['thresholds'] = {}
    
    # Update with suggestions
    for key, value in suggestions.items():
        config['thresholds'][key] = value
    
    # Write back to file
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)


if __name__ == "__main__":
    main() 