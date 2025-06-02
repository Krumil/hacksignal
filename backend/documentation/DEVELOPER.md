# Developer Documentation

## 🏗️ System Architecture

The Hackathon Monitor is designed as a modular pipeline system with clear separation of concerns:

```
[Ingestion] → [Scoring] → [Enrichment] → [Alerting]
     ↓             ↓           ↓            ↓
  Raw Tweets   Relevance   Prize/ROI    Notifications
             Scores      Analysis     & Digests
```

### Core Modules

1. **`ingestion.py`** - Platform integration and data collection
2. **`scoring.py`** - Relevance scoring engine (focus of this document)
3. **`enrichment.py`** - Prize extraction and ROI calculation
4. **`alert.py`** - Alert delivery and digest management

## 🎯 Scoring Algorithm Deep Dive

### Overview

The scoring system converts raw tweet objects into numeric relevance scores (0.0 to 1.0) that represent how well a hackathon matches our "indie-friendly" criteria.

### Scoring Formula

```python
final_score = (follower_fit * 0.3) + (keyword_quality * 0.2) + (topic_confidence * 0.5)
```

**Weight Distribution Rationale:**

-   **Topic Confidence (50%)**: Primary filter - ensures content is actually about AI/crypto hackathons
-   **Follower Fit (30%)**: Secondary filter - ensures organizer size matches indie-friendly range
-   **Keyword Quality (20%)**: Tertiary boost - rewards high-quality, specific hackathon terminology

### Component Analysis

#### 1. Follower Fit (`check_follower_fit`)

-   **Purpose**: Binary validation of organizer account size
-   **Logic**: 1 if follower count ∈ [2K, 50K], else 0
-   **Rationale**: Too small = no reach, too large = corporate events

```python
follower_fit = 1 if 2000 <= followers <= 50000 else 0
```

#### 2. Topic Confidence (`assess_topic_confidence`)

-   **Purpose**: Measures AI/crypto relevance strength
-   **Logic**: Keyword density scoring for domain terms
-   **Output**: 0.0 to 1.0 confidence score

```python
ai_terms = ["ai", "machine learning", "neural", ...]
crypto_terms = ["crypto", "blockchain", "defi", ...]
confidence = min(max(ai_score, crypto_score) * 0.2, 1.0)
```

#### 3. Keyword Quality (`score_keywords_presence`)

-   **Purpose**: Weighted scoring based on keyword importance
-   **Logic**: Multi-tier weighting system with catalog integration
-   **Output**: 0.0 to ~10.0 (normalized to 0.0-0.2 in final score)

**Keyword Weight Hierarchy:**

-   **High Relevance Hashtags (2.0)**: `#AIHack`, `#CryptoHackathon`, `#DeFiHack`
-   **Catalog Keywords (1.6)**: `"blockchain hackathon"`, `"defi sprint"`
-   **Medium Relevance Hashtags (1.2)**: `#BuildOnEthereum`, `#AIChallenge`
-   **General Hackathon Terms (1.0)**: `"hackathon"`, `"bounty"`
-   **Weak Indicators (0.8)**: `"hack"`, `"challenge"`, `"sprint"`
-   **Contest Terms (0.6)**: `"contest"`
-   **Unknown Keywords (0.4)**: Fallback for unrecognized terms

### Keyword Extraction Strategy

The system uses a multi-source approach to identify relevant keywords:

1. **Catalog Keywords**: Pre-defined phrases from `sources/catalog.json`
2. **Hashtag Recognition**: Direct hashtag matching with relevance weighting
3. **Domain Indicators**: Common hackathon/competition terminology
4. **Pattern Matching**: Case-insensitive substring matching

```python
# Example keyword extraction flow
text = "AI Hackathon this weekend! $10.8k prize #AIHack"
keywords = ["AI", "hackathon", "#aihack"]
weighted_score = (0.4 + 1.0 + 2.0) = 3.4
normalized = min(3.4 * 0.02, 0.2) = 0.068
```

## 📊 Configuration System

### Threshold Management

All scoring thresholds are centralized in `config.json`:

```json
{
    "thresholds": {
        "follower_min": 2000, // Minimum organizer followers
        "follower_max": 50000, // Maximum organizer followers
        "relevance_threshold": 0.6 // Minimum score for alerting
    }
}
```

### Keyword Catalog Structure

The `sources/catalog.json` file defines weighted keyword sources:

```json
{
    "hashtags": [
        {
            "tag": "#AIHack",
            "relevance": "High", // High/Medium/Low → 2.0/1.2/0.8 weight
            "evidence": "Frequently used for AI hackathon announcements"
        }
    ],
    "keywords": [
        "blockchain hackathon", // All catalog keywords get 1.6 weight
        "defi sprint"
    ]
}
```

## 🧪 Testing Strategy

### Unit Test Categories

1. **Boundary Testing**: Follower count edge cases, score limits
2. **Input Validation**: Type checking, required field validation
3. **Keyword Matching**: Accuracy of extraction and weighting
4. **Integration**: End-to-end scoring pipeline validation

### Test Data Requirements

```python
# Comprehensive test tweet structure
sample_tweet = {
    "id": "1234567890",
    "text": "AI Hackathon this weekend! $10.8k prize pool #AIHack",
    "user": {
        "screen_name": "TechEvents",
        "followers_count": 15000
    },
    "created_at": "2024-12-01T10:00:00Z"
}
```

### Mock Strategy

-   **Configuration Mocking**: Use `unittest.mock.patch` for `_load_config()`
-   **File System Mocking**: Mock catalog.json loading for isolated tests
-   **API Response Mocking**: Mock tweet objects for consistent testing

## 🚀 Extension Guidelines

### Adding New Scoring Criteria

1. **Create New Component Function**:

    ```python
    def assess_new_criteria(tweet_data: Dict[str, Any]) -> float:
        """New scoring component with 0.0-1.0 output."""
        pass
    ```

2. **Update Main Formula**:

    ```python
    score = (follower_fit * 0.25) + (keyword_quality * 0.15) +
            (topic_confidence * 0.4) + (new_criteria * 0.2)
    ```

3. **Add Configuration**:
    ```json
    {
        "new_criteria": {
            "weight": 0.2,
            "thresholds": {...}
        }
    }
    ```

### Modifying Keyword Weights

1. **Update Catalog**: Modify `sources/catalog.json` relevance levels
2. **Adjust Weight Mapping**: Update `_build_keyword_weights()` function
3. **Test Impact**: Run integration tests to verify score distribution

### Performance Optimization

-   **Keyword Lookup**: Consider using sets instead of lists for O(1) lookups
-   **Catalog Caching**: Cache loaded catalog data to avoid repeated file I/O
-   **Regex Compilation**: Pre-compile regex patterns for complex matching

## 🔍 Debugging & Monitoring

### Score Analysis

To debug unexpected scores, trace through each component:

```python
# Debug scoring breakdown
tweet = {...}
follower_fit = check_follower_fit(tweet["user"]["followers_count"])
keywords = extract_keywords(tweet["text"])
keyword_score = score_keywords_presence(keywords)
topic_confidence = assess_topic_confidence(tweet["text"])

print(f"Follower Fit: {follower_fit} (weight: 0.3)")
print(f"Keywords: {keywords} → Score: {keyword_score} (normalized)")
print(f"Topic Confidence: {topic_confidence} (weight: 0.5)")
```

### Common Issues

1. **Low Scores Despite Relevant Content**:

    - Check follower count range
    - Verify keyword catalog loading
    - Examine topic confidence algorithm

2. **Inconsistent Keyword Matching**:

    - Case sensitivity issues
    - Missing catalog entries
    - Hashtag format mismatches

3. **Score Distribution Problems**:
    - Weight normalization issues
    - Threshold misconfiguration
    - Edge case handling

## 📚 Dependencies & Requirements

### Core Dependencies

-   **Python 3.8+**: Type hints and modern syntax
-   **json**: Configuration and catalog loading
-   **typing**: Type annotations for better code clarity

### Development Dependencies

-   **unittest**: Built-in testing framework
-   **unittest.mock**: Mocking for isolated tests
-   **pytest**: Alternative test runner (optional)

### File Structure Dependencies

```
/
├── config.json              # Central configuration
├── sources/catalog.json     # Keyword catalog
├── scoring.py              # This module
└── test_scoring.py         # Unit tests
```

## 🔄 Version History & Migration

### Current Version: 1.0

-   Implemented weighted keyword scoring
-   Added catalog-based relevance weighting
-   Integrated with main scoring pipeline

### Migration Notes

When updating the scoring algorithm:

1. **Backup Data**: Save current feedback data
2. **Test Compatibility**: Verify against existing test cases
3. **Threshold Adjustment**: May need to retune relevance thresholds
4. **Documentation**: Update this document with changes

---

_This documentation should be updated whenever significant changes are made to the scoring algorithm or system architecture._
