"""
Insight Synthesis Engine - Module I
Combines Milton's raw insights with trending news to create content opportunities
"""

from typing import List, Dict, Optional
from anthropic import Anthropic
import json
import asyncpg
import os
from datetime import datetime
from dataclasses import dataclass

@dataclass
class NewsArticle:
    """News article data structure"""
    article_id: int
    title: str
    url: str
    source: str
    published_date: datetime
    content: str
    relevance_score: float
    categories: List[str]

class InsightSynthesizer:
    """
    Combines Milton's raw insights with trending news
    to create high-value content opportunities
    """

    def __init__(self, anthropic_api_key: str, db_url: str):
        """
        Initialize Insight Synthesizer

        Args:
            anthropic_api_key: Anthropic API key for Claude
            db_url: PostgreSQL connection URL
        """
        self.client = Anthropic(api_key=anthropic_api_key)
        self.db_url = db_url
        self.db_pool = None
        self.voice_profile = {}

    async def initialize(self):
        """Initialize database connection and load voice profile"""
        self.db_pool = await asyncpg.create_pool(self.db_url, min_size=2, max_size=10)
        self.voice_profile = await self._load_voice_profile()

    async def close(self):
        """Close database connection"""
        if self.db_pool:
            await self.db_pool.close()

    async def synthesize_insight(
        self,
        executive_insight: str,
        insight_id: str,
        related_articles: List[NewsArticle],
        pillar: str
    ) -> Dict:
        """
        Synthesize Milton's insight with current trends

        Args:
            executive_insight: Milton's raw input
            insight_id: Database ID of the insight
            related_articles: Relevant news articles
            pillar: Target thought leadership pillar

        Returns:
            Structured content opportunity
        """
        print(f"[InsightSynthesizer] Synthesizing insight {insight_id} with {len(related_articles)} articles")

        # Build context for Claude
        context = self._build_synthesis_context(
            executive_insight,
            related_articles,
            pillar
        )

        # Use Claude to synthesize
        synthesis = await self._claude_synthesize(context)

        # Structure the opportunity
        opportunity = {
            "original_insight": executive_insight,
            "insight_id": insight_id,
            "news_hooks": [
                {
                    "article_id": article.article_id,
                    "article_title": article.title,
                    "article_url": article.url,
                    "connection_angle": self._extract_connection(synthesis, article)
                }
                for article in related_articles[:3]  # Top 3 articles
            ],
            "content_angles": synthesis.get("content_angles", []),
            "recommended_format": synthesis.get("format", "linkedin_long"),
            "target_platforms": synthesis.get("platforms", ["linkedin"]),
            "draft_outline": synthesis.get("outline", ""),
            "call_to_action": synthesis.get("cta", ""),
            "visual_suggestions": synthesis.get("visuals", []),
            "urgency_score": synthesis.get("urgency", 0.5),
            "pillar_alignment": pillar
        }

        # Store in database as content opportunity
        await self._create_content_opportunity(opportunity)

        return opportunity

    async def process_pending_insights(self):
        """
        Process all pending insights that need synthesis

        This is called by a background worker or scheduler
        """
        print("[InsightSynthesizer] Processing pending insights...")

        async with self.db_pool.acquire() as conn:
            # Get unprocessed insights
            insights = await conn.fetch("""
                SELECT insight_id, raw_content, priority
                FROM executive_insights
                WHERE processed = FALSE
                AND processing_started_at IS NOT NULL
                ORDER BY
                    CASE priority
                        WHEN 'urgent' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        ELSE 4
                    END,
                    timestamp DESC
                LIMIT 10
            """)

            for insight in insights:
                try:
                    # Find related articles
                    articles = await self._find_related_articles(insight['raw_content'])

                    if articles:
                        # Determine best pillar
                        pillar = await self._determine_pillar(insight['raw_content'], articles)

                        # Synthesize
                        await self.synthesize_insight(
                            executive_insight=insight['raw_content'],
                            insight_id=insight['insight_id'],
                            related_articles=articles,
                            pillar=pillar
                        )

                    # Mark as processed
                    await conn.execute("""
                        UPDATE executive_insights
                        SET processed = TRUE,
                            processing_completed_at = NOW()
                        WHERE insight_id = $1
                    """, insight['insight_id'])

                    print(f"[InsightSynthesizer] Processed insight {insight['insight_id']}")

                except Exception as e:
                    print(f"[InsightSynthesizer] Error processing {insight['insight_id']}: {e}")

    def _build_synthesis_context(
        self,
        insight: str,
        articles: List[NewsArticle],
        pillar: str
    ) -> str:
        """Build comprehensive context for Claude"""

        articles_summary = "\n\n".join([
            f"**Article {i+1}:** {article.title}\n"
            f"Source: {article.source}\n"
            f"Key points: {article.content[:300]}...\n"
            f"URL: {article.url}"
            for i, article in enumerate(articles[:3])
        ])

        voice_tone = self.voice_profile.get('primary_tone', 'visionary_strategic_approachable')
        avg_sentence_length = self.voice_profile.get('avg_sentence_length', 18)
        question_ratio = self.voice_profile.get('question_ratio', 0.15)

        context = f"""You are synthesizing content for Milton Overton, Athletic Director at Keuka College.

**Milton's Thought Leadership Pillar:** {pillar}

**Milton's Raw Insight:**
{insight}

**Related Current News:**
{articles_summary}

**Milton's Voice Profile:**
- Tone: {voice_tone}
- Perspective: AI Innovation + Executive Leadership
- Style: 80% strategic insights, 20% personal stories
- Avg sentence length: ~{avg_sentence_length} words
- Uses questions: {question_ratio*100:.0f}% of the time
- Avoids: Generic AI speak, jargon without context
- Embraces: Data-driven insights, specific examples, forward-thinking perspective

**Milton's Positioning:**
- THE AI innovator in college sports
- Built KSU Donor Fund AI system (practical AI implementation)
- Uses AI avatar (HeyGen/Synthesia) for donor outreach
- Targeting Power Four AD opportunities
- Thought leader at intersection of AI + College Sports

**Task:**
Synthesize Milton's insight with the current news to create compelling thought leadership content.
Identify the strongest content angles that position him as an AI innovator in college sports.

Return JSON with:
- content_angles: [List of 3-5 compelling angles, each 1-2 sentences]
- format: "linkedin_long" | "twitter_thread" | "avatar_video" | "article"
- platforms: [List of target platforms: "linkedin", "twitter", "instagram"]
- outline: Detailed content outline (5-7 bullet points)
- cta: Suggested call-to-action (engaging question or invitation)
- visuals: [List of 2-3 visual content suggestions]
- urgency: Score 0-1 for time-sensitivity (1 = post today, 0 = evergreen)

Format your response as valid JSON."""

        return context

    async def _claude_synthesize(self, context: str) -> Dict:
        """Use Claude API for synthesis"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": context
                    }
                ]
            )

            # Parse JSON response
            response_text = message.content[0].text

            # Extract JSON (handle markdown code blocks)
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text

            return json.loads(json_str)

        except json.JSONDecodeError as e:
            print(f"[InsightSynthesizer] JSON decode error: {e}")
            print(f"Response text: {response_text}")
            # Return default structure
            return {
                "content_angles": ["Discuss the implications of this trend for college athletics"],
                "format": "linkedin_long",
                "platforms": ["linkedin"],
                "outline": ["Introduction", "Key insight", "Industry implications", "Call to action"],
                "cta": "What's your take on this trend?",
                "visuals": ["Professional headshot"],
                "urgency": 0.5
            }
        except Exception as e:
            print(f"[InsightSynthesizer] Claude API error: {e}")
            raise

    async def _find_related_articles(self, insight_text: str, limit: int = 5) -> List[NewsArticle]:
        """
        Find news articles related to the insight

        Args:
            insight_text: The executive insight text
            limit: Maximum articles to return

        Returns:
            List of related NewsArticle objects
        """
        async with self.db_pool.acquire() as conn:
            # Simple keyword matching (would use vector similarity in production)
            # Extract keywords from insight
            keywords = self._extract_keywords(insight_text)

            if not keywords:
                # Fallback: get most recent relevant articles
                rows = await conn.fetch("""
                    SELECT article_id, title, url, source, published_date,
                           content, relevance_score, categories
                    FROM news_articles
                    WHERE processed = FALSE
                    ORDER BY relevance_score DESC, published_date DESC
                    LIMIT $1
                """, limit)
            else:
                # Match articles containing keywords
                keyword_pattern = '|'.join(keywords)
                rows = await conn.fetch("""
                    SELECT article_id, title, url, source, published_date,
                           content, relevance_score, categories
                    FROM news_articles
                    WHERE (title ~* $1 OR content ~* $1)
                    AND processed = FALSE
                    ORDER BY relevance_score DESC, published_date DESC
                    LIMIT $2
                """, keyword_pattern, limit)

            articles = []
            for row in rows:
                articles.append(NewsArticle(
                    article_id=row['article_id'],
                    title=row['title'],
                    url=row['url'],
                    source=row['source'],
                    published_date=row['published_date'],
                    content=row['content'] or "",
                    relevance_score=float(row['relevance_score']),
                    categories=row['categories'] or []
                ))

            return articles

    async def _determine_pillar(self, insight_text: str, articles: List[NewsArticle]) -> str:
        """Determine which thought leadership pillar this content aligns with"""

        text = f"{insight_text} {' '.join([a.title for a in articles])}".lower()

        pillar_scores = {
            "AI Innovation in Sports Business": 0,
            "Leadership & Vision": 0,
            "Future of College Sports": 0
        }

        # AI Innovation keywords
        if any(word in text for word in ["ai", "artificial intelligence", "technology", "innovation", "data", "analytics", "automation", "digital"]):
            pillar_scores["AI Innovation in Sports Business"] += 2

        # Leadership keywords
        if any(word in text for word in ["leadership", "strategy", "management", "director", "vision", "execution", "team", "organizational"]):
            pillar_scores["Leadership & Vision"] += 2

        # Future of Sports keywords
        if any(word in text for word in ["nil", "conference", "realignment", "future", "trend", "evolution", "reform", "ncaa"]):
            pillar_scores["Future of College Sports"] += 2

        # Return highest scoring pillar
        best_pillar = max(pillar_scores.items(), key=lambda x: x[1])[0]

        # Default to Leadership if all scores are 0
        return best_pillar if pillar_scores[best_pillar] > 0 else "Leadership & Vision"

    def _extract_connection(self, synthesis: Dict, article: NewsArticle) -> str:
        """Extract the connection angle between insight and article"""
        for angle in synthesis.get("content_angles", []):
            # Simple matching - check if article title keywords appear in angle
            title_words = set(article.title.lower().split())
            angle_words = set(angle.lower().split())
            if len(title_words & angle_words) >= 2:  # At least 2 words in common
                return angle

        # Default: return first angle
        return synthesis.get("content_angles", ["General industry analysis"])[0]

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text (simplified)"""
        # In production, use spaCy or KeyBERT
        # For now, simple word extraction
        import re

        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are', 'was', 'were'}

        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        keywords = [w for w in words if w not in stop_words]

        # Return top 5 most frequent
        from collections import Counter
        return [word for word, count in Counter(keywords).most_common(5)]

    async def _create_content_opportunity(self, opportunity: Dict):
        """Store content opportunity in database"""
        async with self.db_pool.acquire() as conn:
            try:
                # Determine if there's an article_id
                article_id = None
                if opportunity['news_hooks'] and len(opportunity['news_hooks']) > 0:
                    article_id = opportunity['news_hooks'][0]['article_id']

                await conn.execute("""
                    INSERT INTO content_opportunities (
                        type, insight_id, article_id, suggested_angle,
                        urgency, pillar_alignment, target_platforms,
                        status, metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                    'insight_expansion',
                    opportunity['insight_id'],
                    article_id,
                    opportunity['content_angles'][0] if opportunity['content_angles'] else "General analysis",
                    'today' if opportunity['urgency_score'] > 0.7 else 'this_week',
                    [opportunity['pillar_alignment']],
                    opportunity['target_platforms'],
                    'pending',
                    json.dumps({
                        'content_angles': opportunity['content_angles'],
                        'recommended_format': opportunity['recommended_format'],
                        'draft_outline': opportunity['draft_outline'],
                        'cta': opportunity['call_to_action'],
                        'visual_suggestions': opportunity['visual_suggestions'],
                        'news_hooks': opportunity['news_hooks']
                    })
                )

                print(f"[InsightSynthesizer] Created content opportunity for insight {opportunity['insight_id']}")

            except Exception as e:
                print(f"[InsightSynthesizer] Error creating opportunity: {e}")

    async def _load_voice_profile(self) -> Dict:
        """Load Milton's voice profile from database"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT primary_tone, avg_sentence_length, question_ratio,
                       storytelling_ratio, formality_level
                FROM voice_profile
                WHERE is_active = TRUE
                ORDER BY training_date DESC
                LIMIT 1
            """)

            if row:
                return {
                    'primary_tone': row['primary_tone'],
                    'avg_sentence_length': float(row['avg_sentence_length']) if row['avg_sentence_length'] else 18.0,
                    'question_ratio': float(row['question_ratio']) if row['question_ratio'] else 0.15,
                    'storytelling_ratio': float(row['storytelling_ratio']) if row['storytelling_ratio'] else 0.20,
                    'formality_level': row['formality_level']
                }
            else:
                # Default profile
                return {
                    'primary_tone': 'visionary_strategic_approachable',
                    'avg_sentence_length': 18.0,
                    'question_ratio': 0.15,
                    'storytelling_ratio': 0.20,
                    'formality_level': 'professional_accessible'
                }


# Standalone execution (background worker)
async def main():
    from dotenv import load_dotenv
    load_dotenv()

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    db_url = os.getenv("DATABASE_URL")

    if not anthropic_key or not db_url:
        print("ERROR: Missing required environment variables (ANTHROPIC_API_KEY, DATABASE_URL)")
        return

    synthesizer = InsightSynthesizer(anthropic_api_key=anthropic_key, db_url=db_url)
    await synthesizer.initialize()

    print("[InsightSynthesizer] Starting background worker...")

    try:
        # Run continuously
        import asyncio
        while True:
            await synthesizer.process_pending_insights()
            await asyncio.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n[InsightSynthesizer] Shutting down...")
    finally:
        await synthesizer.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
