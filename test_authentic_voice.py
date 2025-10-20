"""
Test authentic Milton Overton voice generation
Uses real LinkedIn post patterns from milton_linkedin_posts.txt
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

print("="*70)
print("MILTON OVERTON - AUTHENTIC VOICE TEST")
print("="*70)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Get API key
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("[ERROR] ANTHROPIC_API_KEY not found in .env file")
    exit(1)

print(f"[OK] API Key loaded")
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
print("TEST SCENARIOS - Generate posts in Milton's authentic voice")
print("="*70)
print()

# Test scenarios that match Milton's actual posting patterns
scenarios = [
    {
        "name": "Partner Appreciation Post",
        "context": "New technology partner (AI analytics company) just signed sponsorship deal with KSU Athletics to help improve fan engagement and donor insights",
        "instruction": "Write a brief LinkedIn post (2-4 sentences) thanking the partner in Milton's warm, appreciative style"
    },
    {
        "name": "Team Achievement Celebration",
        "context": "KSU Women's Soccer team just won the conference championship for the first time in program history",
        "instruction": "Write a brief congratulatory post (1-3 sentences) celebrating the team in Milton's enthusiastic style"
    },
    {
        "name": "Community Service Highlight",
        "context": "KSU student-athletes volunteered 500 hours this semester at local youth sports programs in Cobb County",
        "instruction": "Write a brief post (2-3 sentences) highlighting this community impact in Milton's humble, community-focused style"
    }
]

for i, scenario in enumerate(scenarios, 1):
    print(f"SCENARIO {i}: {scenario['name']}")
    print("-" * 70)
    print(f"Context: {scenario['context']}")
    print()
    print("[INFO] Generating post with authentic Milton voice...")
    print()

    # Build prompt with Milton's authentic voice profile
    prompt = f"""You are helping Milton Overton, Athletic Director at Kennesaw State University, draft a LinkedIn post.

**CRITICAL VOICE REQUIREMENTS - Milton's Authentic Style:**

1. **LENGTH**: 1-4 sentences maximum (20-80 words). Milton NEVER writes long posts.

2. **TONE**:
   - Warm, supportive, grateful
   - Humble and community-focused
   - Celebratory of others, not self-promotional
   - Faith-informed language welcome ("blessed," "honored")

3. **SIGNATURE PHRASES Milton actually uses**:
   - "Let's Go Owls!" (his signature sign-off - USE THIS!)
   - "I am so proud of..."
   - "Honored/Blessed to..."
   - "We want to thank..."
   - Mention people/organizations BY NAME with appreciation

4. **STYLE**:
   - Simple, direct sentences
   - Exclamation points for enthusiasm (!!!)
   - Personal and relationship-driven
   - Focus on OTHERS' achievements, not Milton's leadership
   - Natural, conversational (occasional informal phrasing is authentic)

5. **WHAT MILTON DOES NOT DO**:
   - NO long thought leadership essays
   - NO business strategy analysis
   - NO data-heavy insights
   - NO self-promotion of his own achievements
   - NO corporate jargon
   - NO hashtag spam (max 2-3 hashtags, often just "#GoOwls")

**REAL MILTON POST EXAMPLES:**

Example 1 (Partner Thank You):
"We want to thank Randy Koporc and our wonderful partners at Fifth Third Bank for there support for Kennesaw State University and the greater Cobb County Community. Fifth Third Bank's foundational support of KSU Athletics over the years has helped us build a championship experience for our student-athletes and coaches. Champion partners build champion leaders in our community. Let's Go Fifth Third Bank and Lets Go Owl !!"

Example 2 (Personal Pride):
"I am so proud of my son Micaiah Overton in his new career and entrepreneurial journey as a graphics designer here in Metro Atlanta. Connect with him on LinkedIn to inquire about his services :)"

Example 3 (Team Celebration):
"Congrats to our leader. This honor is well deserved. Let's Go Owls !!!"

Example 4 (Community Appreciation):
"I am so proud of my brother and friend Mel Clemmons for maximizing the gifts God has blessed him with to make a positive difference in the lives of so many in our community as a business leader, entrepreneur, author and philanthropist. Mel truly has a passion for helping others realize their dreams!!!"

---

**YOUR TASK**: {scenario['instruction']}

**CONTEXT**: {scenario['context']}

Write ONLY the LinkedIn post text. Keep it brief (1-4 sentences), warm, and authentic to Milton's voice. End with "Let's Go Owls!" or similar Owl pride sign-off."""

    try:
        # Call Claude API
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,  # Lower token limit for shorter posts
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Extract content
        generated_post = response.content[0].text.strip()

        # Calculate stats
        word_count = len(generated_post.split())
        sentence_count = generated_post.count('.') + generated_post.count('!') + generated_post.count('?')

        print("GENERATED POST:")
        print("-" * 70)
        print(generated_post)
        print("-" * 70)
        print()
        print(f"Word Count: {word_count}")
        print(f"Sentence Count: {sentence_count}")
        print(f"Has 'Let's Go Owls': {'YES' if 'Owls' in generated_post or 'owls' in generated_post else 'NO'}")
        print(f"Has enthusiasm (!!!): {'YES' if '!!!' in generated_post or '!!' in generated_post else 'NO'}")
        print()

        # Voice authenticity checks
        authenticity_score = 0
        max_score = 5

        checks = []

        # Check 1: Length (should be 20-100 words)
        if 20 <= word_count <= 100:
            authenticity_score += 1
            checks.append(("[OK]", f"Length: {word_count} words (authentic range 20-100)"))
        else:
            checks.append(("[FAIL]", f"Length: {word_count} words (TOO {'SHORT' if word_count < 20 else 'LONG'})"))

        # Check 2: Contains signature phrase
        signature_phrases = ["Let's Go Owls", "Go Owls", "proud of", "honored", "blessed", "thank", "congrats"]
        has_signature = any(phrase.lower() in generated_post.lower() for phrase in signature_phrases)
        if has_signature:
            authenticity_score += 1
            checks.append(("[OK]", "Contains Milton's signature phrases"))
        else:
            checks.append(("[FAIL]", "Missing signature phrases"))

        # Check 3: Warm/positive tone (has exclamation points)
        if '!' in generated_post:
            authenticity_score += 1
            checks.append(("[OK]", "Warm, enthusiastic tone"))
        else:
            checks.append(("[WARN]", "Missing exclamation points (Milton uses these!)"))

        # Check 4: Not too corporate (lacks jargon)
        corporate_jargon = ["leverage", "synergy", "optimize", "paradigm", "strategic imperative", "value proposition"]
        has_jargon = any(word in generated_post.lower() for word in corporate_jargon)
        if not has_jargon:
            authenticity_score += 1
            checks.append(("[OK]", "Natural language (no corporate jargon)"))
        else:
            checks.append(("[FAIL]", "Contains corporate jargon"))

        # Check 5: Focus on others (not "I" heavy)
        i_count = generated_post.lower().count(" i ")
        if i_count <= 2:
            authenticity_score += 1
            checks.append(("[OK]", "Other-focused (appropriate use of 'I')"))
        else:
            checks.append(("[WARN]", f"Too self-focused ({i_count} uses of 'I')"))

        print("AUTHENTICITY CHECKS:")
        print("-" * 70)
        for status, check in checks:
            print(f"{status} {check}")

        print()
        print(f"AUTHENTICITY SCORE: {authenticity_score}/{max_score} ({int(authenticity_score/max_score*100)}%)")
        print()
        print("="*70)
        print()

    except Exception as e:
        print(f"[ERROR] Generation failed: {e}")
        print()

print()
print("="*70)
print("TEST COMPLETE")
print("="*70)
print()
print("ANALYSIS:")
print("- Review the posts above")
print("- Check if they match Milton's brief, warm, celebratory style")
print("- Authentic Milton posts are 1-4 sentences, not essays")
print("- Should focus on thanking/celebrating others, not self-promotion")
print()
print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()
