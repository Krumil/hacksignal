from fastapi import FastAPI, BackgroundTasks, HTTPException
from pathlib import Path
import json
import os
import sys
from typing import List, Dict, Any

# Ensure local modules are importable when running via `uvicorn backend.api:app`
CURRENT_DIR = Path(__file__).parent
sys.path.append(str(CURRENT_DIR))

# Lazy import internal pipeline modules to avoid heavy startup cost
from main import main as run_full_pipeline, run_quick_test  # noqa: E402
from scoring import save_scored_tweets  # noqa: F401, E402

app = FastAPI(
    title="HackSignal Backend API",
    description="Exposes endpoints to run the HackSignal tweet-processing pipeline and retrieve processed data.",
    version="0.1.0",
)

DATA_DIR = CURRENT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
ENRICHED_DIR = DATA_DIR / "enriched"
DEFAULT_SCORED_FILE = ENRICHED_DIR / "scored_tweets.json"
TOP_SCORED_FILE = ENRICHED_DIR / "top_scored_tweets.json"
HACKATHONS_FILE = ENRICHED_DIR / "hackathons.json"
TOP_HACKATHONS_FILE = ENRICHED_DIR / "top_hackathons.json"


@app.get("/health", tags=["Utility"])
def health() -> Dict[str, str]:
    """Health-check endpoint used by monitoring systems."""
    return {"status": "ok"}


@app.post("/pipeline/run", tags=["Pipeline"])
def run_pipeline(background_tasks: BackgroundTasks) -> Dict[str, str]:
    """Kick-off the full tweet-processing pipeline.

    The pipeline is executed in a background task so the request can return immediately.
    """
    background_tasks.add_task(run_full_pipeline)
    return {"message": "Pipeline started"}


@app.post("/pipeline/test", tags=["Pipeline"])
def quick_test() -> Dict[str, str]:
    """Synchronously run the quick test mode and return its success status."""
    success = run_quick_test()
    return {"success": success}


@app.get("/tweets/top", tags=["Tweets"])
def get_top_tweets(limit: int = 20) -> List[Dict[str, Any]]:
    """Return the top-scored tweets capped by *limit* (default 20)."""
    if not TOP_SCORED_FILE.exists():
        raise HTTPException(status_code=404, detail="Top-scored tweets file not found. Run the pipeline first.")
    with TOP_SCORED_FILE.open("r", encoding="utf-8") as f:
        tweets = json.load(f)
    return tweets[:limit]


@app.get("/tweets/scored", tags=["Tweets"])
def get_scored_tweets(limit: int = 100) -> List[Dict[str, Any]]:
    """Return scored tweets, ordered by score descending, up to *limit* (default 100)."""
    if not DEFAULT_SCORED_FILE.exists():
        raise HTTPException(status_code=404, detail="Scored tweets file not found. Run the pipeline first.")
    with DEFAULT_SCORED_FILE.open("r", encoding="utf-8") as f:
        tweets = json.load(f)
    return tweets[:limit]


@app.get("/tweets/raw", tags=["Tweets"])
def get_raw_tweets() -> List[Dict[str, Any]]:
    """Return the latest collected raw tweets (deduplicated)."""
    # Collect all JSON files inside data/raw (they are typically named by timestamp)
    raw_files = sorted(RAW_DIR.glob("*.json"), reverse=True)
    if not raw_files:
        raise HTTPException(status_code=404, detail="No raw tweet files found.")

    # Load the most recent raw file for simplicity
    with raw_files[0].open("r", encoding="utf-8") as f:
        tweets = json.load(f)
    return tweets


@app.get("/hackathons", tags=["Hackathons"])
def get_hackathons(limit: int = 50) -> Dict[str, Any]:
    """Return transformed hackathon data up to *limit* (default 50)."""
    if not HACKATHONS_FILE.exists():
        raise HTTPException(
            status_code=404, 
            detail="Hackathons file not found. Run the pipeline first to generate hackathon data."
        )
    
    try:
        with HACKATHONS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        hackathons = data.get('hackathons', [])
        metadata = data.get('metadata', {})
        
        # Apply limit
        limited_hackathons = hackathons[:limit]
        
        return {
            "hackathons": limited_hackathons,
            "metadata": {
                **metadata,
                "returned_count": len(limited_hackathons),
                "total_count": len(hackathons),
                "limit_applied": limit
            }
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid hackathons data file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading hackathons data: {str(e)}")


@app.get("/hackathons/top", tags=["Hackathons"])
def get_top_hackathons(limit: int = 20) -> List[Dict[str, Any]]:
    """Return the top hackathons (highest relevance scores) up to *limit* (default 20)."""
    # Always use the main hackathons file to get full dataset
    if not HACKATHONS_FILE.exists():
        raise HTTPException(
            status_code=404, 
            detail="Hackathons file not found. Run the pipeline first to generate hackathon data."
        )
    
    try:
        with HACKATHONS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        hackathons = data.get('hackathons', [])
        
        # Sort by relevance score and return top entries
        sorted_hackathons = sorted(hackathons, key=lambda x: x.get('relevanceScore', 0), reverse=True)
        return sorted_hackathons[:limit]
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid hackathons data file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading hackathons data: {str(e)}") 