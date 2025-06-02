import os
import json
from typing import Dict, Any, Optional

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json and environment variables.
    
    Environment variables take precedence over config.json for sensitive data.
    
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
    
    # Override sensitive values with environment variables
    telegram_config = config.get('telegram', {})
    
    # Get bot token from environment (required)
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if bot_token:
        telegram_config['bot_token'] = bot_token
    elif not telegram_config.get('bot_token'):
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
    
    # Get channel ID from environment (optional override)
    channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
    if channel_id:
        telegram_config['channel_id'] = channel_id
    
    # Update config with potentially modified telegram settings
    config['telegram'] = telegram_config
    
    return config

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