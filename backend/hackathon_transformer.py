"""Hackathon Data Transformer

Converts scored tweet data into hackathon-formatted data for frontend consumption.
Moves complex transformation logic from frontend to backend for better performance and maintainability.
"""

import json
import os
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from config import load_config


def transform_tweet_to_hackathon(tweet_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a single scored tweet into hackathon format.
    
    Args:
        tweet_data: Scored tweet object with score, keywords, etc.
        
    Returns:
        Hackathon object formatted for frontend consumption
    """
    # Extract basic data
    tweet_id = str(tweet_data.get('tweet_id', ''))
    score = tweet_data.get('score', 0.0)
    followers = tweet_data.get('account_followers', 0)
    keywords = tweet_data.get('keyword_matches', [])
    expanded_url = tweet_data.get('expanded_url', '')
    tweet_text = tweet_data.get('text', '')  # Add tweet text extraction
    
    # Generate hackathon data
    title = _generate_title(keywords, score, tweet_text)  # Pass tweet text to title generation
    organizer = _generate_organizer(followers, keywords)
    prize_pool = _calculate_prize_pool(score, followers)
    duration = _generate_duration(prize_pool, keywords)
    relevance_score = min(int(score * 100), 100)
    tags = _generate_tags(keywords)
    description = _generate_description(keywords, prize_pool)
    deadline = _generate_deadline(duration)
    
    hackathon = {
        'id': f"hack_{tweet_id}",
        'title': title,
        'organizer': organizer,
        'prizePool': prize_pool,
        'duration': duration,
        'relevanceScore': relevance_score,
        'tags': tags,
        'description': description,
        'deadline': deadline,
        'registrationUrl': expanded_url,
        'website': expanded_url,
        'location': _determine_location(keywords),
        'sourceScore': score,
        'sourceFollowers': followers,
        'sourceKeywords': keywords,
        'lastUpdated': datetime.now().isoformat()
    }
    
    return hackathon


def transform_tweets_batch(scored_tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transform multiple scored tweets into hackathon format.
    
    Args:
        scored_tweets: List of scored tweet objects
        
    Returns:
        List of hackathon objects formatted for frontend
    """
    hackathons = []
    
    for tweet_data in scored_tweets:
        try:
            hackathon = transform_tweet_to_hackathon(tweet_data)
            hackathons.append(hackathon)
        except Exception as e:
            print(f"Error transforming tweet {tweet_data.get('tweet_id', 'unknown')}: {e}")
            continue
    
    # Sort by relevance score (highest first)
    hackathons.sort(key=lambda x: x['relevanceScore'], reverse=True)
    
    return hackathons


def save_hackathons(hackathons: List[Dict[str, Any]], output_file: str = "data/enriched/hackathons.json") -> None:
    """Save transformed hackathon data to file.
    
    Args:
        hackathons: List of hackathon objects
        output_file: Path to output file
    """
    # Get project root
    from scoring import _find_project_root
    script_dir = _find_project_root()
    
    # If output_file is relative, make it relative to the script directory
    if not os.path.isabs(output_file):
        output_file = os.path.join(script_dir, output_file)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Add metadata
    output_data = {
        'hackathons': hackathons,
        'metadata': {
            'count': len(hackathons),
            'last_updated': datetime.now().isoformat(),
            'version': '1.0'
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(hackathons)} hackathons to {output_file}")


def _generate_title(keywords: List[str], score: float, tweet_text: str) -> str:
    """Generate hackathon title based on keywords, score, and tweet content."""
    if not tweet_text:
        return "Innovation Challenge"
    
    # Clean tweet text for processing
    text = tweet_text.lower().strip()
    
    # Remove URLs, mentions, and hashtags for cleaner text processing
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#(\w+)', r'\1', text)  # Keep hashtag content but remove #
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Extract key phrases and information
    title_components = _extract_title_components(text, keywords)
    
    # Determine event type from text
    event_type = _determine_event_type(text, keywords)
    
    # Generate title based on extracted components
    if title_components['theme']:
        base_title = f"{title_components['theme'].title()} {event_type}"
    elif title_components['tech_focus']:
        base_title = f"{title_components['tech_focus'].title()} {event_type}"
    elif keywords:
        # Fallback to keyword-based title
        primary_keyword = keywords[0].replace('#', '').title()
        base_title = f"{primary_keyword} {event_type}"
    else:
        base_title = f"Innovation {event_type}"
    
    # Add prestige modifier based on score and context
    if score >= 0.8 or title_components['is_premium']:
        if 'summit' not in base_title.lower():
            base_title = base_title.replace('Challenge', 'Summit').replace('Hackathon', 'Summit')
    elif title_components['duration'] and 'sprint' in title_components['duration']:
        base_title = base_title.replace('Challenge', 'Sprint').replace('Hackathon', 'Sprint')
    
    # Clean up and finalize
    base_title = re.sub(r'\s+', ' ', base_title).strip()
    
    # Ensure title is reasonable length (max ~50 chars)
    if len(base_title) > 50:
        words = base_title.split()
        if len(words) > 3:
            base_title = ' '.join(words[:3])
    
    return base_title


def _extract_title_components(text: str, keywords: List[str]) -> Dict[str, Any]:
    """Extract meaningful components from tweet text for title generation."""
    components = {
        'theme': None,
        'tech_focus': None,
        'duration': None,
        'is_premium': False,
        'location': None
    }
    
    # Look for themes and focuses
    theme_patterns = [
        r'(\w+\s+(?:innovation|revolution|transformation|future))',
        r'(build\s+the\s+\w+)',
        r'(create\s+(?:the\s+)?next\s+\w+)',
        r'(\w+\s+(?:builder|creator|developer)s?)',
        r'((?:next|future)\s+generation\s+\w+)'
    ]
    
    for pattern in theme_patterns:
        match = re.search(pattern, text)
        if match and len(match.group(1)) < 30:
            components['theme'] = match.group(1).strip()
            break
    
    # Extract technology focus
    tech_keywords = ['ai', 'web3', 'blockchain', 'crypto', 'defi', 'nft', 'gamefi', 'infrastructure']
    for tech in tech_keywords:
        if tech in text and tech in [k.lower() for k in keywords]:
            components['tech_focus'] = tech
            break
    
    # Look for duration indicators
    duration_patterns = [
        r'(\d+[-\s]?(?:hour|day|week)s?\s+(?:sprint|hackathon|challenge))',
        r'((?:weekend|week|month)[-\s]?long)',
        r'(\d+h\s+(?:sprint|hack))'
    ]
    
    for pattern in duration_patterns:
        match = re.search(pattern, text)
        if match:
            components['duration'] = match.group(1)
            break
    
    # Check for premium indicators
    premium_indicators = ['top', 'elite', 'premier', 'exclusive', 'invite-only', 'championship']
    components['is_premium'] = any(indicator in text for indicator in premium_indicators)
    
    # Look for prizes to enhance premium detection
    prize_patterns = [r'\$\d+k', r'\$\d{1,3},?\d{3}', r'€\d+k', r'₹\d+']
    if any(re.search(pattern, text) for pattern in prize_patterns):
        components['is_premium'] = True
    
    return components


def _determine_event_type(text: str, keywords: List[str]) -> str:
    """Determine the most appropriate event type based on text content."""
    text_lower = text.lower()
    
    # Event type priority (more specific first)
    if any(word in text_lower for word in ['sprint', 'speed', 'quick', 'rapid']):
        return "Sprint"
    elif any(word in text_lower for word in ['summit', 'conference', 'expo']):
        return "Summit"
    elif any(word in text_lower for word in ['championship', 'tournament', 'contest']):
        return "Championship"
    elif any(word in text_lower for word in ['bootcamp', 'workshop', 'training']):
        return "Bootcamp"
    elif any(word in text_lower for word in ['challenge', 'quest']):
        return "Challenge"
    elif any(word in text_lower for word in ['hackathon', 'hack']):
        return "Hackathon"
    elif any(word in text_lower for word in ['competition', 'compete']):
        return "Competition"
    elif any(word in text_lower for word in ['build', 'create', 'develop']):
        return "Builder Challenge"
    else:
        return "Challenge"  # Default fallback


def _generate_organizer(followers: int, keywords: List[str]) -> str:
    """Generate organizer name based on follower count and keywords."""
    keywords_lower = [k.lower() for k in keywords]
    
    # High-tier organizers (>20K followers)
    if followers > 20000:
        if any('web3' in k for k in keywords_lower):
            return "Web3 Foundation"
        elif any('ai' in k for k in keywords_lower):
            return "AI Research Institute"
        elif any('blockchain' in k for k in keywords_lower):
            return "Blockchain Alliance"
        elif any('crypto' in k for k in keywords_lower):
            return "Crypto Innovation Labs"
        else:
            return "TechCorp Global"
    
    # Mid-tier organizers (5K-20K followers)
    elif followers > 5000:
        if any('defi' in k for k in keywords_lower):
            return "DeFi Collective"
        elif any('nft' in k for k in keywords_lower):
            return "Digital Arts Foundation"
        elif any('gaming' in k for k in keywords_lower):
            return "GameFi Alliance"
        elif any('infrastructure' in k for k in keywords_lower):
            return "Protocol Labs"
        else:
            return "Innovation Hub"
    
    # Community organizers (2K-5K followers)
    elif followers > 2000:
        if any('cross-chain' in k for k in keywords_lower):
            return "Bridge Builders Guild"
        elif any('ai' in k for k in keywords_lower):
            return "AI Developers Community"
        else:
            return "Developer Community"
    
    # Startup/small organizers
    else:
        return "StartupLab Collective"


def _calculate_prize_pool(score: float, followers: int) -> int:
    """Calculate prize pool based on score and follower count."""
    # Base amount calculation
    base_amount = max(5000, min(followers * 0.8, 100000))
    
    # Score multiplier (0.5x to 2.0x)
    score_multiplier = max(0.5, min(score * 1.5, 2.0))
    
    # Calculate total
    total = int(base_amount * score_multiplier)
    
    # Round to nearest 1000
    rounded = round(total / 1000) * 1000
    
    # Ensure reasonable bounds
    return max(5000, min(rounded, 250000))


def _generate_duration(prize_pool: int, keywords: List[str]) -> int:
    """Generate duration based on prize pool and event type."""
    keywords_lower = [k.lower() for k in keywords]
    
    # Longer events for higher prizes
    if prize_pool > 50000:
        base_duration = 21  # 3 weeks
    elif prize_pool > 25000:
        base_duration = 14  # 2 weeks
    elif prize_pool > 10000:
        base_duration = 7   # 1 week
    else:
        base_duration = 5   # 5 days
    
    # Adjust based on event type
    if any('sprint' in k for k in keywords_lower):
        return max(3, base_duration - 7)  # Shorter sprints
    elif any('competition' in k for k in keywords_lower):
        return base_duration + 7  # Longer competitions
    elif any('challenge' in k for k in keywords_lower):
        return base_duration  # Standard challenges
    
    return base_duration


def _generate_tags(keywords: List[str]) -> List[str]:
    """Generate and clean tags from keywords."""
    if not keywords:
        return ["Innovation", "Technology"]
    
    # Tag mapping for better formatting
    tag_mapping = {
        'ai': 'AI',
        'web3': 'Web3',
        'blockchain': 'Blockchain',
        'crypto': 'Crypto',
        'defi': 'DeFi',
        'nft': 'NFT',
        'cross-chain': 'Cross-Chain',
        'interoperability': 'Interoperability',
        'agentic': 'AI Agents',
        'infrastructure': 'Infrastructure',
        'gaming': 'Gaming',
        'gamefi': 'GameFi',
        'dao': 'DAO',
        'dapp': 'DApp',
        'smart contract': 'Smart Contracts',
        'zero-knowledge': 'Zero-Knowledge',
        'layer2': 'Layer 2',
        'scaling': 'Scaling'
    }
    
    # Filter and clean keywords
    clean_keywords = []
    keywords_lower = [k.lower() for k in keywords]
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        
        # Skip common words
        if keyword_lower in ['hack', 'the', 'and', 'or', 'by', 'to', 'of', 'in', 'on', 'at', 'hackathon', 'challenge']:
            continue
        
        # Apply mapping or capitalize
        if keyword_lower in tag_mapping:
            clean_keywords.append(tag_mapping[keyword_lower])
        elif len(keyword) > 2:
            # Capitalize first letter
            clean_keywords.append(keyword.capitalize())
    
    # Remove duplicates and limit to 5 tags
    unique_tags = list(dict.fromkeys(clean_keywords))[:5]
    
    # Ensure we have at least 2 tags
    if len(unique_tags) < 2:
        default_tags = ["Innovation", "Technology", "Development", "Contest"]
        for tag in default_tags:
            if tag not in unique_tags:
                unique_tags.append(tag)
                if len(unique_tags) >= 2:
                    break
    
    return unique_tags


def _generate_description(keywords: List[str], prize_pool: int) -> str:
    """Generate hackathon description based on keywords and prize pool."""
    if not keywords:
        return f"Join this innovation challenge and compete for ${prize_pool:,} in prizes!"
    
    # Main technology focus
    primary_tech = None
    keywords_lower = [k.lower() for k in keywords]
    
    tech_descriptions = {
        'ai': 'artificial intelligence and machine learning',
        'web3': 'decentralized web technologies',
        'blockchain': 'blockchain and distributed ledger technology',
        'crypto': 'cryptocurrency and digital assets',
        'defi': 'decentralized finance protocols',
        'nft': 'non-fungible tokens and digital collectibles',
        'cross-chain': 'cross-chain and interoperability solutions',
        'infrastructure': 'developer infrastructure and tooling',
        'gaming': 'blockchain gaming and GameFi',
        'dao': 'decentralized autonomous organizations'
    }
    
    for tech, description in tech_descriptions.items():
        if any(tech in k for k in keywords_lower):
            primary_tech = description
            break
    
    if primary_tech:
        description = f"Build innovative solutions using {primary_tech}. "
    else:
        description = "Create cutting-edge applications and tools. "
    
    description += f"Compete with developers worldwide for ${prize_pool:,} in total prizes. "
    
    # Add call to action based on prize tier
    if prize_pool > 50000:
        description += "This is a premium event with top-tier judges and sponsors."
    elif prize_pool > 25000:
        description += "Great opportunity to showcase your skills and win significant rewards."
    else:
        description += "Perfect for learning, networking, and building your portfolio."
    
    return description


def _generate_deadline(duration: int) -> str:
    """Generate deadline based on duration."""
    # Assume events start in 3-7 days and run for the specified duration
    start_delay = 5  # days
    deadline = datetime.now() + timedelta(days=start_delay + duration)
    return deadline.isoformat()


def _determine_location(keywords: List[str]) -> str:
    """Determine event location from keywords."""
    keywords_lower = [k.lower() for k in keywords]
    
    # Check for location indicators
    if any('remote' in k or 'online' in k or 'virtual' in k for k in keywords_lower):
        return "Remote/Online"
    elif any('global' in k or 'worldwide' in k or 'international' in k for k in keywords_lower):
        return "Global/Remote"
    elif any('sf' in k or 'san francisco' in k for k in keywords_lower):
        return "San Francisco, CA"
    elif any('nyc' in k or 'new york' in k for k in keywords_lower):
        return "New York, NY"
    elif any('london' in k for k in keywords_lower):
        return "London, UK"
    elif any('singapore' in k for k in keywords_lower):
        return "Singapore"
    else:
        return "Remote/Online"  # Default to remote


def validate_hackathon_data(hackathon: Dict[str, Any]) -> bool:
    """Validate hackathon data structure.
    
    Args:
        hackathon: Hackathon object to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = [
        'id', 'title', 'organizer', 'prizePool', 'duration', 
        'relevanceScore', 'tags', 'description', 'deadline'
    ]
    
    # Check required fields
    for field in required_fields:
        if field not in hackathon:
            return False
    
    # Validate data types and ranges
    try:
        assert isinstance(hackathon['prizePool'], int) and hackathon['prizePool'] >= 0
        assert isinstance(hackathon['duration'], int) and hackathon['duration'] > 0
        assert isinstance(hackathon['relevanceScore'], int) and 0 <= hackathon['relevanceScore'] <= 100
        assert isinstance(hackathon['tags'], list) and len(hackathon['tags']) > 0
        assert isinstance(hackathon['title'], str) and len(hackathon['title']) > 0
        assert isinstance(hackathon['organizer'], str) and len(hackathon['organizer']) > 0
        return True
    except (AssertionError, TypeError):
        return False 