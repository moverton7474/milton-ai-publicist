"""
Content Generator - Module II
Multi-platform content generation maintaining Milton's authentic voice
"""

from anthropic import Anthropic
from typing import Dict, List, Optional
import json
from datetime import datetime, timedelta
import asyncpg
import os


class ContentGenerator:
    """
    Multi-platform content generation maintaining Milton's authentic voice

    Platforms:
    - LinkedIn (primary): 300-500 word thought leadership
    - Twitter/X: Punchy threads (3-5 tweets)
    - Instagram: Visual-first captions
    """

    def __init__(self, anthropic_api_key: str, db_url: str):
        """
        Initialize Content Generator

        Args:
            anthropic_api_key: Anthropic API key
            db_url: PostgreSQL connection URL
        """
        self.client = Anthropic(api_key=anthropic_api_key)
        self.db_url = db_url
        self.db_pool = None
        self.voice_profile = {}
        self.linkedin_best_practices = self._load_linkedin_bp()
        self.twitter_best_practices = self._load_twitter_bp()

    async def initialize(self):
        """Initialize database connection and load voice profile"""
        self.db_pool = await asyncpg.create_pool(self.db_url, min_size=2, max_size=10)
        self.voice_profile = await self._load_voice_profile()

    async def close(self):
        """Close database connection"""
        if self.db_pool:
            await self.db_pool.close()

    async def generate_linkedin_post(
        self,
        opportunity_id: int,
        target_pillar: str,
        include_personal_story: bool = False
    ) -> Dict:
        """
        Generate LinkedIn thought leadership post

        Specifications:
        - 300-500 words
        - Hook opening (first 2 lines crucial)
        - Clear structure with line breaks
        - 80% strategic insights, 20% personal stories
        - Strong CTA question at end
        - Hashtag strategy (3-5 relevant)

        Args:
            opportunity_id: Content opportunity ID from database
            target_pillar: Thought leadership pillar
            include_personal_story: Include personal anecdote

        Returns:
            Dict with generated content and metadata
        """
        print(f"[ContentGenerator] Generating LinkedIn post for opportunity {opportunity_id}")

        # Load opportunity data
        opportunity = await self._load_opportunity(opportunity_id)

        # Build generation prompt
        prompt = self._build_linkedin_prompt(
            opportunity,
            target_pillar,
            include_personal_story
        )

        # Generate with Claude
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=0.7,
            system=self._build_system_prompt("linkedin"),
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response.content[0].text

        # Post-process for LinkedIn formatting
        formatted_content = self._format_for_linkedin(content)

        # Store in database
        content_id = await self._store_generated_content(
            opportunity_id=opportunity_id,
            platform="linkedin",
            content_type="post",
            content=formatted_content,
            metadata={
                "pillar": target_pillar,
                "include_story": include_personal_story
            }
        )

        return {
            "content_id": content_id,
            "platform": "linkedin",
            "content": formatted_content,
            "character_count": len(formatted_content),
            "word_count": len(formatted_content.split()),
            "hashtags": self._extract_hashtags(formatted_content),
            "mentions": self._suggest_mentions(opportunity),
            "visual_suggestions": self._suggest_visuals_linkedin(opportunity),
            "optimal_post_time": self._calculate_optimal_time("linkedin"),
            "pillar": target_pillar,
            "created_at": datetime.utcnow().isoformat()
        }

    async def generate_twitter_thread(
        self,
        opportunity_id: int,
        linkedin_content: Optional[str] = None
    ) -> Dict:
        """
        Generate Twitter/X thread

        Specifications:
        - 3-5 tweets
        - First tweet is standalone hook
        - Punchy, conversational tone
        - Each tweet <280 characters
        - Ends with link to full LinkedIn post

        Args:
            opportunity_id: Content opportunity ID
            linkedin_content: Optional LinkedIn post to adapt

        Returns:
            Dict with thread and metadata
        """
        print(f"[ContentGenerator] Generating Twitter thread for opportunity {opportunity_id}")

        # Load opportunity
        opportunity = await self._load_opportunity(opportunity_id)

        if linkedin_content:
            # Convert LinkedIn post to thread
            prompt = self._build_twitter_from_linkedin_prompt(linkedin_content, opportunity)
        else:
            # Generate fresh thread
            prompt = self._build_twitter_prompt(opportunity)

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            temperature=0.7,
            system=self._build_system_prompt("twitter"),
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response.content[0].text

        # Parse JSON response
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        else:
            json_str = content

        thread_data = json.loads(json_str)
        tweets = thread_data.get("tweets", [])

        # Store in database
        content_id = await self._store_generated_content(
            opportunity_id=opportunity_id,
            platform="twitter",
            content_type="thread",
            content="\n\n---TWEET---\n\n".join(tweets),
            metadata={"tweet_count": len(tweets), "adapted_from_linkedin": linkedin_content is not None}
        )

        return {
            "content_id": content_id,
            "platform": "twitter",
            "tweets": tweets,
            "tweet_count": len(tweets),
            "total_characters": sum(len(t) for t in tweets),
            "hashtags": self._extract_hashtags(tweets[0]) if tweets else [],
            "optimal_post_time": self._calculate_optimal_time("twitter"),
            "created_at": datetime.utcnow().isoformat()
        }

    async def generate_avatar_script(
        self,
        purpose: str,
        key_message: str,
        duration_seconds: int = 60,
        style: str = "professional"
    ) -> Dict:
        """
        Generate script for HeyGen/Synthesia avatar video

        Use cases:
        - KSU Donor Fund promotion
        - Event announcements
        - AI innovation showcases
        - Thought leadership snippets

        Args:
            purpose: Purpose of video
            key_message: Core message to convey
            duration_seconds: Target duration (30, 60, or 90)
            style: professional | inspirational | educational

        Returns:
            Dict with script and metadata
        """
        words_per_second = 2.5
        target_words = int(duration_seconds * words_per_second)

        prompt = f"""Generate a video script for Milton Overton's AI avatar (HeyGen/Synthesia).

**Purpose:** {purpose}
**Key Message:** {key_message}
**Target Duration:** {duration_seconds} seconds (~{target_words} words)
**Style:** {style}

**Avatar Context:**
Milton is using an AI avatar to showcase his commitment to AI innovation in college sports.
The use of the avatar ITSELF is part of the message - demonstrating he practices what he preaches.

**Script Requirements:**
- Conversational tone (written for speech, not reading)
- Clear enunciation points
- Natural pauses marked with [PAUSE]
- Emphasize key words in CAPS
- Direct camera address ("you", "we")
- Length: {target_words} ± 20 words
- Include specific CTA

**Milton's Speaking Style:**
- Confident but approachable
- Uses rhetorical questions
- Bridges vision with practical action
- Authentic, not overly scripted

**Structure:**
1. Hook (first 10 seconds): Grab attention
2. Body (middle 40 seconds): Deliver key message
3. Close (last 10 seconds): Strong CTA

Generate the script with clear [PAUSE] markers and emphasis indicators:"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            temperature=0.8,
            system="You are a professional video script writer specializing in executive communication.",
            messages=[{"role": "user", "content": prompt}]
        )

        script = response.content[0].text
        word_count = len(script.split())
        estimated_duration = word_count / words_per_second

        return {
            "platform": "avatar_video",
            "script": script,
            "word_count": word_count,
            "estimated_duration": f"{estimated_duration:.1f} seconds",
            "pause_count": script.count("[PAUSE]"),
            "emphasis_count": len([w for w in script.split() if w.isupper() and len(w) > 2]),
            "visual_suggestions": self._suggest_avatar_visuals(purpose),
            "background_music": self._suggest_background_music(style),
            "created_at": datetime.utcnow().isoformat()
        }

    def _build_linkedin_prompt(
        self,
        opportunity: Dict,
        pillar: str,
        include_story: bool
    ) -> str:
        """Build comprehensive LinkedIn generation prompt"""

        story_instruction = """
Include a brief (2-3 sentence) personal story or specific example from Milton's experience
that illustrates the point. This should feel authentic and grounded, not generic.
Examples: "Last week at Keuka...", "When we launched the KSU Donor Fund...", "I remember when..."
""" if include_story else ""

        prompt = f"""Generate a LinkedIn thought leadership post for Milton Overton, Athletic Director at Keuka College.

**Content Opportunity:**
{json.dumps(opportunity, indent=2, default=str)}

**Target Thought Leadership Pillar:** {pillar}

**Milton's Voice Profile:**
- Tone: {self.voice_profile.get('primary_tone', 'visionary_strategic_approachable')}
- Avg sentence length: ~{self.voice_profile.get('avg_sentence_length', 18)} words
- Question ratio: {self.voice_profile.get('question_ratio', 0.15):.0%}
- Uses data/stats frequently
- Storytelling ratio: {self.voice_profile.get('storytelling_ratio', 0.20):.0%}

**Milton's Key Positioning:**
- THE AI innovator in college sports
- Built KSU Donor Fund AI system (practical AI implementation)
- Uses AI avatar (HeyGen) for donor outreach - walks the talk
- Targeting Power Four AD opportunities
- Thought leader at intersection of AI + College Athletics

**Required Structure:**
1. HOOK (2 lines max): Compelling opening that stops the scroll
   - Must work as standalone (visible before "see more")
   - Should intrigue or challenge conventional thinking

2. CONTEXT (2-3 paragraphs): Explain the issue/trend with Milton's unique perspective
   - What's happening in college sports/AI?
   - Why does it matter NOW?

3. INSIGHT (2-3 paragraphs): Share the strategic insight or innovation angle
   - Milton's unique take/solution
   - Connect to his AI-first approach at Keuka
{story_instruction}

4. CALL-TO-ACTION: End with an engaging question for comments
   - Should invite discussion
   - Relevant to the topic

**LinkedIn Best Practices:**
- First 2 lines MUST hook attention (shows without "see more")
- Use line breaks for readability (every 2-3 sentences)
- Mix of strategic analysis (80%) and human elements (20%)
- Include 3-5 relevant hashtags at the END
- Target length: 300-500 words
- Professional but conversational tone

**Avoid:**
- Generic motivational speak
- Buzzwords without substance
- Overly promotional tone
- Starting with "I'm excited to announce..."
- Generic AI speak ("game-changer", "revolutionary" without proof)

**Embrace:**
- Specific examples and data
- Forward-thinking perspective
- Practical implications
- Milton's authentic voice

Generate the post now (just the post text, no meta-commentary):"""

        return prompt

    def _build_twitter_from_linkedin_prompt(self, linkedin_post: str, opportunity: Dict) -> str:
        """Build prompt to convert LinkedIn post to Twitter thread"""

        return f"""Convert this LinkedIn post into a Twitter/X thread.

**LinkedIn Post:**
{linkedin_post}

**Twitter Thread Requirements:**
- 3-5 tweets total
- Tweet 1: Standalone hook (can work alone)
- Tweets 2-4: Key insights (1 per tweet)
- Final tweet: CTA + "Full thoughts on LinkedIn 👇" + link placeholder
- Each tweet <280 characters
- Maintain Milton's voice but punchier/more conversational
- Use line breaks for emphasis in individual tweets
- Hashtags ONLY in first tweet (2 max)

**Milton's Twitter Tone:**
- Direct and punchy
- Data-driven when possible
- Slightly more casual than LinkedIn but still professional
- Strategic insights, not hot takes
- Confident but not arrogant

Return as JSON array of tweets:
{{"tweets": ["tweet 1 text", "tweet 2 text", ...]}}"""

    def _build_twitter_prompt(self, opportunity: Dict) -> str:
        """Build prompt for fresh Twitter thread"""

        return f"""Generate a Twitter/X thread for Milton Overton, Athletic Director at Keuka College.

**Content Opportunity:**
{json.dumps(opportunity, indent=2, default=str)}

**Thread Requirements:**
- 3-5 tweets
- Tweet 1: Hook that works standalone
- Middle tweets: Core insights
- Final tweet: CTA + link placeholder
- Each <280 characters
- Punchy and conversational
- Professional but more casual than LinkedIn

Return as JSON:
{{"tweets": ["tweet 1", "tweet 2", ...]}}"""

    def _build_system_prompt(self, platform: str) -> str:
        """Build system prompt for content generation"""

        base_prompt = """You are Milton Overton's AI content strategist.

Milton Overton:
- Athletic Director at Keuka College
- AI innovator in college sports
- Built KSU Donor Fund AI system
- Uses AI avatar (HeyGen) for donor outreach
- Positioning for Power Four AD opportunities

Your role:
1. Sound authentically like Milton (not generic AI content)
2. Position him as THE thought leader in AI + college sports
3. Balance visionary thinking with practical executive insights
4. Maintain professionalism while being approachable

Milton's Three Thought Leadership Pillars:
- AI Innovation in Sports Business (The Founder)
- Leadership & Vision (The AD)
- The Future of College Sports (The Futurist)"""

        if platform == "linkedin":
            base_prompt += """

LinkedIn-specific guidelines:
- Professional but engaging tone
- Hook in first 2 lines (critical for "see more" expansion)
- Use strategic line breaks for readability
- End with engaging questions for comments
- Include relevant hashtags (3-5)
- Balance data/insights (80%) with personal stories (20%)
- 300-500 words ideal"""

        elif platform == "twitter":
            base_prompt += """

Twitter-specific guidelines:
- Punchy and direct
- Each tweet <280 characters
- Strategic use of line breaks
- More conversational than LinkedIn
- Lead with value, end with CTA
- Max 2 hashtags in first tweet only"""

        return base_prompt

    def _format_for_linkedin(self, content: str) -> str:
        """Apply LinkedIn-specific formatting"""

        # Ensure line breaks after paragraphs
        paragraphs = content.split("\n\n")
        formatted = "\n\n".join([p.strip() for p in paragraphs if p.strip()])

        # Ensure hashtags at end if not present
        if "#" not in formatted:
            formatted += "\n\n#CollegeSports #AIInnovation #AthleticDirector #HigherEd #SportsLeadership"

        return formatted

    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from content"""
        import re
        return re.findall(r'#\w+', content)

    def _suggest_mentions(self, opportunity: Dict) -> List[str]:
        """Suggest @mentions for engagement"""
        mentions = []

        # Extract from opportunity metadata
        metadata = opportunity.get('metadata', {})
        if isinstance(metadata, str):
            import json
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}

        # Check for NCAA content
        if "NCAA" in str(opportunity):
            mentions.append("@NCAA")

        # Check for D3 content
        if "D3" in str(opportunity) or "Division III" in str(opportunity):
            mentions.append("@D3Ticker")

        return mentions

    def _suggest_visuals_linkedin(self, opportunity: Dict) -> Dict:
        """Suggest visual content for LinkedIn post"""

        suggestions = {
            "primary_visual": "professional_headshot",
            "alternatives": []
        }

        opp_str = str(opportunity).lower()

        # Context-specific suggestions
        if "data" in opp_str or "stats" in opp_str or "analytics" in opp_str:
            suggestions["primary_visual"] = "data_visualization"
            suggestions["alternatives"].append({
                "type": "infographic",
                "description": "Key statistics visualized"
            })

        if "ai" in opp_str or "avatar" in opp_str:
            suggestions["primary_visual"] = "avatar_screenshot"
            suggestions["alternatives"].append({
                "type": "side_by_side",
                "description": "Milton + AI Avatar comparison"
            })

        return suggestions

    def _suggest_avatar_visuals(self, purpose: str) -> List[Dict]:
        """Suggest visual elements for avatar video"""

        base_visuals = [
            {"type": "lower_third", "text": "Milton Overton, Athletic Director"},
            {"type": "background", "style": "professional_office"}
        ]

        if "donor" in purpose.lower():
            base_visuals.append({
                "type": "overlay",
                "element": "KSU Donor Fund logo",
                "timing": "0:15-0:45"
            })

        return base_visuals

    def _suggest_background_music(self, style: str) -> str:
        """Suggest background music for video"""

        music_map = {
            "professional": "subtle_corporate",
            "inspirational": "uplifting_ambient",
            "educational": "neutral_background"
        }

        return music_map.get(style, "subtle_corporate")

    def _calculate_optimal_time(self, platform: str) -> str:
        """Calculate optimal posting time for platform"""

        # Based on research for executive/B2B audiences
        optimal_times = {
            "linkedin": {
                "monday": "09:00",
                "tuesday": "09:00",
                "wednesday": "12:00",
                "thursday": "09:00",
                "friday": "09:00"
            },
            "twitter": {
                "monday": "12:00",
                "tuesday": "12:00",
                "wednesday": "18:00",
                "thursday": "12:00",
                "friday": "12:00"
            }
        }

        # Get next business day
        now = datetime.now()
        next_day = now + timedelta(days=1)
        day_name = next_day.strftime("%A").lower()

        if day_name in ["saturday", "sunday"]:
            # Skip to Monday
            days_to_add = (7 - next_day.weekday()) if next_day.weekday() > 0 else 1
            next_day = next_day + timedelta(days=days_to_add)
            day_name = "monday"

        time = optimal_times.get(platform, {}).get(day_name, "09:00")
        return f"{next_day.strftime('%Y-%m-%d')} {time}"

    async def _load_opportunity(self, opportunity_id: int) -> Dict:
        """Load content opportunity from database"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT co.*, ei.raw_content as insight_content,
                       na.title as article_title, na.url as article_url
                FROM content_opportunities co
                LEFT JOIN executive_insights ei ON co.insight_id = ei.insight_id
                LEFT JOIN news_articles na ON co.article_id = na.article_id
                WHERE co.opportunity_id = $1
            """, opportunity_id)

            if not row:
                raise ValueError(f"Opportunity {opportunity_id} not found")

            return dict(row)

    async def _store_generated_content(
        self,
        opportunity_id: int,
        platform: str,
        content_type: str,
        content: str,
        metadata: Dict
    ) -> int:
        """Store generated content in database"""
        async with self.db_pool.acquire() as conn:
            content_id = await conn.fetchval("""
                INSERT INTO generated_content (
                    opportunity_id, platform, content_type, content,
                    metadata, status, created_at
                ) VALUES ($1, $2, $3, $4, $5, 'pending_approval', NOW())
                RETURNING content_id
            """,
                opportunity_id,
                platform,
                content_type,
                content,
                json.dumps(metadata)
            )

            print(f"[ContentGenerator] Stored content {content_id} for platform {platform}")
            return content_id

    async def _load_voice_profile(self) -> Dict:
        """Load Milton's active voice profile from database"""
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

    def _load_linkedin_bp(self) -> Dict:
        """Load LinkedIn best practices"""
        return {
            "ideal_length_words": (300, 500),
            "hook_length_chars": 100,
            "optimal_hashtags": (3, 5),
            "line_break_frequency": "every_2_3_sentences",
            "question_placement": "end_of_post"
        }

    def _load_twitter_bp(self) -> Dict:
        """Load Twitter best practices"""
        return {
            "max_thread_length": 5,
            "ideal_tweet_length": (180, 240),
            "hook_critical": True,
            "hashtag_limit": 2
        }


# Test script
async def main():
    from dotenv import load_dotenv
    load_dotenv()

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    db_url = os.getenv("DATABASE_URL")

    if not anthropic_key or not db_url:
        print("ERROR: Missing ANTHROPIC_API_KEY or DATABASE_URL")
        return

    generator = ContentGenerator(anthropic_api_key=anthropic_key, db_url=db_url)
    await generator.initialize()

    try:
        # Test LinkedIn generation
        result = await generator.generate_linkedin_post(
            opportunity_id=1,
            target_pillar="AI Innovation in Sports Business",
            include_personal_story=True
        )

        print("\n=== GENERATED LINKEDIN POST ===")
        print(result['content'])
        print(f"\nWords: {result['word_count']}")
        print(f"Hashtags: {result['hashtags']}")

    finally:
        await generator.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
