"""
Media Monitor - Module I
Continuous monitoring of college sports and tech news sources
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import feedparser
from dataclasses import dataclass, asdict
import re
import asyncpg
import os
from dotenv import load_dotenv

@dataclass
class NewsArticle:
    """Structured news article data"""
    title: str
    url: str
    source: str
    published_date: datetime
    content: str
    summary: Optional[str] = None
    categories: List[str] = None
    relevance_score: float = 0.0
    key_entities: List[str] = None

    def __post_init__(self):
        if self.categories is None:
            self.categories = []
        if self.key_entities is None:
            self.key_entities = []

class MediaMonitor:
    """
    Continuous monitoring of college sports and tech news sources

    Sources:
    - NCAA.org
    - D3Ticker.com (Division III specific)
    - Sports Business Journal
    - TechCrunch AI
    - VentureBeat AI
    - Chronicle of Higher Education
    """

    def __init__(self, db_url: str):
        """
        Initialize Media Monitor

        Args:
            db_url: PostgreSQL connection URL
        """
        self.db_url = db_url
        self.db_pool = None

        # Configure news sources
        self.sources = {
            "ncaa": {
                "url": "https://www.ncaa.org/news",
                "rss": "https://www.ncaa.org/news/rss.xml",
                "type": "rss",
                "authority_weight": 1.0
            },
            "d3ticker": {
                "url": "https://d3ticker.com/feed/",
                "type": "rss",
                "authority_weight": 0.9
            },
            "sbj": {
                "url": "https://www.sportsbusinessjournal.com/Daily/Issues.aspx",
                "type": "scrape",
                "authority_weight": 1.0
            },
            "techcrunch_ai": {
                "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
                "type": "rss",
                "authority_weight": 0.7
            },
            "venturebeat_ai": {
                "url": "https://venturebeat.com/category/ai/feed/",
                "type": "rss",
                "authority_weight": 0.7
            },
            "chronicle": {
                "url": "https://www.chronicle.com/section/athletics/61",
                "type": "scrape",
                "authority_weight": 0.8
            }
        }

        # Keywords for relevance filtering
        self.keywords = [
            # Core topics
            "NIL", "name image likeness",
            "conference realignment", "athletic director",
            "college sports technology", "fan engagement",
            "donor management", "AI in sports", "sports analytics",
            "NCAA Division III", "D3", "DIII",
            "athletic fundraising", "athletic revenue",

            # Technology trends
            "artificial intelligence", "machine learning",
            "data analytics", "CRM", "donor relations",
            "digital transformation", "innovation",

            # Leadership
            "athletic leadership", "sports administration",
            "strategic planning", "organizational change",

            # Future trends
            "future of college sports", "sports business",
            "NCAA reform", "athlete compensation"
        ]

    async def initialize(self):
        """Initialize database connection pool"""
        self.db_pool = await asyncpg.create_pool(self.db_url, min_size=2, max_size=10)

    async def close(self):
        """Close database connection pool"""
        if self.db_pool:
            await self.db_pool.close()

    async def monitor_continuous(self, interval_minutes: int = 30):
        """
        Continuous monitoring loop

        Args:
            interval_minutes: Check interval (default 30 min)
        """
        print(f"[MediaMonitor] Starting continuous monitoring (interval: {interval_minutes} min)")

        while True:
            try:
                print(f"[MediaMonitor] Fetching articles at {datetime.utcnow().isoformat()}")

                # Fetch all sources
                articles = await self.fetch_all_sources()
                print(f"[MediaMonitor] Fetched {len(articles)} total articles")

                # Filter for relevance
                relevant_articles = self.filter_relevant(articles)
                print(f"[MediaMonitor] {len(relevant_articles)} relevant articles found")

                # Process and store
                await self.process_articles(relevant_articles)

                print(f"[MediaMonitor] Sleeping for {interval_minutes} minutes")
                await asyncio.sleep(interval_minutes * 60)

            except Exception as e:
                print(f"[MediaMonitor] ERROR: {e}")
                await asyncio.sleep(60)  # Retry after 1 min on error

    async def fetch_all_sources(self) -> List[NewsArticle]:
        """Fetch articles from all configured sources"""
        articles = []

        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_source(source_name, source_config, session)
                for source_name, source_config in self.sources.items()
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, list):
                    articles.extend(result)
                elif isinstance(result, Exception):
                    print(f"[MediaMonitor] Source fetch error: {result}")

        return articles

    async def fetch_source(
        self,
        source_name: str,
        config: dict,
        session: aiohttp.ClientSession
    ) -> List[NewsArticle]:
        """Fetch articles from a single source"""

        try:
            if config["type"] == "rss":
                return await self.fetch_rss(source_name, config.get("rss", config.get("url")))
            elif config["type"] == "scrape":
                return await self.fetch_scrape(source_name, config["url"], session)
        except Exception as e:
            print(f"[MediaMonitor] Error fetching {source_name}: {e}")

        return []

    async def fetch_rss(self, source_name: str, url: str) -> List[NewsArticle]:
        """Fetch RSS feed"""
        try:
            # Run feedparser in executor to avoid blocking
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, url)

            articles = []

            for entry in feed.entries[:20]:  # Latest 20
                article = NewsArticle(
                    title=entry.get('title', 'Untitled'),
                    url=entry.get('link', ''),
                    source=source_name,
                    published_date=self._parse_date(entry.get("published", "")),
                    content=self._clean_html(entry.get("summary", entry.get("description", ""))),
                    categories=self._extract_categories(entry),
                    relevance_score=0.0,
                    key_entities=[]
                )
                articles.append(article)

            return articles

        except Exception as e:
            print(f"[MediaMonitor] RSS fetch error for {source_name}: {e}")
            return []

    async def fetch_scrape(
        self,
        source_name: str,
        url: str,
        session: aiohttp.ClientSession
    ) -> List[NewsArticle]:
        """Scrape articles from website"""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    print(f"[MediaMonitor] HTTP {response.status} for {source_name}")
                    return []

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Custom scraping logic per source
                if source_name == "sbj":
                    return self._scrape_sbj(soup)
                elif source_name == "chronicle":
                    return self._scrape_chronicle(soup)

                return []

        except Exception as e:
            print(f"[MediaMonitor] Scrape error for {source_name}: {e}")
            return []

    def filter_relevant(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        Filter articles by relevance to Milton's thought leadership pillars

        Scoring criteria:
        - Keyword matches (40%)
        - Publication recency (30%)
        - Source authority (30%)
        """
        relevant = []

        for article in articles:
            score = self._calculate_relevance_score(article)
            article.relevance_score = score

            if score >= float(os.getenv("MIN_ARTICLE_RELEVANCE", "0.6")):
                relevant.append(article)

        # Sort by relevance
        relevant.sort(key=lambda x: x.relevance_score, reverse=True)

        return relevant[:10]  # Top 10 most relevant

    def _calculate_relevance_score(self, article: NewsArticle) -> float:
        """Calculate relevance score (0-1)"""
        score = 0.0
        text = f"{article.title} {article.content}".lower()

        # Keyword matching (40% of score)
        keyword_matches = sum(1 for kw in self.keywords if kw.lower() in text)
        score += (keyword_matches / len(self.keywords)) * 0.4

        # Recency (30% of score)
        days_old = (datetime.utcnow() - article.published_date).days
        recency_score = max(0, 1 - (days_old / 30))  # Decay over 30 days
        score += recency_score * 0.3

        # Source authority (30% of score)
        source_config = self.sources.get(article.source, {})
        authority_weight = source_config.get("authority_weight", 0.5)
        score += authority_weight * 0.3

        return min(score, 1.0)

    async def process_articles(self, articles: List[NewsArticle]):
        """Process relevant articles for content opportunities"""
        for article in articles:
            # Extract key entities (simplified - would use spaCy in production)
            article.key_entities = self._extract_entities(article)

            # Store in database
            await self._store_article(article)

            # Create content opportunity
            await self._create_content_opportunity(article)

    async def _store_article(self, article: NewsArticle):
        """Store article in database"""
        async with self.db_pool.acquire() as conn:
            try:
                await conn.execute("""
                    INSERT INTO news_articles (
                        title, url, source, published_date, content,
                        categories, relevance_score, key_entities
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (url) DO UPDATE SET
                        relevance_score = EXCLUDED.relevance_score,
                        updated_at = NOW()
                """,
                    article.title,
                    article.url,
                    article.source,
                    article.published_date,
                    article.content,
                    article.categories,
                    article.relevance_score,
                    article.key_entities
                )
            except Exception as e:
                print(f"[MediaMonitor] Database error storing article: {e}")

    async def _create_content_opportunity(self, article: NewsArticle):
        """Create content opportunity for Module II"""
        async with self.db_pool.acquire() as conn:
            # Get article_id
            row = await conn.fetchrow("SELECT article_id FROM news_articles WHERE url = $1", article.url)
            if not row:
                return

            article_id = row['article_id']

            # Determine urgency
            urgency = self._assess_urgency(article)

            # Map to pillars
            pillars = self._map_to_pillars(article)

            # Suggest angle
            angle = self._suggest_content_angle(article)

            try:
                await conn.execute("""
                    INSERT INTO content_opportunities (
                        type, article_id, suggested_angle, urgency,
                        pillar_alignment, target_platforms, status
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                    "news_reaction",
                    article_id,
                    angle,
                    urgency,
                    pillars,
                    ['linkedin'],  # Default to LinkedIn
                    'pending'
                )
            except Exception as e:
                print(f"[MediaMonitor] Database error creating opportunity: {e}")

    def _suggest_content_angle(self, article: NewsArticle) -> str:
        """Suggest how Milton should respond to this news"""
        text = f"{article.title} {article.content}".lower()

        if "nil" in text or "name image likeness" in text:
            return "Connect NIL trends to AI-driven donor management opportunities"
        elif any(tech in text for tech in ["ai", "artificial intelligence", "technology", "innovation"]):
            return "Position as validation of AI-first approach at Keuka College"
        elif "athletic director" in text or "leadership" in text:
            return "Share executive perspective on leadership in modern college athletics"
        elif "conference" in text or "realignment" in text:
            return "Analyze implications for Division III programs and strategic positioning"
        else:
            return "Provide executive perspective on implications for college athletics"

    def _map_to_pillars(self, article: NewsArticle) -> List[str]:
        """Map article to Milton's thought leadership pillars"""
        pillars = []
        text = f"{article.title} {article.content}".lower()

        if any(word in text for word in ["ai", "technology", "innovation", "data", "analytics"]):
            pillars.append("AI Innovation in Sports Business")

        if any(word in text for word in ["leadership", "strategy", "management", "director", "vision"]):
            pillars.append("Leadership & Vision")

        if any(word in text for word in ["nil", "conference", "future", "trend", "reform"]):
            pillars.append("Future of College Sports")

        return pillars if pillars else ["Leadership & Vision"]  # Default pillar

    def _assess_urgency(self, article: NewsArticle) -> str:
        """Assess content urgency"""
        hours_old = (datetime.utcnow() - article.published_date).total_seconds() / 3600

        if article.relevance_score >= 0.9 and hours_old < 6:
            return "immediate"  # Breaking news, highly relevant
        elif article.relevance_score >= 0.8 and hours_old < 24:
            return "today"
        elif article.relevance_score >= 0.7 and hours_old < 72:
            return "this_week"
        else:
            return "standard"

    # Helper methods
    def _parse_date(self, date_str: str) -> datetime:
        """Parse various date formats"""
        if not date_str:
            return datetime.utcnow()

        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            return datetime.utcnow()

    def _clean_html(self, html: str) -> str:
        """Remove HTML tags"""
        if not html:
            return ""
        return BeautifulSoup(html, 'html.parser').get_text().strip()

    def _extract_categories(self, entry: dict) -> List[str]:
        """Extract RSS categories"""
        return [tag.get('term', '') for tag in entry.get("tags", [])]

    def _extract_entities(self, article: NewsArticle) -> List[str]:
        """Extract named entities (simplified - use spaCy for production)"""
        # Placeholder - would use spaCy NER in production
        entities = []

        # Simple regex for organization names (capitalized words)
        text = f"{article.title} {article.content}"
        matches = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)
        entities.extend(list(set(matches))[:10])  # Top 10 unique

        return entities

    def _scrape_sbj(self, soup: BeautifulSoup) -> List[NewsArticle]:
        """Sports Business Journal scraping logic"""
        # Simplified - implement based on actual site structure
        articles = []
        # TODO: Implement actual scraping logic
        return articles

    def _scrape_chronicle(self, soup: BeautifulSoup) -> List[NewsArticle]:
        """Chronicle of Higher Education scraping logic"""
        # Simplified - implement based on actual site structure
        articles = []
        # TODO: Implement actual scraping logic
        return articles


# Standalone execution
async def main():
    load_dotenv()

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return

    interval = int(os.getenv("MEDIA_MONITORING_INTERVAL", "30"))

    monitor = MediaMonitor(db_url=db_url)
    await monitor.initialize()

    try:
        await monitor.monitor_continuous(interval_minutes=interval)
    except KeyboardInterrupt:
        print("\n[MediaMonitor] Shutting down...")
    finally:
        await monitor.close()


if __name__ == "__main__":
    asyncio.run(main())
