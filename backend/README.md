# Hackathon Monitor - Backend

This is the Python backend implementation of the Hackathon Monitor system.

## 🎯 Overview

A lightweight system that monitors X (formerly Twitter) to surface AI and crypto-focused hackathons matching an "indie-friendly" profile.

## 🚀 Quick Start

### Prerequisites

-   Python 3.8+
-   X (Twitter) API credentials (for real monitoring)

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

3. Run the demo:

```bash
python demo_run.py
```

### Environment Variables

For real X monitoring, set these environment variables:

```bash
export X_API_KEY="your_api_key"
export X_API_SECRET="your_api_secret"
export X_BEARER_TOKEN="your_bearer_token"
```

## 📊 API Endpoints

The backend can be run as a service via `main.py` which provides:

-   Tweet ingestion and monitoring
-   Relevance scoring
-   Prize/duration enrichment
-   Alert generation

## 🧪 Testing

Run the test suite:

```bash
python -m pytest
```

## 📁 Structure

-   `ingestion.py` - X API integration for tweet monitoring
-   `scoring.py` - Relevance scoring engine
-   `enrichment.py` - Prize/duration extraction
-   `alert.py` - Alert delivery system
-   `main.py` - Main entry point
-   `data/` - Data storage (raw, enriched, feedback)
-   `sources/` - Monitoring configuration

For detailed documentation, see:

-   [SCORING_README.md](SCORING_README.md) - Scoring algorithm details
-   [Policy.md](Policy.md) - Data retention and privacy policies
