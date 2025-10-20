"""
News Monitoring Module - Milton AI Publicist
Automatically monitor KSU Athletics news and generate post suggestions
"""

import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsMonitor:
    """
    Monitor news sources for KSU Athletics content and generate post suggestions

    Features:
    - RSS feed monitoring
    - Web scraping for KSU news
    - Sentiment analysis
    - Automatic post generation suggestions
    - Priority scoring for newsworthy content
    """

    def __init__(self, anthropic_api_key: Optional[str] = None):
        """Initialize news monitor"""
        self.api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_client = Anthropic(api_key=self.api_key)

        # News sources for KSU Athletics
        self.news_sources = {
            "ksu_athletics": "https://ksuowls.com/news.aspx/rss/All",
            "espn_owls": "https://www.espn.com/espn/rss/ncf/news",
            "sports_reference": "https://www.sports-reference.com/cbb/schools/kennesaw-state/"
        }

        logger.info("News Monitor initialized")

    def fetch_rss_feeds(self) -> List[Dict]:
        """Fetch latest news from RSS feeds"""
        all_news = []

        for source_name, feed_url in self.news_sources.items():
            try:
                logger.info(f"Fetching RSS feed: {source_name}")
                feed = feedparser.parse(feed_url)

                for entry in feed.entries[:10]:  # Get last 10 items
                    news_item = {
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "summary": entry.get("summary", ""),
                        "source": source_name
                    }

                    # Filter for KSU-related content
                    if self._is_ksu_related(news_item):
                        all_news.append(news_item)

                logger.info(f"Found {len([n for n in all_news if n['source'] == source_name])} KSU-related items from {source_name}")

            except Exception as e:
                logger.error(f"Error fetching {source_name}: {e}")
                continue

        return all_news

    def _is_ksu_related(self, news_item: Dict) -> bool:
        """Check if news item is related to KSU"""
        ksu_keywords = [
            "kennesaw", "ksu", "owls", "milton overton",
            "kennesaw state", "ksuowls"
        ]

        text = f"{news_item['title']} {news_item.get('summary', '')}".lower()

        return any(keyword in text for keyword in ksu_keywords)

    def analyze_sentiment(self, news_item: Dict) -> Dict:
        """
        Analyze sentiment and newsworthiness of a news item

        Returns:
            {
                "sentiment": "positive" | "negative" | "neutral",
                "priority": 1-10 (10 = most newsworthy),
                "post_worthy": bool,
                "reasoning": str
            }
        """
        try:
            prompt = f"""Analyze this KSU Athletics news item:

Title: {news_item['title']}
Summary: {news_item.get('summary', 'N/A')}

Provide:
1. Sentiment (positive/negative/neutral)
2. Priority score (1-10, where 10 = urgent/important news worth posting about immediately)
3. Is this worth posting about? (yes/no)
4. Brief reasoning (1 sentence)

Examples:
- "KSU wins championship" = positive, priority 10, yes, major achievement
- "Player injured" = negative, priority 7, yes if starter, newsworthy
- "Practice schedule change" = neutral, priority 2, no, internal matter
- "New recruit commitment" = positive, priority 8-9, yes, excellent content
- "Coach interview" = positive, priority 5-6, maybe, depends on content

Format your response as JSON:
{{
  "sentiment": "positive|negative|neutral",
  "priority": 1-10,
  "post_worthy": true|false,
  "reasoning": "brief explanation"
}}"""

            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            analysis = json.loads(response.content[0].text.strip())

            return analysis

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                "sentiment": "neutral",
                "priority": 5,
                "post_worthy": False,
                "reasoning": "Analysis failed"
            }

    def generate_post_suggestion(
        self,
        news_item: Dict,
        voice_type: str = "personal"
    ) -> Optional[Dict]:
        """
        Generate a social media post suggestion based on news

        Args:
            news_item: News article data
            voice_type: "personal" or "coach"

        Returns:
            {
                "content": str (suggested post text),
                "scenario": str (scenario type),
                "context": str (additional context),
                "media_suggestion": str (suggestion for graphics/video)
            }
        """
        try:
            if voice_type == "personal":
                prompt = f"""You are Milton Overton, Athletic Director at Kennesaw State University.

Generate a PERSONAL LinkedIn post (20-80 words) reacting to this news:

Title: {news_item['title']}
Summary: {news_item.get('summary', '')}
Source: {news_item.get('link', '')}

Guidelines:
- Use warm, supportive, celebratory tone
- Keep it brief (20-80 words)
- End with "Let's Go Owls!"
- Be authentic to Milton's voice
- Focus on student-athlete success or program growth

Write ONLY the LinkedIn post. No explanations."""

            else:  # coach voice
                prompt = f"""You are Milton Overton, Athletic Director at Kennesaw State University.

Generate a COACH-STYLE motivational post (50-100 words) reacting to this news:

Title: {news_item['title']}
Summary: {news_item.get('summary', '')}
Source: {news_item.get('link', '')}

Guidelines:
- Use motivational, leadership tone
- Emphasize values, character, teamwork
- Celebrate success or rally after setbacks
- 50-100 words
- End with "Let's Go Owls!"

Write ONLY the post. No explanations."""

            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            suggested_post = response.content[0].text.strip()

            # Determine scenario based on news content
            scenario = self._determine_scenario(news_item)

            # Media suggestion
            media_suggestion = self._suggest_media(news_item)

            return {
                "content": suggested_post,
                "scenario": scenario,
                "context": f"{news_item['title']} - {news_item.get('link', '')}",
                "media_suggestion": media_suggestion,
                "news_item": news_item
            }

        except Exception as e:
            logger.error(f"Post generation failed: {e}")
            return None

    def _determine_scenario(self, news_item: Dict) -> str:
        """Determine the best scenario category for this news"""
        title = news_item['title'].lower()
        summary = news_item.get('summary', '').lower()
        text = f"{title} {summary}"

        if any(word in text for word in ["win", "victory", "champion", "defeat"]):
            return "game_highlights"
        elif any(word in text for word in ["recruit", "commit", "sign"]):
            return "recruiting_update"
        elif any(word in text for word in ["partner", "sponsor", "donation"]):
            return "partner_appreciation"
        elif any(word in text for word in ["scholar", "academic", "dean", "gpa"]):
            return "academic_achievement"
        elif any(word in text for word in ["award", "honor", "recognize"]):
            return "award_announcement"
        elif any(word in text for word in ["hire", "coach", "staff"]):
            return "hiring_announcement"
        else:
            return "general_announcement"

    def _suggest_media(self, news_item: Dict) -> str:
        """Suggest what type of media would work well"""
        title = news_item['title'].lower()

        if any(word in title for word in ["win", "victory", "champion"]):
            return "Action photo or game highlights video"
        elif any(word in title for word in ["recruit", "commit"]):
            return "Player photo with KSU uniform template"
        elif "partner" in title:
            return "Branded graphic with partner logo"
        else:
            return "KSU branded graphic with key quote"

    def monitor_and_suggest(
        self,
        hours_back: int = 24,
        min_priority: int = 7
    ) -> List[Dict]:
        """
        Main monitoring function - fetch news and generate suggestions

        Args:
            hours_back: How many hours back to check (default 24)
            min_priority: Minimum priority score to generate suggestions (1-10)

        Returns:
            List of post suggestions sorted by priority
        """
        logger.info(f"Monitoring news from last {hours_back} hours...")

        # Fetch all news
        all_news = self.fetch_rss_feeds()
        logger.info(f"Found {len(all_news)} total news items")

        suggestions = []

        for news_item in all_news:
            # Analyze sentiment and newsworthiness
            analysis = self.analyze_sentiment(news_item)

            if not analysis["post_worthy"] or analysis["priority"] < min_priority:
                logger.info(f"Skipping (priority {analysis['priority']}): {news_item['title']}")
                continue

            # Generate post suggestion
            logger.info(f"Generating suggestion (priority {analysis['priority']}): {news_item['title']}")

            suggestion = self.generate_post_suggestion(news_item, voice_type="personal")

            if suggestion:
                suggestion["analysis"] = analysis
                suggestion["priority"] = analysis["priority"]
                suggestions.append(suggestion)

        # Sort by priority (highest first)
        suggestions.sort(key=lambda x: x["priority"], reverse=True)

        logger.info(f"Generated {len(suggestions)} post suggestions")

        return suggestions


def main():
    """Test news monitoring"""
    monitor = NewsMonitor()

    print("="*70)
    print("KSU ATHLETICS NEWS MONITOR - TEST RUN")
    print("="*70)

    suggestions = monitor.monitor_and_suggest(hours_back=168, min_priority=6)  # Last week, priority 6+

    print(f"\nFound {len(suggestions)} post-worthy news items:\n")

    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n[{i}] Priority: {suggestion['priority']}/10")
        print(f"Headline: {suggestion['news_item']['title']}")
        print(f"Sentiment: {suggestion['analysis']['sentiment'].upper()}")
        print(f"Scenario: {suggestion['scenario']}")
        print(f"\nSuggested Post:")
        print(f"{suggestion['content']}")
        print(f"\nMedia Suggestion: {suggestion['media_suggestion']}")
        print(f"Source: {suggestion['news_item']['link']}")
        print("-"*70)


if __name__ == "__main__":
    main()
