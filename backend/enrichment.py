"""Event Enrichment Engine

Extracts prize values with currency conversion to USD, parses event duration,
and calculates ROI scores for indie hackathon targeting.
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple


def extract_prize_amount(text: str) -> Tuple[float, str]:
    """Parse and convert prize values from text to USD.
    
    Args:
        text: Tweet text content to parse for prize information
        
    Returns:
        Tuple of (prize_value_in_usd, currency_detected)
        
    Raises:
        ValueError: When no prize amount is found in text
        TypeError: When text is not a string
    """
    if not isinstance(text, str):
        raise TypeError("Text must be a string")
    
    patterns = _parse_prize_patterns()
    for pattern, currency in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(",", "")
            amount = float(amount_str)
            # Handle "10k" style amounts
            if "k" in match.group(0).lower():
                amount *= 1000
            if currency != "USD":
                rate = _get_currency_conversion_rate(currency, "USD")
                amount *= rate
            return float(amount), currency

    raise ValueError("Prize amount not found")


def parse_duration(text: str) -> int:
    """Extract event duration from text in hours.
    
    Args:
        text: Text content containing duration information
        
    Returns:
        Duration in hours
        
    Raises:
        ValueError: When no valid duration is found
        TypeError: When text is not a string
    """
    if not isinstance(text, str):
        raise TypeError("Text must be a string")
    
    patterns = _parse_duration_patterns()
    for pattern, multiplier in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if match.groups():
                hours = int(match.group(1)) * multiplier
            else:
                hours = multiplier
            return hours

    raise ValueError("Duration not found")


def calculate_roi(prize_value: float, duration_hours: int) -> float:
    """Compute ROI score as prize_value ÷ duration_hours.
    
    Args:
        prize_value: Prize amount in USD
        duration_hours: Event duration in hours
        
    Returns:
        ROI score (USD per hour)
        
    Raises:
        ValueError: When duration_hours is zero or negative
        TypeError: When inputs are not numeric
    """
    if not isinstance(prize_value, (int, float)) or not isinstance(duration_hours, (int, float)):
        raise TypeError("Prize value and duration must be numeric")
    
    if duration_hours <= 0:
        raise ValueError("Duration must be positive")
    
    return prize_value / duration_hours


def detect_deadline(text: str) -> Optional[str]:
    """Find registration deadlines in text.
    
    Args:
        text: Text content to search for deadlines
        
    Returns:
        ISO format datetime string if found, None otherwise
        
    Raises:
        TypeError: When text is not a string
    """
    if not isinstance(text, str):
        raise TypeError("Text must be a string")
    
    # Very simple date detection (e.g., "December 31, 2024")
    month_names = (
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    )
    month_regex = "|".join(month_names)
    match = re.search(
        rf"({month_regex})\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:,)?\s*(\d{{4}})",
        text,
        re.IGNORECASE,
    )

    if match:
        month, day, year = match.groups()
        try:
            dt = datetime.strptime(f"{month} {day} {year}", "%B %d %Y")
            return dt.isoformat() + "Z"
        except ValueError:
            pass

    return None


def enrich_event(tweet: Dict[str, Any]) -> Dict[str, Any]:
    """Main enrichment function that processes a scored tweet.
    
    Args:
        tweet: Tweet object with relevance score
        
    Returns:
        Enriched event data with prize, duration, ROI, and deadline
        
    Raises:
        ValueError: When tweet is missing required fields
    """
    if "tweet_id" not in tweet or "text" not in tweet:
        raise ValueError("Tweet missing required fields")

    text = tweet["text"]
    try:
        prize, currency = extract_prize_amount(text)
    except ValueError:
        prize, currency = 0.0, "USD"

    try:
        duration = parse_duration(text)
    except ValueError:
        duration = 48  # Assume weekend if not found

    roi = calculate_roi(prize, duration) if prize and duration else 0.0
    deadline = detect_deadline(text)

    enriched = {
        "tweet_id": tweet["tweet_id"],
        "prize_value": prize,
        "duration_hours": duration,
        "roi_score": roi,
        "currency_detected": currency,
        "registration_deadline": deadline,
        "user": tweet.get("user", {}),
    }

    return enriched


def _get_currency_conversion_rate(from_currency: str, to_currency: str = "USD") -> float:
    """Get currency conversion rate from external API or cached rates.
    
    Args:
        from_currency: Source currency code (USD, ETH, BTC, etc.)
        to_currency: Target currency code (default: USD)
        
    Returns:
        Conversion rate multiplier
        
    Raises:
        CurrencyNotSupportedError: When currency is not supported
        APIError: When conversion API is unavailable
    """
    # Simple mock conversion rates
    mock_rates = {
        "USD": 1.0,  # USD to USD
        "ETH": 2800.0,  # ETH to USD (approximate)
        "BTC": 45000.0,  # BTC to USD (approximate)
        "EUR": 0.92  # EUR to USD (approximate)
    }
    
    if from_currency not in mock_rates:
        raise CurrencyNotSupportedError(f"Currency {from_currency} not supported")
    
    return mock_rates[from_currency]


def _parse_prize_patterns() -> List[Tuple[str, str]]:
    """Load prize detection patterns with associated currencies.
    
    Returns:
        List of (regex_pattern, currency) tuples
    """
    # Common prize detection patterns (regex, currency)
    patterns = [
        (r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', 'USD'),
        (r'\$(\d+)k', 'USD'),  # $10k format
        (r'€(\d+(?:,\d{3})*(?:\.\d{2})?)', 'EUR'),
        (r'€(\d+)k', 'EUR'),  # €10k format
        (r'(\d+(?:\.\d+)?)\s*ETH', 'ETH'),
        (r'(\d+(?:\.\d+)?)\s*BTC', 'BTC'),
        (r'(\d+(?:,\d{3})*)\s*USD', 'USD'),
        (r'(\d+(?:,\d{3})*)\s*dollars?', 'USD')
    ]
    return patterns


def _parse_duration_patterns() -> List[Tuple[str, int]]:
    """Load duration detection patterns with associated hour values.
    
    Returns:
        List of (regex_pattern, hours) tuples
    """
    patterns = [
        (r'(\d+)\s*hour', 1),  # Direct hours
        (r'(\d+)\s*day', 24),  # Days to hours
        (r'weekend\s*sprint', 48),  # Weekend = 48h
        (r'weekend\s*hackathon', 48),
        (r'(\d+)[\-\s]*hour\s*hackathon', 1),  # "72-hour hackathon"
        (r'(\d+)[\-\s]*day\s*hackathon', 24),  # "3-day hackathon"
    ]
    return patterns


def validate_enrichment_data(data: Dict[str, Any]) -> bool:
    """Validate enriched event data has required fields.
    
    Args:
        data: Enriched event data to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['tweet_id', 'prize_value', 'duration_hours', 'roi_score']
    return all(field in data for field in required_fields)


# Custom exception classes
class CurrencyNotSupportedError(Exception):
    """Raised when currency conversion is not supported."""
    pass


class APIError(Exception):
    """Raised when external API calls fail."""
    pass 