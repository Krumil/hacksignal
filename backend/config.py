import os
import json
from typing import Dict, Any, Optional

# Try to load python-dotenv for .env file support
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    # python-dotenv not installed, rely on system environment variables
    pass

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json and environment variables.
    
    Environment variables take precedence over config.json for sensitive data.
    Telegram credentials are loaded exclusively from environment variables.
    
    Returns:
        Configuration dictionary with all settings
        
    Raises:
        FileNotFoundError: When config.json is missing
        ValueError: When required environment variables are missing
    """
    # Load base config from JSON file
    try:
        with open('backend/config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        # Try current directory if backend/ doesn't exist
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("config.json not found in backend/ or current directory")
    
    # Build telegram configuration entirely from environment variables
    telegram_config = {
        'enabled': _get_env_bool('TELEGRAM_ENABLED', True),
        'max_tweets_to_send': _get_env_int('TELEGRAM_MAX_TWEETS_TO_SEND', 15),
        'min_score_to_send': _get_env_float('TELEGRAM_MIN_SCORE_TO_SEND', 0.3)
    }
    
    # Get required telegram credentials from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
    
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
    if not channel_id:
        raise ValueError("TELEGRAM_CHANNEL_ID environment variable is required")
    
    telegram_config['bot_token'] = bot_token
    telegram_config['channel_id'] = channel_id
    
    # Replace any telegram config from JSON with environment-based config
    config['telegram'] = telegram_config
    
    return config

def _get_env_bool(key: str, default: bool) -> bool:
    """Get boolean environment variable with default fallback."""
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in ('true', '1', 'yes', 'on')

def _get_env_int(key: str, default: int) -> int:
    """Get integer environment variable with default fallback."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def _get_env_float(key: str, default: float) -> float:
    """Get float environment variable with default fallback."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default

def get_telegram_config() -> Dict[str, Any]:
    """Get Telegram-specific configuration.
    
    Returns:
        Telegram configuration dictionary
    """
    config = load_config()
    return config.get('telegram', {})

def get_processing_config() -> Dict[str, Any]:
    """Get processing-specific configuration.
    
    Returns:
        Processing configuration dictionary
    """
    config = load_config()
    return config.get('processing', {})

def get_thresholds_config() -> Dict[str, Any]:
    """Get thresholds configuration.
    
    Returns:
        Thresholds configuration dictionary
    """
    config = load_config()
    return config.get('thresholds', {}) 