"""
Quality Assurance System - Module II
QA checks for generated content before approval
"""

from typing import Dict, List
import re
import json
from anthropic import Anthropic
import asyncpg


class QualityAssurance:
    """
    Quality assurance for generated content

    Checks:
    - Voice authenticity
    - Brand alignment
    - Platform compliance
    - Engagement optimization
    - Readability
    """

    def __init__(self, anthropic_api_key: str, db_url: str):
        """
        Initialize QA system

        Args:
            anthropic_api_key: Anthropic API key for voice checking
            db_url: PostgreSQL connection URL
        """
        self.client = Anthropic(api_key=anthropic_api_key)
        self.db_url = db_url
        self.db_pool = None
        self.voice_profile = {}

        # Quality thresholds
        self.thresholds = {
            "voice_authenticity": 0.75,
            "brand_alignment": 0.80,
            "platform_compliance": 0.85,
            "engagement_prediction": 0.60,
            "readability": 0.70,
            "overall": 0.75
        }

    async def initialize(self):
        """Initialize database connection and load voice profile"""
        self.db_pool = await asyncpg.create_pool(self.db_url, min_size=2, max_size=10)
        self.voice_profile = await self._load_voice_profile()

    async def close(self):
        """Close database connection"""
        if self.db_pool:
            await self.db_pool.close()

    async def full_qa_check(self, content_id: int) -> Dict:
        """
        Comprehensive QA check on generated content

        Args:
            content_id: ID of generated content to check

        Returns:
            QA report with scores, pass/fail, and recommendations
        """
        print(f"[QA] Running full QA check on content {content_id}")

        # Load content from database
        content = await self._load_content(content_id)

        platform = content['platform']
        text = content['content']

        # Run all checks
        checks = {
            "voice_authenticity": await self.check_voice_authenticity(text),
            "brand_alignment": self.check_brand_alignment(text, platform),
            "platform_compliance": self.check_platform_compliance(content),
            "engagement_potential": self.check_engagement_potential(content),
            "readability": self.check_readability(text)
        }

        # Calculate overall score
        overall_score = sum(c["score"] for c in checks.values()) / len(checks)

        # Determine pass/fail
        passed = all(
            checks[key]["score"] >= self.thresholds.get(key, 0.70)
            for key in checks.keys()
            if key in self.thresholds
        )

        qa_result = {
            "content_id": content_id,
            "overall_score": round(overall_score, 2),
            "passed": passed,
            "checks": checks,
            "recommendations": self._generate_recommendations(checks),
            "ready_for_approval": passed and overall_score >= self.thresholds["overall"]
        }

        # Store QA scores in database
        await self._update_content_qa_scores(content_id, qa_result)

        print(f"[QA] Content {content_id} QA complete. Score: {overall_score:.2f}, Passed: {passed}")

        return qa_result

    async def check_voice_authenticity(self, text: str) -> Dict:
        """
        Check if content matches Milton's authentic voice

        Uses Claude to compare against voice profile
        """

        prompt = f"""Analyze if this content authentically matches Milton Overton's voice profile.

**Content:**
{text}

**Milton's Voice Profile:**
- Tone: {self.voice_profile.get('primary_tone', 'visionary_strategic_approachable')}
- Avg sentence length: ~{self.voice_profile.get('avg_sentence_length', 18)} words
- Question usage: {self.voice_profile.get('question_ratio', 0.15):.0%} of sentences
- Personal stories: {self.voice_profile.get('storytelling_ratio', 0.20):.0%} of content
- Formality: {self.voice_profile.get('formality_level', 'professional_accessible')}

**Voice Characteristics:**
- Visionary yet practical
- Strategic insights backed by experience
- Avoids generic "AI speak" and buzzwords without substance
- Uses specific examples and data
- Authentic and approachable, not overly promotional

**Analysis Required:**
1. Tone match (visionary, strategic, approachable)
2. Sentence structure similarity
3. Vocabulary alignment
4. Avoids generic corporate speak
5. Has personal/authentic feel
6. Sounds like a real person, not AI

Return JSON:
{{
    "score": 0.0-1.0,
    "matches_tone": true/false,
    "sounds_authentic": true/false,
    "concerns": ["list any voice issues"],
    "suggestions": ["how to improve authenticity"]
}}"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text

            # Extract JSON
            if "```json" in result_text:
                json_str = result_text.split("```json")[1].split("```")[0].strip()
            else:
                json_str = result_text

            return json.loads(json_str)

        except Exception as e:
            print(f"[QA] Voice authenticity check error: {e}")
            # Return conservative score on error
            return {
                "score": 0.70,
                "matches_tone": True,
                "sounds_authentic": True,
                "concerns": ["Unable to complete full voice analysis"],
                "suggestions": ["Manual review recommended"]
            }

    def check_brand_alignment(self, text: str, platform: str) -> Dict:
        """
        Check alignment with Milton's brand pillars

        Three pillars:
        1. AI Innovation in Sports Business
        2. Leadership & Vision
        3. Future of College Sports
        """

        score = 0.0
        aligned_pillars = []
        concerns = []

        text_lower = text.lower()

        # Check pillar alignment
        pillar_keywords = {
            "AI Innovation": ["ai", "artificial intelligence", "technology", "innovation", "data", "avatar", "synthesia", "heygen", "automation", "digital"],
            "Leadership": ["leadership", "strategy", "vision", "culture", "team", "executive", "management", "organizational"],
            "Future of Sports": ["future", "nil", "conference", "trend", "changing", "evolution", "reform", "ncaa"]
        }

        for pillar, keywords in pillar_keywords.items():
            if any(kw in text_lower for kw in keywords):
                aligned_pillars.append(pillar)
                score += 0.33

        # Check for positioning as innovator
        innovator_indicators = ["first", "innovative", "pioneering", "leading", "ahead"]
        if any(ind in text_lower for ind in innovator_indicators):
            score += 0.1

        # Check for specific Milton branding (KSU Donor Fund)
        if "donor" in text_lower or "fundraising" in text_lower:
            if "ksu" in text_lower or "keuka" in text_lower:
                score += 0.1
            else:
                concerns.append("Mentions donors but not the KSU Donor Fund initiative")

        # Avoid over-promotional tone
        if text.count("!") > 3:
            concerns.append("Too many exclamation points - sounds promotional")
            score -= 0.1

        # Avoid generic motivational speak
        generic_phrases = ["excited to announce", "thrilled to share", "honored to", "humbled"]
        if any(phrase in text_lower for phrase in generic_phrases):
            concerns.append("Contains generic corporate speak")
            score -= 0.05

        return {
            "score": min(max(score, 0.0), 1.0),
            "aligned_pillars": aligned_pillars,
            "concerns": concerns,
            "positions_as_innovator": score >= 0.4
        }

    def check_platform_compliance(self, content: Dict) -> Dict:
        """Check compliance with platform best practices"""

        platform = content['platform']
        score = 1.0
        issues = []

        if platform == "linkedin":
            text = content['content']
            word_count = len(text.split())

            # Length check
            if word_count < 300:
                issues.append(f"Too short ({word_count} words, target 300-500)")
                score -= 0.2
            elif word_count > 600:
                issues.append(f"Too long ({word_count} words, target 300-500)")
                score -= 0.1

            # Hook check (first 100 chars)
            hook = text[:100]
            if "\n" not in hook[:150]:  # Should have line break early
                issues.append("Hook should have line break within first 150 chars for mobile")
                score -= 0.1

            # Hashtag check
            hashtag_count = text.count("#")
            if hashtag_count < 3:
                issues.append(f"Too few hashtags ({hashtag_count}, target 3-5)")
                score -= 0.1
            elif hashtag_count > 7:
                issues.append(f"Too many hashtags ({hashtag_count}, target 3-5)")
                score -= 0.1

            # CTA check (question at end)
            if "?" not in text[-200:]:
                issues.append("Missing question/CTA at end")
                score -= 0.15

        elif platform == "twitter":
            # Parse tweets
            tweets = content['content'].split("\n\n---TWEET---\n\n")

            # Tweet count
            if len(tweets) < 3:
                issues.append(f"Thread too short ({len(tweets)} tweets, recommend 3-5)")
                score -= 0.1
            elif len(tweets) > 7:
                issues.append(f"Thread too long ({len(tweets)} tweets, recommend 3-5)")
                score -= 0.1

            # Character limits
            for i, tweet in enumerate(tweets):
                if len(tweet) > 280:
                    issues.append(f"Tweet {i+1} exceeds 280 characters ({len(tweet)} chars)")
                    score -= 0.2

        return {
            "score": max(score, 0.0),
            "compliant": len(issues) == 0,
            "issues": issues
        }

    def check_engagement_potential(self, content: Dict) -> Dict:
        """Predict engagement potential"""

        platform = content['platform']
        text = content['content']

        score = 0.5  # Base score
        factors = []

        # Question inclusion (drives comments)
        question_count = text.count("?")
        if question_count >= 1:
            score += 0.15
            factors.append("Includes engaging question(s)")

        # Hook strength (first 100 chars)
        hook = text[:100]
        if any(char in hook for char in ["?", "!"]):
            score += 0.1
            factors.append("Strong hook")

        # Length appropriateness
        word_count = len(text.split())
        if platform == "linkedin" and 300 <= word_count <= 500:
            score += 0.1
            factors.append("Optimal length")

        # Hashtag usage
        hashtag_count = text.count("#")
        if 3 <= hashtag_count <= 5:
            score += 0.05
            factors.append("Good hashtag count")

        # Data/statistics (drives shares)
        if re.search(r'\d+%|\d+\.\d+', text):
            score += 0.1
            factors.append("Includes data/statistics")

        # Personal story (drives emotional engagement)
        personal_indicators = ["recently", "last week", "when i", "we had", "remember"]
        if any(ind in text.lower() for ind in personal_indicators):
            score += 0.1
            factors.append("Includes personal story/example")

        return {
            "score": min(score, 1.0),
            "predicted_engagement": "high" if score >= 0.8 else "medium" if score >= 0.6 else "low",
            "factors": factors
        }

    def check_readability(self, text: str) -> Dict:
        """Check readability using simplified metrics"""

        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return {"score": 0.5, "grade_level": "unknown", "issues": ["No sentences detected"]}

        words = text.split()
        avg_sentence_length = len(words) / len(sentences)

        # Simplified readability score
        # Ideal: 15-20 words per sentence for professional content
        if 15 <= avg_sentence_length <= 20:
            score = 1.0
            grade = "executive_appropriate"
        elif 12 <= avg_sentence_length <= 23:
            score = 0.85
            grade = "good"
        else:
            score = 0.70
            grade = "needs_adjustment"

        issues = []
        if avg_sentence_length > 25:
            issues.append("Sentences too long - consider breaking up")
        elif avg_sentence_length < 10:
            issues.append("Sentences too short - may feel choppy")

        return {
            "score": score,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "grade_level": grade,
            "issues": issues
        }

    def _generate_recommendations(self, checks: Dict) -> List[str]:
        """Generate actionable recommendations from QA checks"""

        recommendations = []

        # Voice authenticity
        voice_check = checks.get("voice_authenticity", {})
        if voice_check.get("score", 1.0) < self.thresholds["voice_authenticity"]:
            recommendations.extend(voice_check.get("suggestions", []))

        # Brand alignment
        brand_check = checks.get("brand_alignment", {})
        if brand_check.get("score", 1.0) < self.thresholds["brand_alignment"]:
            if not brand_check.get("aligned_pillars"):
                recommendations.append("Strengthen alignment with thought leadership pillars")
            recommendations.extend([f"Concern: {c}" for c in brand_check.get("concerns", [])])

        # Platform compliance
        platform_check = checks.get("platform_compliance", {})
        if not platform_check.get("compliant", True):
            recommendations.extend([f"Fix: {issue}" for issue in platform_check.get("issues", [])])

        # Engagement
        engagement_check = checks.get("engagement_potential", {})
        if engagement_check.get("score", 1.0) < self.thresholds["engagement_prediction"]:
            if engagement_check.get("predicted_engagement") == "low":
                recommendations.append("Add engaging question or call-to-action")
                recommendations.append("Consider including data or personal example")

        # Readability
        readability_check = checks.get("readability", {})
        recommendations.extend(readability_check.get("issues", []))

        return recommendations if recommendations else ["Content passes all QA checks - ready for approval"]

    async def _load_content(self, content_id: int) -> Dict:
        """Load generated content from database"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT content_id, platform, content_type, content, metadata
                FROM generated_content
                WHERE content_id = $1
            """, content_id)

            if not row:
                raise ValueError(f"Content {content_id} not found")

            return dict(row)

    async def _update_content_qa_scores(self, content_id: int, qa_result: Dict):
        """Update generated_content table with QA scores"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                UPDATE generated_content
                SET
                    voice_authenticity_score = $2,
                    brand_alignment_score = $3,
                    engagement_prediction_score = $4,
                    readability_score = $5,
                    overall_qa_score = $6,
                    status = CASE WHEN $7 THEN 'pending_approval' ELSE status END
                WHERE content_id = $1
            """,
                content_id,
                qa_result["checks"]["voice_authenticity"]["score"],
                qa_result["checks"]["brand_alignment"]["score"],
                qa_result["checks"]["engagement_potential"]["score"],
                qa_result["checks"]["readability"]["score"],
                qa_result["overall_score"],
                qa_result["passed"]
            )

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
                return {
                    'primary_tone': 'visionary_strategic_approachable',
                    'avg_sentence_length': 18.0,
                    'question_ratio': 0.15,
                    'storytelling_ratio': 0.20,
                    'formality_level': 'professional_accessible'
                }


# Test script
async def main():
    from dotenv import load_dotenv
    import os

    load_dotenv()

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    db_url = os.getenv("DATABASE_URL")

    if not anthropic_key or not db_url:
        print("ERROR: Missing ANTHROPIC_API_KEY or DATABASE_URL")
        return

    qa = QualityAssurance(anthropic_api_key=anthropic_key, db_url=db_url)
    await qa.initialize()

    try:
        # Run QA check on content_id 1
        result = await qa.full_qa_check(content_id=1)

        print("\n=== QA REPORT ===")
        print(json.dumps(result, indent=2))

    finally:
        await qa.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
