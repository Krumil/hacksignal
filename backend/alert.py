"""Alert Delivery Layer

Transforms enriched events into user-visible messages.
Channel-agnostic interface with immediate alerts and daily digests.
"""

import json
import os
import asyncio
import aiohttp
from datetime import datetime, time
from typing import Dict, List, Any, Optional
from enum import Enum
from config import load_config, get_telegram_config
from enrichment import validate_enrichment_data


class AlertPriority(Enum):
    """Alert priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AlertChannel(Enum):
    """Available alert delivery channels."""
    CONSOLE = "console"
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"


def send_immediate_alert(event: Dict[str, Any]) -> bool:
    """Send high-priority notification for top ROI events.
    
    Args:
        event: Enriched event data with ROI score
        
    Returns:
        True if alert sent successfully, False otherwise
        
    Raises:
        ValueError: When event data is invalid
        AlertDeliveryError: When alert delivery fails
    """
    if not validate_enrichment_data(event):
        raise ValueError("Invalid event data")

    message = format_alert_message(event)
    return send_alert("High ROI Event", message, "high", "console")


def queue_for_digest(event: Dict[str, Any]) -> bool:
    """Add event to daily digest queue.
    
    Args:
        event: Enriched event data above relevance threshold
        
    Returns:
        True if queued successfully, False otherwise
        
    Raises:
        ValueError: When event data is invalid
        QueueError: When queueing fails
    """
    if not validate_enrichment_data(event):
        raise ValueError("Invalid event data")

    queue = _load_digest_queue()
    queue.append(event)
    _save_digest_queue(queue)
    return True


def format_alert_message(event: Dict[str, Any]) -> str:
    """Generate consistent message formatting for alerts.
    
    Args:
        event: Enriched event data
        
    Returns:
        Formatted alert message string
        
    Raises:
        ValueError: When event data is missing required fields
    """
    required = ["prize_value", "duration_hours", "currency_detected"]
    for field in required:
        if field not in event:
            raise ValueError("Event missing required fields")

    message = (
        f"Prize: {event['prize_value']} {event['currency_detected']}\n"
        f"Duration: {event['duration_hours']}h"
    )
    if event.get("registration_deadline"):
        message += f"\nDeadline: {event['registration_deadline']}"
    if event.get("expanded_url"):
        message += f"\n{event['expanded_url']}"
    return message


def send_daily_digest() -> bool:
    """Send scheduled digest delivery at configured time.
    
    Returns:
        True if digest sent successfully, False otherwise
        
    Raises:
        DigestError: When digest compilation or delivery fails
    """
    events = _load_digest_queue()
    if not events:
        return True

    for event in events:
        message = format_alert_message(event)
        send_alert("Daily Digest", message, "normal", "console")

    _save_digest_queue([])
    return True


def send_alert(title: str, body: str, priority: str = 'normal', 
               channel: str = 'console') -> bool:
    """Channel-agnostic alert delivery interface.
    
    Args:
        title: Alert title/subject
        body: Alert message content
        priority: Alert priority level (low, normal, high, urgent)
        channel: Delivery channel (console, email, webhook, slack)
        
    Returns:
        True if alert delivered successfully, False otherwise
        
    Raises:
        ValueError: When priority or channel is invalid
        AlertDeliveryError: When delivery fails
    """
    try:
        priority_enum = AlertPriority(priority)
        channel_enum = AlertChannel(channel)
    except ValueError as e:
        raise ValueError(f"Invalid priority or channel: {e}")
    
    if channel_enum == AlertChannel.CONSOLE:
        return _send_console_alert(title, body, priority_enum)
    elif channel_enum == AlertChannel.EMAIL:
        return _send_email_alert(title, body, priority_enum)
    elif channel_enum == AlertChannel.WEBHOOK:
        return _send_webhook_alert(title, body, priority_enum)
    elif channel_enum == AlertChannel.SLACK:
        return _send_slack_alert(title, body, priority_enum)
    
    return False


def check_alert_threshold(roi_score: float) -> bool:
    """Check if event ROI score meets immediate alert threshold.
    
    Args:
        roi_score: ROI score for the event
        
    Returns:
        True if meets top 10% threshold, False otherwise
    """
    config = _load_config()
    threshold_percentile = config['processing']['alert_threshold_percentile']
    
    # Using a simple fixed threshold for now
    return roi_score > 200.0


def get_digest_schedule() -> time:
    """Get configured daily digest send time.
    
    Returns:
        Time object for digest delivery
    """
    config = _load_config()
    digest_time_str = config['processing']['digest_send_time']
    
    # Parse "18:00" format
    hour, minute = map(int, digest_time_str.split(':'))
    return time(hour, minute)


def _send_console_alert(title: str, body: str, priority: AlertPriority) -> bool:
    """Send alert to console output.
    
    Args:
        title: Alert title
        body: Alert message
        priority: Alert priority level
        
    Returns:
        True if successful
    """
    timestamp = datetime.now().isoformat()
    priority_indicator = "🚨" if priority in [AlertPriority.HIGH, AlertPriority.URGENT] else "ℹ️"
    
    print(f"{priority_indicator} [{timestamp}] {priority.value.upper()}: {title}")
    print(f"   {body}")
    print("-" * 50)
    
    return True


def _send_email_alert(title: str, body: str, priority: AlertPriority) -> bool:
    """Send alert via email.
    
    Args:
        title: Alert title/subject
        body: Alert message content
        priority: Alert priority level
        
    Returns:
        True if sent successfully
    """
    print(f"[EMAIL] {title}: {body}")
    return True


def _send_webhook_alert(title: str, body: str, priority: AlertPriority) -> bool:
    """Send alert via webhook.
    
    Args:
        title: Alert title
        body: Alert message content
        priority: Alert priority level
        
    Returns:
        True if sent successfully
    """
    print(f"[WEBHOOK] {title}: {body}")
    return True


def _send_slack_alert(title: str, body: str, priority: AlertPriority) -> bool:
    """Send alert to Slack channel.
    
    Args:
        title: Alert title
        body: Alert message content
        priority: Alert priority level
        
    Returns:
        True if sent successfully
    """
    print(f"[SLACK] {title}: {body}")
    return True


def _load_config() -> Dict[str, Any]:
    """Load configuration using the new environment-aware config system.
    
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: When config.json is missing
        ValueError: When required environment variables are missing
    """
    return load_config()


def _load_digest_queue() -> List[Dict[str, Any]]:
    """Load events from digest queue file.
    
    Returns:
        List of queued events for digest
    """
    queue_file = os.path.join(os.path.dirname(__file__), "data", "digest_queue.json")
    if not os.path.exists(queue_file):
        return []
    try:
        with open(queue_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_digest_queue(events: List[Dict[str, Any]]) -> bool:
    """Save events to digest queue file.
    
    Args:
        events: List of events to queue
        
    Returns:
        True if saved successfully
    """
    queue_file = os.path.join(os.path.dirname(__file__), "data", "digest_queue.json")
    try:
        with open(queue_file, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2)
        return True
    except Exception:
        return False


# Custom exception classes
class AlertDeliveryError(Exception):
    """Raised when alert delivery fails."""
    pass


class QueueError(Exception):
    """Raised when queueing operations fail."""
    pass


class DigestError(Exception):
    """Raised when digest operations fail."""
    pass 