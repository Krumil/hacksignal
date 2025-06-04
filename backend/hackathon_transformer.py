"""Hackathon Data Transformer

Converts scored tweet data into hackathon-formatted data for frontend consumption.
Uses OpenAI's structured outputs to generate complete hackathon objects in a single LLM call.
"""

import json
import os
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
import openai

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


class HackathonLocation(str, Enum):
    """Predefined location options for hackathons."""
    remote_online = "Remote/Online"
    global_remote = "Global/Remote"
    san_francisco = "San Francisco, CA"
    new_york = "New York, NY"
    london = "London, UK"
    singapore = "Singapore"
    hybrid = "Hybrid"


class HackathonData(BaseModel):
    """Pydantic model for structured hackathon output."""
    title: str = Field(description="Engaging hackathon title (2-5 words max, should indicate the host organization)")
    organizer: str = Field(description="Organization or entity hosting the hackathon")
    prizePool: int = Field(description="Total prize money in USD (range: 5000-250000)", ge=5000, le=250000)
    duration: int = Field(description="Duration in days (range: 3-21)", ge=3, le=21)
    relevanceScore: int = Field(description="Relevance score from 1-100 based on tweet quality and engagement", ge=1, le=100)
    score: float = Field(description="Overall tweet quality score from 0.0-1.0 based on follower count, keywords, and hackathon relevance", ge=0.0, le=1.0)
    tags: List[str] = Field(description="3-5 relevant technology tags (e.g., 'AI', 'Web3', 'Blockchain')", min_items=1, max_items=5)
    description: str = Field(description="2-3 sentence description of the hackathon and what participants will build", min_length=50)
    location: HackathonLocation = Field(description="Event location, default to Remote/Online if unclear")
    reasoning: str = Field(description="Brief explanation of how you determined the hackathon details from the tweet")


def transform_tweet_to_hackathon(tweet_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a single scored tweet into hackathon format using structured LLM output.
    
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
    tweet_text = tweet_data.get('text', '')
    
    # Generate hackathon data using LLM structured output
    llm_result = _generate_hackathon_with_llm(tweet_text, keywords, score, followers)
    
    if not llm_result:
        # Fallback to rule-based generation if LLM fails
        print(f"LLM generation failed for tweet {tweet_id}, using fallback")
        return _generate_hackathon_fallback(tweet_data)
    
    # Calculate deadline based on duration
    deadline = _generate_deadline(llm_result.duration)
    
    # Build final hackathon object
    hackathon = {
        'id': f"hack_{tweet_id}",
        'title': llm_result.title,
        'organizer': llm_result.organizer,
        'prizePool': llm_result.prizePool,
        'duration': llm_result.duration,
        'relevanceScore': llm_result.relevanceScore,
        'tags': llm_result.tags,
        'description': llm_result.description,
        'deadline': deadline,
        'registrationUrl': expanded_url,
        'website': expanded_url,
        'location': llm_result.location.value,
        'sourceScore': llm_result.score,
        'sourceFollowers': followers,
        'sourceKeywords': keywords,
        'lastUpdated': datetime.now().isoformat(),
        'reasoning': llm_result.reasoning
    }
    
    return hackathon


def _generate_hackathon_with_llm(tweet_text: str, keywords: List[str], score: float, followers: int) -> Optional[HackathonData]:
    """Generate complete hackathon data using OpenAI structured outputs."""
    try:
        # Get OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Warning: OPENAI_API_KEY not found, using fallback generation")
            return None
        
        # Prepare context for the LLM
        keywords_str = ", ".join(keywords) if keywords else "technology, innovation"
        
        # Create comprehensive prompt
        prompt = f"""Analyze this tweet and generate a realistic hackathon based on the content and context:

TWEET: "{tweet_text}"
KEYWORDS: {keywords_str}
ENGAGEMENT SCORE: {score:.2f} (0.0-1.0 scale)
ACCOUNT FOLLOWERS: {followers:,}

Generate a hackathon that would realistically be associated with this tweet. Consider:

1. TITLE: Create an exciting, professional title that reflects the main technology/theme and the host organization.

2. ORGANIZER: The name of the organization hosting the hackathon.

3. PRIZE POOL: Calculate based on followers and engagement:
   - Base: max(5000, min(followers * 0.8, 100000))
   - Multiply by engagement score (0.5x to 2.0x)
   - Round to nearest 1000, keep between 5000-250000

4. DURATION: 
   - Higher prizes = longer events (21 days for 50K+, 14 days for 25K+, 7 days for 10K+)
   - Adjust for event type (sprints shorter, competitions longer)

5. RELEVANCE SCORE: Convert engagement score to 1-100 scale, capped at 100. MINIMUM VALUE IS 1 (never 0).

6. SCORE: Calculate overall tweet quality score (0.0-1.0) based on:
   - Follower count fit (0.3 weight): 1.0 if 2K-50K followers, 0.0 otherwise
   - Keyword presence (0.2 weight): 0.1 per relevant keyword, capped at 0.2
   - Topic relevance (0.5 weight): How well the tweet relates to hackathons/tech competitions
   Final score = (follower_fit * 0.3) + (keyword_score * 0.2) + (topic_relevance * 0.5), capped at 1.0

7. TAGS: Extract 3-5 relevant technology tags from keywords and tweet content

8. DESCRIPTION: Write 2-3 sentences about what participants will build and why it's exciting

9. LOCATION: Choose based on keywords or default to Remote/Online

10. REASONING: Briefly explain your decisions based on the tweet content"""

        # Call OpenAI API with structured output
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert hackathon organizer who creates realistic "
                        "and engaging hackathon events based on technology trends "
                        "and community engagement. Generate structured hackathon "
                        "data that matches the quality and scope indicated by the "
                        "tweet metrics."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        # Extract and validate the result
        result_data = json.loads(response.choices[0].message.content)
        result = HackathonData.model_validate(result_data)

        print(result)
        
        if result and _validate_llm_hackathon_data(result):
            return result
        else:
            print(f"Warning: Generated hackathon data failed validation")
            return None
            
    except Exception as e:
        print(f"Error generating LLM hackathon data: {e}")
        return None


def _validate_llm_hackathon_data(data: HackathonData) -> bool:
    """Validate the LLM-generated hackathon data."""
    try:
        # Check title length
        if not data.title or len(data.title) > 50 or len(data.title.split()) > 6:
            return False
        
        # Check prize pool range
        if not (5000 <= data.prizePool <= 250000):
            return False
        
        # Check duration range
        if not (3 <= data.duration <= 21):
            return False
        
        # Check relevance score range
        if not (1 <= data.relevanceScore <= 100):
            return False
        
        # Check score range
        if not (0.0 <= data.score <= 1.0):
            return False
        
        # Check tags
        if not data.tags or len(data.tags) == 0 or len(data.tags) > 5:
            return False
        
        # Check description length
        if not data.description or len(data.description) < 50:
            return False
        
        return True
        
    except Exception as e:
        print(f"Validation error: {e}")
        return False


def _generate_hackathon_fallback(tweet_data: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback hackathon generation using rule-based approach (original logic)."""
    # Extract basic data
    tweet_id = str(tweet_data.get('tweet_id', ''))
    score = tweet_data.get('score', 0.0)
    followers = tweet_data.get('account_followers', 0)
    keywords = tweet_data.get('keyword_matches', [])
    expanded_url = tweet_data.get('expanded_url', '')
    tweet_text = tweet_data.get('text', '')
    
    # Generate using original rule-based methods
    title = _generate_rule_based_title(keywords, score, tweet_text)
    organizer = _generate_organizer(followers, keywords)
    prize_pool = _calculate_prize_pool(score, followers)
    duration = _generate_duration(prize_pool, keywords)
    relevance_score = min(int(score * 100), 100)
    tags = _generate_tags(keywords)
    description = _generate_description(keywords, prize_pool)
    deadline = _generate_deadline(duration)
    
    # Calculate fallback score using rule-based approach
    follower_fit = 1 if 2000 <= followers <= 50000 else 0
    keyword_score = min(len(keywords) * 0.1, 0.2)
    topic_confidence = min(len([k for k in keywords if any(tech in k.lower() for tech in ['ai', 'crypto', 'blockchain', 'hackathon'])]) * 0.1, 0.5)
    fallback_score = min((follower_fit * 0.3) + keyword_score + (topic_confidence * 0.5), 1.0)
    
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
        'sourceScore': fallback_score,  # Use calculated fallback score
        'sourceFollowers': followers,
        'sourceKeywords': keywords,
        'lastUpdated': datetime.now().isoformat(),
        'reasoning': 'Generated using fallback rule-based approach'
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


def _generate_rule_based_title(keywords: List[str], score: float, tweet_text: str) -> str:
    """Generate hackathon title using rule-based approach (original logic)."""
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


def process_raw_tweets_with_llm_scoring(raw_data_dir: str = "data/raw") -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Process raw tweets with LLM-based scoring and transformation.
    
    Args:
        raw_data_dir: Path to directory containing raw tweet JSON files
        
    Returns:
        Tuple of (scored_tweets, hackathons) - both lists sorted by score (highest first)
        
    Raises:
        FileNotFoundError: When raw data directory doesn't exist
    """
    import glob
    
    # Get the directory where this script is located (project root)
    from scoring import _find_project_root, _normalize_tweet_structure
    
    script_dir = _find_project_root()
    
    # If raw_data_dir is relative, make it relative to the script directory
    if not os.path.isabs(raw_data_dir):
        raw_data_dir = os.path.join(script_dir, raw_data_dir)
    
    if not os.path.exists(raw_data_dir):
        raise FileNotFoundError(f"Raw data directory '{raw_data_dir}' not found")
    
    scored_tweets = []
    hackathons = []
    tweet_files = glob.glob(os.path.join(raw_data_dir, "tweet_*.json"))
    
    print(f"Found {len(tweet_files)} tweet files to process with LLM scoring...")
    
    for file_path in tweet_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extract tweet_data from the file structure
            if 'tweet_data' in data:
                tweet = data['tweet_data']
                
                # Normalize the tweet structure
                normalized_tweet = _normalize_tweet_structure(tweet)
                
                # Extract basic data for LLM processing
                tweet_id = str(normalized_tweet.get('id', ''))
                tweet_text = normalized_tweet.get('text', '')
                followers = normalized_tweet.get('user', {}).get('followers_count', 0)
                expanded_url = normalized_tweet.get('expanded_url', '')
                
                # Extract keywords from the text (simple extraction)
                keywords = _extract_simple_keywords(tweet_text)
                
                # Generate hackathon data using LLM (which now includes scoring)
                llm_result = _generate_hackathon_with_llm(tweet_text, keywords, 0.0, followers)
                
                if llm_result:
                    # Create hackathon object
                    deadline = _generate_deadline(llm_result.duration)
                    hackathon = {
                        'id': f"hack_{tweet_id}",
                        'title': llm_result.title,
                        'organizer': llm_result.organizer,
                        'prizePool': llm_result.prizePool,
                        'duration': llm_result.duration,
                        'relevanceScore': llm_result.relevanceScore,
                        'tags': llm_result.tags,
                        'description': llm_result.description,
                        'deadline': deadline,
                        'registrationUrl': expanded_url,
                        'website': expanded_url,
                        'location': llm_result.location.value,
                        'sourceScore': llm_result.score,
                        'sourceFollowers': followers,
                        'sourceKeywords': keywords,
                        'lastUpdated': datetime.now().isoformat(),
                        'reasoning': llm_result.reasoning
                    }
                    hackathons.append(hackathon)
                    
                    # Create scored tweet object for compatibility with existing pipeline
                    scored_tweet = {
                        "tweet_id": tweet_id,
                        "score": llm_result.score,
                        "account_followers": followers,
                        "keyword_matches": keywords,
                        "follower_fit": 1 if 2000 <= followers <= 50000 else 0,
                        "expanded_url": expanded_url,
                        "source_file": os.path.basename(file_path),
                        "collected_at": data.get('collected_at', ''),
                        "text": tweet_text[:200] + "..." if len(tweet_text) > 200 else tweet_text
                    }
                    scored_tweets.append(scored_tweet)
                    
                    print(f"✅ Processed tweet {tweet_id} with LLM score: {llm_result.score:.3f}")
                else:
                    print(f"❌ Failed to process tweet {tweet_id} with LLM")
                    
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON in {file_path}: {e}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Sort both lists by score (highest first)
    scored_tweets.sort(key=lambda x: x['score'], reverse=True)
    hackathons.sort(key=lambda x: x['sourceScore'], reverse=True)
    
    print(f"Successfully processed {len(scored_tweets)} tweets with LLM scoring")
    return scored_tweets, hackathons


def _extract_simple_keywords(text: str) -> List[str]:
    """Simple keyword extraction for LLM processing."""
    if not text:
        return []
    
    text_lower = text.lower()
    keywords = []
    
    # Common hackathon/tech keywords
    keyword_patterns = [
        'hackathon', 'hack', 'challenge', 'competition', 'sprint', 'contest',
        'ai', 'artificial intelligence', 'machine learning', 'ml', 'neural',
        'blockchain', 'crypto', 'bitcoin', 'ethereum', 'web3', 'defi', 'nft',
        'gamefi', 'dao', 'dapp', 'smart contract', 'infrastructure', 'build',
        'developer', 'coding', 'programming', 'innovation', 'technology'
    ]
    
    for keyword in keyword_patterns:
        if keyword in text_lower:
            keywords.append(keyword)
    
    # Extract hashtags
    import re
    hashtags = re.findall(r'#(\w+)', text)
    keywords.extend([f"#{tag}" for tag in hashtags[:5]])  # Limit hashtags
    
    return list(set(keywords))  # Remove duplicates 