# Tweet Scoring System

This scoring system analyzes tweets from the `data/raw` folder and assigns relevance scores based on hackathon-related content, follower counts, and keyword matching.

## Quick Start

### Method 1: Using the Test Runner (Recommended)

```bash
python test_runner.py scoring
```

### Method 2: Direct Script Execution

```bash
python scoring.py
```

### Method 3: Direct Test File Execution

```bash
python test/test_scoring.py
```

## How the Scoring Works

The scoring algorithm evaluates tweets based on several factors:

### 1. Follower Fit (30% weight)

-   **1.0**: Account has 2,000-50,000 followers (target range)
-   **0.0**: Account outside the target range

### 2. Keyword Presence (up to 20% weight)

-   Detects hackathon-related keywords and hashtags
-   High-relevance terms: `#hackathon`, `#hack`, `#aihack` (2.0 points each)
-   Medium-relevance terms: `#challenge`, `#competition` (1.2 points each)
-   Basic terms: `hackathon`, `challenge`, `competition` (0.8-1.6 points each)

### 3. Topic Confidence (50% weight)

-   Analyzes AI/crypto topic relevance
-   AI terms: `ai`, `machine learning`, `neural`, `deep learning`
-   Crypto terms: `blockchain`, `bitcoin`, `ethereum`, `defi`, `web3`

### Final Score Formula

```
score = (follower_fit * 0.3) + (normalized_keyword_score) + (topic_confidence * 0.5)
```

## Output Files

### Main Output: `data/enriched/scored_tweets.json`

Contains all scored tweets with:

-   `tweet_id`: Original tweet ID
-   `score`: Relevance score (0.0 to 1.0)
-   `account_followers`: Follower count
-   `keyword_matches`: List of matched keywords
-   `follower_fit`: Binary follower range fit (0 or 1)
-   `source_file`: Original filename
-   `collected_at`: Collection timestamp
-   `expanded_url`: Direct URL to the tweet or linked content

### Top Tweets: `data/enriched/top_scored_tweets.json`

Contains the highest-scoring 20 tweets (by default).

## Command Line Options

### For Scoring Tweets:

```bash
python test_runner.py scoring              # Score tweets from data/raw (recommended)
python test/test_scoring.py                # Direct execution
python scoring.py                          # Alternative direct execution
```

### For Running Unit Tests:

```bash
python -m pytest test/test_scoring.py -v   # Run unit tests with pytest
python -m unittest test.test_scoring       # Run unit tests with unittest
```

### Test Runner Integration:

```bash
python test_runner.py scoring              # Score tweets
python test_runner.py ingestion            # Run ingestion tests
python test_runner.py all                  # Run all available tests
python test_runner.py --help               # Show available tests
```

## Example Output

```
🧪 Running Score tweets from raw data folder
📁 File: test/test_scoring.py
==================================================
🚀 Starting tweet scoring process...
Found 59 tweet files to process...
Successfully scored 59 tweets

=== SCORING SUMMARY ===
Total tweets scored: 59
Average score: 0.156
Highest score: 0.552
Lowest score: 0.000

Score Distribution:
  High relevance (≥0.8): 0 tweets
  Medium relevance (0.5-0.8): 1 tweets
  Low relevance (<0.5): 58 tweets

=== TOP 10 TWEETS ===

#1 (Score: 0.552)
URL: https://x.com/draper_u/status/1927948266592948285
Followers: 14,627
Keywords: hackathon, hack, challenge
Text: 🔊☀ @draper_u x @superai_conf Global Hackathon • 17-19 June powered by...

✅ scoring tests passed!
```

## Configuration Files

### `config.json` - Scoring Thresholds

```json
{
    "thresholds": {
        "follower_min": 2000,
        "follower_max": 50000,
        "relevance_threshold": 0.6
    }
}
```

### `sources/catalog.json` - Keywords and Hashtags

Contains:

-   `keywords`: List of hackathon-related terms
-   `hashtags`: List with relevance weights (High/Medium/Low)

## Data Structure

### Input: Tweet JSON Files

Located in `data/raw/tweet_*.json`, each containing:

```json
{
    "collected_at": "2025-05-30T12:20:01.422829",
    "tweet_data": {
        "id": "1927954147200094284",
        "text": "Tweet content...",
        "user": {
            "screen_name": "username",
            "followers_count": 30672
        },
        "created_at": "Thu May 29 05:04:23 +0000 2025"
    }
}
```

## Score Interpretation

-   **0.8-1.0**: High relevance - Strong hackathon signals
-   **0.5-0.8**: Medium relevance - Some relevant content
-   **0.0-0.5**: Low relevance - Minimal or no relevant content

## Integration with Other Modules

The scoring system can be imported and used programmatically:

```python
from scoring import score_tweets_from_raw_data, calculate_relevance_score

# Score all tweets from raw data
scored_tweets = score_tweets_from_raw_data()

# Score individual tweet
tweet_data = {...}  # Your tweet object
score = calculate_relevance_score(tweet_data)
```

## Testing

The system includes comprehensive unit tests that verify:

-   Follower count validation
-   Keyword extraction accuracy
-   Topic confidence assessment
-   Score calculation structure
-   Integration workflows

Unit tests can be run separately with:

```bash
python -m pytest test/test_scoring.py -v
python -m unittest test.test_scoring
```

## Error Handling

The system gracefully handles:

-   Missing or corrupted JSON files
-   Invalid tweet structures
-   Missing configuration files (uses fallback values)
-   Network or file system errors

## Dependencies

-   Python 3.6+
-   Standard library only (json, os, glob, argparse, unittest)
