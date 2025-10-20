"""
Voice Profile Modeling - Module II
NLP-based voice profile modeling trained on Milton's existing content
"""

import re
from typing import List, Dict, Tuple
from collections import Counter
import numpy as np
from pathlib import Path
import asyncpg
import os
import json

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("[VoiceModeling] Warning: spaCy not available. Using simplified NLP.")


class VoiceProfileModeler:
    """
    NLP-based voice profile modeling trained on Milton's existing content

    Analyzes:
    - Sentence structure patterns
    - Vocabulary and lexicon
    - Rhetorical devices
    - Story vs. analysis ratio
    - Tone indicators
    """

    def __init__(self, db_url: str):
        """
        Initialize Voice Profile Modeler

        Args:
            db_url: PostgreSQL connection URL
        """
        self.db_url = db_url
        self.db_pool = None
        self.nlp = None

        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("[VoiceModeling] spaCy model not found. Run: python -m spacy download en_core_web_sm")
                SPACY_AVAILABLE = False

        self.profile = {}

    async def initialize(self):
        """Initialize database connection"""
        self.db_pool = await asyncpg.create_pool(self.db_url, min_size=2, max_size=10)

    async def close(self):
        """Close database connection"""
        if self.db_pool:
            await self.db_pool.close()

    async def train_on_corpus(self, corpus_dir: str, version: str = "2.0.0") -> Dict:
        """
        Train voice model on Milton's existing content

        Args:
            corpus_dir: Directory containing Milton's content files
            version: Voice profile version number

        Returns:
            Comprehensive voice profile dictionary
        """
        print(f"[VoiceModeling] Training on corpus: {corpus_dir}")

        # Load all content files
        existing_content = self._load_corpus(corpus_dir)

        if not existing_content:
            print("[VoiceModeling] Warning: No content found in corpus directory")
            return self._get_default_profile()

        print(f"[VoiceModeling] Loaded {len(existing_content)} content pieces")

        # Analyze with spaCy if available
        if SPACY_AVAILABLE and self.nlp:
            docs = [self.nlp(text) for text in existing_content]
        else:
            docs = existing_content  # Use raw text

        # Build comprehensive profile
        self.profile = {
            "version": version,
            "lexical": self.analyze_lexical(docs),
            "syntactic": self.analyze_syntactic(docs),
            "semantic": self.analyze_semantic(docs),
            "rhetorical": self.analyze_rhetorical(existing_content),
            "formatting": self.analyze_formatting(existing_content),
            "emotional_tone": self.analyze_tone(docs),
            "trained_on_corpus_size": len(existing_content)
        }

        # Store in database
        await self._store_voice_profile(self.profile)

        print(f"[VoiceModeling] Training complete. Profile version: {version}")

        return self.profile

    def _load_corpus(self, corpus_dir: str) -> List[str]:
        """Load all text files from corpus directory"""
        corpus_path = Path(corpus_dir)
        content = []

        if not corpus_path.exists():
            print(f"[VoiceModeling] Corpus directory not found: {corpus_dir}")
            return content

        # Load all .txt files recursively
        for txt_file in corpus_path.rglob("*.txt"):
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    text = f.read().strip()
                    if text:
                        content.append(text)
            except Exception as e:
                print(f"[VoiceModeling] Error reading {txt_file}: {e}")

        return content

    def analyze_lexical(self, docs) -> Dict:
        """Analyze vocabulary and word choice"""

        all_tokens = []

        if SPACY_AVAILABLE and self.nlp:
            # Use spaCy for proper tokenization
            for doc in docs:
                all_tokens.extend([
                    token.text.lower()
                    for token in doc
                    if not token.is_stop and not token.is_punct and token.is_alpha
                ])
        else:
            # Simple tokenization
            for text in docs:
                words = re.findall(r'\b[a-z]+\b', text.lower())
                all_tokens.extend([w for w in words if len(w) > 2])

        word_freq = Counter(all_tokens)

        return {
            "vocabulary_size": len(set(all_tokens)),
            "most_common_words": dict(word_freq.most_common(50)),
            "avg_word_length": round(np.mean([len(w) for w in all_tokens]) if all_tokens else 0, 2),
            "unique_terminology": self._extract_domain_terms(all_tokens)
        }

    def analyze_syntactic(self, docs) -> Dict:
        """Analyze sentence structure patterns"""

        sentence_lengths = []

        if SPACY_AVAILABLE and self.nlp:
            for doc in docs:
                for sent in doc.sents:
                    sentence_lengths.append(len(list(sent)))
        else:
            # Simple sentence detection
            for text in docs:
                sentences = re.split(r'[.!?]+', text)
                for sent in sentences:
                    words = sent.strip().split()
                    if words:
                        sentence_lengths.append(len(words))

        if not sentence_lengths:
            return {
                "avg_sentence_length": 18.0,
                "sentence_length_std": 5.0,
                "complex_sentence_ratio": 0.3
            }

        return {
            "avg_sentence_length": round(np.mean(sentence_lengths), 2),
            "sentence_length_std": round(np.std(sentence_lengths), 2),
            "complex_sentence_ratio": round(sum(1 for l in sentence_lengths if l > 20) / len(sentence_lengths), 2)
        }

    def analyze_semantic(self, docs) -> Dict:
        """Analyze meaning patterns and themes"""

        themes = []
        entities = []

        if SPACY_AVAILABLE and self.nlp:
            for doc in docs:
                # Extract named entities
                entities.extend([ent.text for ent in doc.ents])

                # Extract noun chunks as themes
                themes.extend([chunk.text for chunk in doc.noun_chunks])
        else:
            # Simple capitalized word extraction
            for text in docs:
                # Find capitalized phrases (potential entities)
                caps = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
                entities.extend(caps)

        return {
            "common_themes": dict(Counter(themes).most_common(20)),
            "frequently_mentioned": dict(Counter(entities).most_common(20)),
            "topic_distribution": {
                "AI_Innovation": 0.35,
                "Leadership": 0.30,
                "College_Sports_Future": 0.35
            }
        }

    def analyze_rhetorical(self, texts: List[str]) -> Dict:
        """Analyze rhetorical devices and persuasion patterns"""

        question_count = sum(text.count("?") for text in texts)
        total_sentences = sum(text.count(".") + text.count("?") + text.count("!") for text in texts)

        return {
            "question_ratio": round(question_count / max(total_sentences, 1), 2),
            "uses_metaphors": self._detect_metaphors(texts),
            "uses_data_points": round(self._detect_data_usage(texts), 2),
            "storytelling_ratio": round(self._calculate_story_ratio(texts), 2),
            "call_to_action_patterns": self._extract_cta_patterns(texts)
        }

    def analyze_formatting(self, texts: List[str]) -> Dict:
        """Analyze formatting preferences"""

        uses_bullets = sum(("•" in text or "- " in text or "* " in text) for text in texts)
        uses_numbers = sum(bool(re.search(r'^\d+\.', text, re.MULTILINE)) for text in texts)
        uses_emoji = sum(bool(re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', text)) for text in texts)

        return {
            "bullet_point_frequency": round(uses_bullets / len(texts), 2),
            "numbered_list_frequency": round(uses_numbers / len(texts), 2),
            "emoji_usage": round(uses_emoji / len(texts), 2),
            "paragraph_length": round(self._calculate_avg_paragraph_length(texts), 2),
            "line_break_pattern": self._analyze_line_breaks(texts)
        }

    def analyze_tone(self, docs) -> Dict:
        """Analyze emotional tone and sentiment"""

        # Keyword-based tone analysis
        positive_words = ["innovative", "exciting", "opportunity", "future", "success", "amazing", "incredible", "fantastic"]
        analytical_words = ["strategy", "data", "analysis", "framework", "system", "approach", "methodology"]
        personal_words = ["I", "we", "my", "our", "believe", "feel", "think"]

        tone_scores = {
            "optimistic": 0,
            "analytical": 0,
            "personal": 0
        }

        if SPACY_AVAILABLE and self.nlp:
            for doc in docs:
                text = doc.text.lower()
                tone_scores["optimistic"] += sum(text.count(w.lower()) for w in positive_words)
                tone_scores["analytical"] += sum(text.count(w.lower()) for w in analytical_words)
                tone_scores["personal"] += sum(text.count(w.lower()) for w in personal_words)
        else:
            for text in docs:
                text_lower = text.lower()
                tone_scores["optimistic"] += sum(text_lower.count(w.lower()) for w in positive_words)
                tone_scores["analytical"] += sum(text_lower.count(w.lower()) for w in analytical_words)
                tone_scores["personal"] += sum(text_lower.count(w.lower()) for w in personal_words)

        total = sum(tone_scores.values()) or 1
        tone_distribution = {k: round(v/total, 2) for k, v in tone_scores.items()}

        return {
            "primary_tone": "visionary_strategic_approachable",
            "tone_distribution": tone_distribution,
            "formality_level": "professional_accessible"
        }

    # Helper methods
    def _extract_domain_terms(self, tokens: List[str]) -> List[str]:
        """Extract domain-specific terminology"""
        domain_terms = [
            "nil", "donor", "athletics", "ncaa", "conference",
            "ai", "innovation", "strategy", "engagement", "technology",
            "leadership", "analytics", "digital", "fundraising"
        ]
        found_terms = [term for term in domain_terms if term in tokens]
        return found_terms[:10]  # Top 10

    def _detect_metaphors(self, texts: List[str]) -> bool:
        """Detect if metaphors are used"""
        metaphor_indicators = ["like", "as if", "imagine", "think of", "picture this"]
        return any(any(ind in text.lower() for ind in metaphor_indicators) for text in texts)

    def _detect_data_usage(self, texts: List[str]) -> float:
        """Detect frequency of data/stats usage"""
        data_mentions = 0
        for text in texts:
            # Look for numbers, percentages, statistics
            data_mentions += len(re.findall(r'\d+%|\d+\.\d+|\$\d+|#\d+', text))
        return data_mentions / max(len(texts), 1)

    def _calculate_story_ratio(self, texts: List[str]) -> float:
        """Calculate ratio of storytelling vs analysis"""
        story_indicators = ["recently", "last week", "when I", "we had", "remember", "story", "example"]
        story_count = sum(
            any(ind in text.lower() for ind in story_indicators)
            for text in texts
        )
        return story_count / max(len(texts), 1)

    def _extract_cta_patterns(self, texts: List[str]) -> List[str]:
        """Extract call-to-action patterns"""
        cta_patterns = []
        for text in texts:
            # Find questions at end
            sentences = re.split(r'[.!?]+', text)
            for sent in sentences:
                if '?' in sent:
                    cta_patterns.append(sent.strip() + '?')

        return list(set(cta_patterns[:5]))  # Top 5 unique

    def _calculate_avg_paragraph_length(self, texts: List[str]) -> float:
        """Calculate average paragraph length"""
        paragraph_lengths = []
        for text in texts:
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            paragraph_lengths.extend([len(p.split()) for p in paragraphs])
        return np.mean(paragraph_lengths) if paragraph_lengths else 50.0

    def _analyze_line_breaks(self, texts: List[str]) -> Dict:
        """Analyze line break usage patterns"""
        double_breaks = sum(text.count("\n\n") for text in texts)
        single_breaks = sum(text.count("\n") for text in texts)

        return {
            "double_break_frequency": round(double_breaks / max(len(texts), 1), 2),
            "single_break_frequency": round(single_breaks / max(len(texts), 1), 2),
            "prefers_short_paragraphs": double_breaks > len(texts) * 2
        }

    def _get_default_profile(self) -> Dict:
        """Return default voice profile when no training data available"""
        return {
            "version": "1.0.0-default",
            "lexical": {
                "vocabulary_size": 1000,
                "most_common_words": {},
                "avg_word_length": 5.5,
                "unique_terminology": ["ai", "innovation", "leadership", "athletics"]
            },
            "syntactic": {
                "avg_sentence_length": 18.0,
                "sentence_length_std": 5.0,
                "complex_sentence_ratio": 0.3
            },
            "semantic": {
                "common_themes": {},
                "frequently_mentioned": {},
                "topic_distribution": {
                    "AI_Innovation": 0.35,
                    "Leadership": 0.30,
                    "College_Sports_Future": 0.35
                }
            },
            "rhetorical": {
                "question_ratio": 0.15,
                "uses_metaphors": True,
                "uses_data_points": 2.5,
                "storytelling_ratio": 0.20,
                "call_to_action_patterns": ["What are your thoughts?", "How do you see this evolving?"]
            },
            "formatting": {
                "bullet_point_frequency": 0.3,
                "numbered_list_frequency": 0.2,
                "emoji_usage": 0.1,
                "paragraph_length": 50.0,
                "line_break_pattern": {
                    "double_break_frequency": 3.0,
                    "single_break_frequency": 8.0,
                    "prefers_short_paragraphs": True
                }
            },
            "emotional_tone": {
                "primary_tone": "visionary_strategic_approachable",
                "tone_distribution": {
                    "optimistic": 0.4,
                    "analytical": 0.4,
                    "personal": 0.2
                },
                "formality_level": "professional_accessible"
            },
            "trained_on_corpus_size": 0
        }

    async def _store_voice_profile(self, profile: Dict):
        """Store voice profile in database"""
        async with self.db_pool.acquire() as conn:
            # Deactivate old profiles
            await conn.execute("UPDATE voice_profile SET is_active = FALSE")

            # Insert new profile
            await conn.execute("""
                INSERT INTO voice_profile (
                    version, vocabulary_size, avg_word_length, most_common_words,
                    unique_terminology, avg_sentence_length, sentence_length_std,
                    complex_sentence_ratio, common_themes, frequently_mentioned,
                    topic_distribution, question_ratio, uses_metaphors,
                    data_usage_frequency, storytelling_ratio, cta_patterns,
                    bullet_point_frequency, numbered_list_frequency, emoji_usage,
                    avg_paragraph_length, line_break_pattern, primary_tone,
                    tone_distribution, formality_level, trained_on_corpus_size,
                    is_active
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                    $11, $12, $13, $14, $15, $16, $17, $18, $19, $20,
                    $21, $22, $23, $24, $25, TRUE
                )
            """,
                profile['version'],
                profile['lexical']['vocabulary_size'],
                profile['lexical']['avg_word_length'],
                json.dumps(profile['lexical']['most_common_words']),
                profile['lexical']['unique_terminology'],
                profile['syntactic']['avg_sentence_length'],
                profile['syntactic']['sentence_length_std'],
                profile['syntactic']['complex_sentence_ratio'],
                json.dumps(profile['semantic']['common_themes']),
                json.dumps(profile['semantic']['frequently_mentioned']),
                json.dumps(profile['semantic']['topic_distribution']),
                profile['rhetorical']['question_ratio'],
                profile['rhetorical']['uses_metaphors'],
                profile['rhetorical']['uses_data_points'],
                profile['rhetorical']['storytelling_ratio'],
                profile['rhetorical']['call_to_action_patterns'],
                profile['formatting']['bullet_point_frequency'],
                profile['formatting']['numbered_list_frequency'],
                profile['formatting']['emoji_usage'],
                profile['formatting']['paragraph_length'],
                json.dumps(profile['formatting']['line_break_pattern']),
                profile['emotional_tone']['primary_tone'],
                json.dumps(profile['emotional_tone']['tone_distribution']),
                profile['emotional_tone']['formality_level'],
                profile['trained_on_corpus_size']
            )

            print(f"[VoiceModeling] Stored voice profile version {profile['version']}")


# Standalone script for training
async def main():
    from dotenv import load_dotenv
    import argparse

    load_dotenv()

    parser = argparse.ArgumentParser(description="Train Milton's voice profile")
    parser.add_argument('--corpus-dir', required=True, help='Directory containing Milton\'s content')
    parser.add_argument('--version', default='2.0.0', help='Profile version number')
    args = parser.parse_args()

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return

    modeler = VoiceProfileModeler(db_url=db_url)
    await modeler.initialize()

    try:
        profile = await modeler.train_on_corpus(args.corpus_dir, args.version)
        print("\n=== VOICE PROFILE ===")
        print(json.dumps(profile, indent=2))
        print(f"\nProfile stored in database with version: {profile['version']}")
    finally:
        await modeler.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
