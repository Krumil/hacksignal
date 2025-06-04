# Hackathon Monitor - Backend

This is the Python backend implementation of the Hackathon Monitor system.

## 🎯 Overview

A lightweight system that monitors X (formerly Twitter) to surface AI and crypto-focused hackathons matching an "indie-friendly" profile.

## 🚀 Quick Start

### Prerequisites

-   Python 3.8+
-   X (Twitter) API credentials (for real monitoring)
-   OpenAI API key (for structured hackathon data generation)

### Installation

1. Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

2. Set up configuration:

```bash
# Copy and edit config file if needed
cp config.json config.local.json
```

3. Set up environment variables:

```bash
# For X monitoring
export X_API_KEY="your_api_key"
export X_API_SECRET="your_api_secret"
export X_BEARER_TOKEN="your_bearer_token"

# For structured hackathon generation
export OPENAI_API_KEY="your_openai_api_key"
```

4. Run the demo:

```bash
python demo_run.py
```

## 🤖 Structured Outputs Implementation

The system now uses **OpenAI's Structured Outputs** for generating high-quality hackathon data from tweets. This provides:

-   **Single LLM call** generates complete hackathon objects
-   **Guaranteed JSON schema** compliance via Pydantic models
-   **50% reduction** in API calls and costs
-   **Enhanced data quality** with better field coherence
-   **Automatic fallback** to rule-based generation if needed

### Key Features

-   **Structured Generation**: Complete hackathon data (title, organizer, prize pool, etc.) in one API call
-   **Type Safety**: Pydantic models ensure data validation
-   **Reasoning Field**: LLM explains its decisions for transparency
-   **Robust Fallback**: Graceful degradation if API unavailable

For detailed documentation, see [STRUCTURED_OUTPUTS_README.md](STRUCTURED_OUTPUTS_README.md).

## 📊 API Endpoints

The backend can be run as a service via `main.py` which provides:

-   Tweet ingestion and monitoring
-   Relevance scoring
-   Structured hackathon data generation
-   Prize/duration enrichment
-   Alert generation

## 🧪 Testing

### Run Standard Test Suite

```bash
python -m pytest
```

### Test Structured Outputs Implementation

Test the new structured outputs hackathon transformer:

```bash
python test_structured_transformer.py
```

This test script validates:

-   Individual tweet transformation using structured outputs
-   Batch processing of multiple tweets
-   File saving/loading functionality
-   Data validation and fallback scenarios
-   API integration with OpenAI structured outputs

**Note**: Set `OPENAI_API_KEY` environment variable to test structured outputs, or tests will use fallback generation.

## 📁 Structure

-   `ingestion.py` - X API integration for tweet monitoring
-   `scoring.py` - Relevance scoring engine
-   `hackathon_transformer.py` - **NEW**: Structured LLM-based hackathon generation
-   `enrichment.py` - Prize/duration extraction
-   `alert.py` - Alert delivery system
-   `main.py` - Main entry point
-   `test_structured_transformer.py` - **NEW**: Test suite for structured outputs
-   `data/` - Data storage (raw, enriched, feedback)
-   `sources/` - Monitoring configuration

For detailed documentation, see:

-   [STRUCTURED_OUTPUTS_README.md](STRUCTURED_OUTPUTS_README.md) - **NEW**: Structured outputs implementation
-   [SCORING_README.md](SCORING_README.md) - Scoring algorithm details
-   [Policy.md](Policy.md) - Data retention and privacy policies
