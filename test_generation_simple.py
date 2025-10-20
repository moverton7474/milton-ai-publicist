"""
Simple Content Generation Test
Tests Claude API and content generation without database
"""

from anthropic import Anthropic
import os
from dotenv import load_dotenv
from datetime import datetime

print("="*70)
print("MILTON OVERTON AI PUBLICIST - SIMPLE TEST")
print("="*70)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load environment
load_dotenv()

# Get API key
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("[ERROR] ANTHROPIC_API_KEY not found in .env file")
    exit(1)

print(f"[OK] API Key loaded: {api_key[:20]}...")
print()

# Initialize Claude client
try:
    client = Anthropic(api_key=api_key)
    print("[OK] Anthropic client initialized")
except Exception as e:
    print(f"[ERROR] Error initializing client: {e}")
    exit(1)

print()
print("="*70)
print("TEST 1: Generate LinkedIn Post for Milton Overton")
print("="*70)
print()

# Milton's voice profile (simplified)
voice_profile = {
    "tone": "visionary_strategic_approachable",
    "avg_sentence_length": 18,
    "question_ratio": 0.15,
    "storytelling_ratio": 0.20,
    "formality": "professional_accessible"
}

# Content prompt
prompt = """Generate a LinkedIn thought leadership post for Milton Overton, Athletic Director at Keuka College.

**Topic:** How AI-driven technology is transforming college athletics donor engagement and fundraising

**Milton's Voice Profile:**
- Tone: Visionary, strategic, but approachable
- Average sentence length: ~18 words
- Uses questions in ~15% of sentences
- Includes personal stories/examples in ~20% of content
- Professional but accessible language

**Milton's Positioning:**
- THE AI innovator in college sports
- Built KSU Donor Fund AI system (practical AI implementation)
- Uses AI avatar (HeyGen) for donor outreach
- Athletic Director at Keuka College (Division III)
- Positioning for Power Four AD opportunities

**Required Structure:**
1. HOOK (2 lines max): Compelling opening that stops the scroll
2. CONTEXT (2-3 paragraphs): Explain the issue/trend with Milton's unique perspective
3. INSIGHT (2-3 paragraphs): Share the strategic insight or innovation angle
4. CALL-TO-ACTION: End with an engaging question for comments

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

**Embrace:**
- Specific examples and data
- Forward-thinking perspective
- Practical implications
- Milton's authentic voice

Generate the LinkedIn post now:"""

print("[INFO] Generating content with Claude API (this may take 10-15 seconds)...")
print()

try:
    # Call Claude API
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        temperature=0.7,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Extract content
    generated_content = response.content[0].text

    # Calculate stats
    word_count = len(generated_content.split())
    char_count = len(generated_content)

    print("[SUCCESS] CONTENT GENERATION SUCCESSFUL!")
    print()
    print("="*70)
    print("GENERATED LINKEDIN POST:")
    print("="*70)
    print()
    print(generated_content)
    print()
    print("="*70)
    print("STATISTICS:")
    print("="*70)
    print(f"Word Count: {word_count}")
    print(f"Character Count: {char_count}")
    print(f"Target Range: 300-500 words (Current: {'IN RANGE' if 300 <= word_count <= 500 else 'OUT OF RANGE'})")
    print()
    print(f"Input Tokens: {response.usage.input_tokens}")
    print(f"Output Tokens: {response.usage.output_tokens}")
    print(f"Total Tokens: {response.usage.input_tokens + response.usage.output_tokens}")
    print()

    # Estimate cost
    # Claude Sonnet 4 pricing: $3 per million input tokens, $15 per million output tokens
    cost = (response.usage.input_tokens * 3 / 1_000_000) + (response.usage.output_tokens * 15 / 1_000_000)
    print(f"Estimated Cost: ${cost:.4f}")
    print()

    # Simple quality checks
    print("="*70)
    print("QUICK QUALITY CHECKS:")
    print("="*70)

    checks = []

    # Check 1: Word count
    if 300 <= word_count <= 500:
        checks.append(("[OK]", "Word Count", "300-500 words (optimal)"))
    elif 250 <= word_count <= 600:
        checks.append(("[WARN]", "Word Count", "Close to optimal range"))
    else:
        checks.append(("[FAIL]", "Word Count", "Outside optimal range"))

    # Check 2: Hashtags
    hashtag_count = generated_content.count("#")
    if 3 <= hashtag_count <= 5:
        checks.append(("[OK]", "Hashtags", f"{hashtag_count} hashtags (optimal)"))
    elif hashtag_count > 0:
        checks.append(("[WARN]", "Hashtags", f"{hashtag_count} hashtags (recommend 3-5)"))
    else:
        checks.append(("[FAIL]", "Hashtags", "No hashtags found"))

    # Check 3: Question (CTA)
    if "?" in generated_content:
        checks.append(("[OK]", "Call-to-Action", "Question included"))
    else:
        checks.append(("[FAIL]", "Call-to-Action", "No question found"))

    # Check 4: Line breaks
    if "\n\n" in generated_content:
        checks.append(("[OK]", "Formatting", "Paragraph breaks present"))
    else:
        checks.append(("[WARN]", "Formatting", "May need more line breaks"))

    # Check 5: Promotional language
    promo_words = ["excited to announce", "thrilled to share", "honored to", "pleased to"]
    has_promo = any(phrase in generated_content.lower() for phrase in promo_words)
    if not has_promo:
        checks.append(("[OK]", "Tone", "Not overly promotional"))
    else:
        checks.append(("[WARN]", "Tone", "Contains promotional language"))

    for status, check_name, result in checks:
        print(f"{status} {check_name}: {result}")

    print()
    print("="*70)
    print("TEST RESULT: [SUCCESS]")
    print("="*70)
    print()
    print("[INFO] Your AI Publicist system is working!")
    print()
    print("Next steps:")
    print("1. Review the generated content above")
    print("2. Check if it matches Milton's voice and style")
    print("3. Run full system test: python scripts/test_system.py")
    print("4. Start approval dashboard: python dashboard/approval_dashboard.py")
    print()
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

except Exception as e:
    print(f"[ERROR] Content generation failed")
    print(f"Error details: {e}")
    print()
    print("Troubleshooting:")
    print("1. Verify API key is correct")
    print("2. Check internet connection")
    print("3. Ensure you have API credits at https://console.anthropic.com/")
    exit(1)
