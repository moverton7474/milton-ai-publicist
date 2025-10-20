"""
PR Opportunity Finder - Milton AI Publicist
Identify trending topics, suggest content opportunities, and recommend hashtags
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re
import logging
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PROpportunityFinder:
    """
    Identify PR opportunities and content suggestions

    Features:
    - Trending topic detection
    - Hashtag recommendations
    - Competitive analysis
    - Content gap identification
    - Engagement opportunity scoring
    """

    def __init__(self, anthropic_api_key: Optional[str] = None):
        """Initialize PR opportunity finder"""
        self.api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_client = Anthropic(api_key=self.api_key)

        # College athletics trends and events
        self.sports_calendar = {
            "football": ["Aug-Dec", "recruiting", "signing day", "bowl games"],
            "basketball": ["Nov-Mar", "march madness", "conference tournament"],
            "baseball": ["Feb-Jun", "college world series", "draft"],
            "volleyball": ["Aug-Dec", "ncaa tournament"],
            "soccer": ["Aug-Nov", "ncaa tournament"],
            "track": ["Jan-Jun", "championships"]
        }

        # Common college athletics hashtags
        self.base_hashtags = {
            "ksu": ["#KSU", "#KSUOwls", "#LetsGoOwls", "#OwlNation", "#KSUAthletics"],
            "conference": ["#CUSA", "#ConferenceUSA"],
            "general": ["#CollegeAthletics", "#NCAA", "#GoOwls"]
        }

        logger.info("PR Opportunity Finder initialized")

    # ========================================================================
    # TRENDING TOPICS
    # ========================================================================

    def analyze_trending_topics(self, sport: str = "all") -> Dict:
        """
        Identify trending topics in college athletics

        Args:
            sport: Specific sport or "all"

        Returns:
            Dict with trending topics, hashtags, and opportunities
        """
        try:
            current_month = datetime.now().strftime("%B")

            prompt = f"""You are a college athletics PR analyst.

Identify the TOP 5 trending topics in college athletics RIGHT NOW ({current_month} 2025).

Focus on:
- Kennesaw State University (KSU) athletics specifically
- Conference USA (CUSA) news
- National college sports trends
- Recruiting cycles
- Championship seasons
- NIL (Name, Image, Likeness) developments

For each trending topic, provide:
1. Topic name (2-4 words)
2. Why it's trending (1 sentence)
3. PR opportunity score (1-10)
4. Suggested content angle for KSU
5. Recommended hashtags (3-5)

Format as JSON:
{{
  "trending_topics": [
    {{
      "topic": "topic name",
      "reason": "why it's trending",
      "opportunity_score": 1-10,
      "ksu_angle": "how KSU can leverage this",
      "hashtags": ["#hashtag1", "#hashtag2"]
    }}
  ]
}}"""

            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            analysis = json.loads(response.content[0].text.strip())

            return {
                "analyzed_at": datetime.now().isoformat(),
                "sport_focus": sport,
                "trending_topics": analysis.get("trending_topics", [])
            }

        except Exception as e:
            logger.error(f"Trending topics analysis failed: {e}")
            return {
                "error": str(e),
                "trending_topics": []
            }

    # ========================================================================
    # HASHTAG RECOMMENDATIONS
    # ========================================================================

    def recommend_hashtags(
        self,
        content: str,
        sport: Optional[str] = None,
        scenario: Optional[str] = None
    ) -> Dict:
        """
        Recommend optimal hashtags for a post

        Args:
            content: Post content
            sport: Sport type (football, basketball, etc.)
            scenario: Post scenario (game_highlights, recruiting, etc.)

        Returns:
            Dict with primary, secondary, and trending hashtags
        """
        # Extract keywords from content
        keywords = self._extract_keywords(content)

        # Build hashtag recommendations
        primary = self.base_hashtags["ksu"][:3]  # Always include KSU tags

        secondary = []
        trending = []

        # Sport-specific hashtags
        if sport:
            sport_tags = self._get_sport_hashtags(sport)
            secondary.extend(sport_tags[:2])

        # Scenario-specific hashtags
        if scenario:
            scenario_tags = self._get_scenario_hashtags(scenario)
            secondary.extend(scenario_tags[:2])

        # Conference hashtags
        secondary.extend(self.base_hashtags["conference"][:1])

        # Keyword-based hashtags
        for keyword in keywords[:3]:
            hashtag = f"#{keyword.capitalize()}"
            if hashtag not in primary and hashtag not in secondary:
                trending.append(hashtag)

        return {
            "primary": primary[:3],  # Most important (brand)
            "secondary": secondary[:5],  # Context-specific
            "trending": trending[:3],  # Content-specific
            "suggested_count": "Use 5-8 total hashtags for optimal reach"
        }

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract key words/phrases from content"""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'i', 'we', 'our', 'this', 'that'
        }

        # Extract words
        words = re.findall(r'\b[a-z]{4,}\b', content.lower())

        # Filter and count
        filtered = [w for w in words if w not in stop_words]
        word_counts = Counter(filtered)

        # Return top keywords
        return [word for word, count in word_counts.most_common(10)]

    def _get_sport_hashtags(self, sport: str) -> List[str]:
        """Get sport-specific hashtags"""
        sport_tags = {
            "football": ["#CollegeFootball", "#CFB", "#KSUFootball"],
            "basketball": ["#CollegeBasketball", "#MarchMadness", "#KSUBasketball"],
            "baseball": ["#CollegeBaseball", "#KSUBaseball"],
            "volleyball": ["#CollegeVolleyball", "#KSUVolleyball"],
            "soccer": ["#CollegeSoccer", "#KSUSoccer"],
            "track": ["#TrackAndField", "#KSUTrack"]
        }
        return sport_tags.get(sport.lower(), [])

    def _get_scenario_hashtags(self, scenario: str) -> List[str]:
        """Get scenario-specific hashtags"""
        scenario_tags = {
            "game_highlights": ["#GameDay", "#OwlsWin", "#Victory"],
            "recruiting_update": ["#Recruiting", "#CommittedToOwls", "#NewOwl"],
            "partner_appreciation": ["#ThankYou", "#Partners", "#Community"],
            "academic_achievement": ["#StudentAthlete", "#Academic Excellence"],
            "award_announcement": ["#Awards", "#Congrats", "#Excellence"],
            "team_celebration": ["#TeamWork", "#Champions", "#OwlPride"]
        }
        return scenario_tags.get(scenario, [])

    # ========================================================================
    # COMPETITIVE ANALYSIS
    # ========================================================================

    def analyze_competitors(self, competitors: List[str] = None) -> Dict:
        """
        Analyze competitor social media presence

        Args:
            competitors: List of competitor schools (defaults to CUSA rivals)

        Returns:
            Competitive intelligence and opportunities
        """
        if not competitors:
            # Default CUSA competitors
            competitors = [
                "Liberty University",
                "Jacksonville State",
                "Sam Houston State",
                "Western Kentucky",
                "Middle Tennessee"
            ]

        try:
            prompt = f"""You are a college athletics PR analyst specializing in competitive intelligence.

Analyze Kennesaw State University's competitive position vs these CUSA rivals:
{', '.join(competitors)}

Provide:
1. Content gaps (what competitors are doing that KSU isn't)
2. KSU strengths (what KSU does better)
3. Untapped opportunities (white space in the market)
4. Recommended content themes (3-5 themes KSU should emphasize)

Format as JSON:
{{
  "content_gaps": ["gap 1", "gap 2", "gap 3"],
  "ksu_strengths": ["strength 1", "strength 2"],
  "opportunities": ["opportunity 1", "opportunity 2"],
  "recommended_themes": ["theme 1", "theme 2", "theme 3"]
}}"""

            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            analysis = json.loads(response.content[0].text.strip())

            return {
                "analyzed_at": datetime.now().isoformat(),
                "competitors_analyzed": competitors,
                "analysis": analysis
            }

        except Exception as e:
            logger.error(f"Competitive analysis failed: {e}")
            return {"error": str(e)}

    # ========================================================================
    # CONTENT OPPORTUNITIES
    # ========================================================================

    def find_content_opportunities(
        self,
        recent_posts: List[str] = None,
        upcoming_events: List[str] = None
    ) -> Dict:
        """
        Identify content opportunities based on recent activity and upcoming events

        Args:
            recent_posts: List of recent post topics
            upcoming_events: List of upcoming events/games

        Returns:
            Content suggestions with priority scores
        """
        try:
            current_date = datetime.now().strftime("%B %d, %Y")

            prompt = f"""You are a college athletics content strategist.

Today's date: {current_date}

Recent KSU posts covered: {', '.join(recent_posts) if recent_posts else 'None provided'}
Upcoming events: {', '.join(upcoming_events) if upcoming_events else 'General season'}

Generate 5 HIGH-IMPACT content opportunities for Kennesaw State Athletics social media.

Consider:
- Timing relevance (what's happening now)
- Audience engagement potential
- Brand alignment
- Content gaps in recent posting
- Upcoming opportunities

For each opportunity:
1. Content idea (specific post concept)
2. Why it works (rationale)
3. Best post format (text, graphic, video)
4. Optimal timing (when to post)
5. Priority score (1-10)
6. Target platforms (LinkedIn, Twitter, Instagram)

Format as JSON:
{{
  "opportunities": [
    {{
      "idea": "specific content idea",
      "rationale": "why this works",
      "format": "text|graphic|video",
      "timing": "when to post",
      "priority": 1-10,
      "platforms": ["platform1", "platform2"]
    }}
  ]
}}"""

            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            analysis = json.loads(response.content[0].text.strip())

            # Sort by priority
            opportunities = analysis.get("opportunities", [])
            opportunities.sort(key=lambda x: x.get("priority", 0), reverse=True)

            return {
                "generated_at": datetime.now().isoformat(),
                "opportunities": opportunities,
                "total_found": len(opportunities)
            }

        except Exception as e:
            logger.error(f"Content opportunity finding failed: {e}")
            return {"error": str(e), "opportunities": []}

    # ========================================================================
    # ENGAGEMENT OPPORTUNITIES
    # ========================================================================

    def identify_engagement_opportunities(self) -> Dict:
        """
        Identify specific opportunities to increase engagement

        Returns:
            Actionable engagement tactics
        """
        opportunities = []

        # Time-based opportunities
        current_hour = datetime.now().hour
        current_day = datetime.now().strftime("%A")

        if current_day in ["Tuesday", "Wednesday", "Thursday"]:
            if 9 <= current_hour <= 11:
                opportunities.append({
                    "type": "timing",
                    "opportunity": "Post now for optimal engagement",
                    "reason": f"{current_day} at {current_hour}:00 is typically high-engagement",
                    "action": "Schedule post for within next hour",
                    "priority": 8
                })

        # Content type opportunities
        opportunities.append({
            "type": "media",
            "opportunity": "Include video content",
            "reason": "Video posts get 2-3x more engagement than text-only",
            "action": "Generate avatar video or use game highlights",
            "priority": 7
        })

        # Interactive content
        opportunities.append({
            "type": "interaction",
            "opportunity": "Ask audience a question",
            "reason": "Questions increase comment rates by 50-100%",
            "action": "End post with 'What do you think?' or poll",
            "priority": 6
        })

        # Trending participation
        opportunities.append({
            "type": "trending",
            "opportunity": "Leverage trending hashtags",
            "reason": "Tap into existing conversations for wider reach",
            "action": "Include 2-3 trending sports hashtags",
            "priority": 7
        })

        # User-generated content
        opportunities.append({
            "type": "ugc",
            "opportunity": "Feature fan/student content",
            "reason": "UGC increases authenticity and fan engagement",
            "action": "Repost fan photos with credit and #OwlNation",
            "priority": 8
        })

        return {
            "opportunities": opportunities,
            "total_found": len(opportunities)
        }

    # ========================================================================
    # COMPLETE PR ANALYSIS
    # ========================================================================

    def generate_pr_report(self) -> Dict:
        """Generate complete PR opportunity report"""
        logger.info("Generating complete PR opportunity report...")

        trending = self.analyze_trending_topics()
        competitive = self.analyze_competitors()
        content_opps = self.find_content_opportunities()
        engagement_opps = self.identify_engagement_opportunities()

        return {
            "generated_at": datetime.now().isoformat(),
            "trending_topics": trending,
            "competitive_analysis": competitive,
            "content_opportunities": content_opps,
            "engagement_opportunities": engagement_opps,
            "summary": {
                "total_opportunities": (
                    len(trending.get("trending_topics", [])) +
                    len(content_opps.get("opportunities", [])) +
                    len(engagement_opps.get("opportunities", []))
                )
            }
        }


def main():
    """Test PR opportunity finder"""
    finder = PROpportunityFinder()

    print("="*70)
    print("PR OPPORTUNITY FINDER - TEST")
    print("="*70)

    # Test 1: Trending topics
    print("\n[1/5] Analyzing trending topics...")
    trending = finder.analyze_trending_topics()
    print(f"  Found {len(trending.get('trending_topics', []))} trending topics")

    for topic in trending.get("trending_topics", [])[:3]:
        print(f"\n  Topic: {topic.get('topic')}")
        print(f"  Opportunity Score: {topic.get('opportunity_score')}/10")
        print(f"  KSU Angle: {topic.get('ksu_angle')}")

    # Test 2: Hashtag recommendations
    print("\n[2/5] Testing hashtag recommendations...")
    sample_post = "I am so proud of our volleyball team for winning the conference championship!"
    hashtags = finder.recommend_hashtags(sample_post, sport="volleyball", scenario="game_highlights")

    print(f"  Primary: {', '.join(hashtags['primary'])}")
    print(f"  Secondary: {', '.join(hashtags['secondary'])}")
    print(f"  Trending: {', '.join(hashtags['trending'])}")

    # Test 3: Competitive analysis
    print("\n[3/5] Running competitive analysis...")
    competitive = finder.analyze_competitors()
    analysis = competitive.get("analysis", {})

    if "ksu_strengths" in analysis:
        print(f"  KSU Strengths: {len(analysis['ksu_strengths'])}")
        print(f"  Content Gaps: {len(analysis.get('content_gaps', []))}")
        print(f"  Opportunities: {len(analysis.get('opportunities', []))}")

    # Test 4: Content opportunities
    print("\n[4/5] Finding content opportunities...")
    content = finder.find_content_opportunities(
        recent_posts=["game highlights", "recruiting update"],
        upcoming_events=["homecoming game", "alumni weekend"]
    )

    opps = content.get("opportunities", [])
    print(f"  Found {len(opps)} content opportunities")

    if opps:
        top_opp = opps[0]
        print(f"\n  Top Opportunity (Priority {top_opp.get('priority')}/10):")
        print(f"    {top_opp.get('idea')}")

    # Test 5: Engagement opportunities
    print("\n[5/5] Identifying engagement opportunities...")
    engagement = finder.identify_engagement_opportunities()
    print(f"  Found {engagement['total_found']} engagement tactics")

    print("\n" + "="*70)


if __name__ == "__main__":
    main()
