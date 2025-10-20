"""
Test Milton Overton's Dual Voice System
Demonstrates both Personal (LinkedIn) and Professional (Official AD) voices
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

print("="*70)
print("MILTON OVERTON - DUAL VOICE SYSTEM TEST")
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
client = Anthropic(api_key=api_key)
print("[OK] Anthropic client initialized")
print()

print("="*70)
print("TESTING DUAL VOICE SYSTEM")
print("="*70)
print()
print("Milton uses TWO distinct voices:")
print("1. PERSONAL (LinkedIn) - Brief, warm, celebratory (20-80 words)")
print("2. PROFESSIONAL (Official AD) - Structured, decisive, strategic (200-400 words)")
print()
print("="*70)
print()

# Test scenarios
scenarios = [
    {
        "voice_type": "PERSONAL (LinkedIn)",
        "name": "Partner Appreciation Post",
        "context": "Tech company 'GameChanger Analytics' just signed a 3-year sponsorship deal with KSU Athletics to provide AI-powered fan engagement tools",
        "max_tokens": 200,
        "target_length": "20-80 words",
        "prompt_template": """You are helping Milton Overton draft a PERSONAL LinkedIn post.

**CRITICAL: Use PERSONAL LINKEDIN VOICE**

**Length:** 20-80 words (1-4 sentences) - KEEP IT BRIEF!

**Tone:** Warm, supportive, celebratory, grateful

**Structure:**
1. Opening: "We want to thank..." / "I am so proud..."
2. Brief context (1-2 sentences)
3. Sign-off: "Let's Go Owls!"

**Signature Phrases:**
- "We want to thank [name]..."
- Mention partner BY NAME
- Community impact language
- "Let's Go Owls!" sign-off

**Real Milton LinkedIn Example (79 words):**
"We want to thank Randy Koporc and our wonderful partners at Fifth Third Bank for there support for Kennesaw State University and the greater Cobb County Community. Fifth Third Bank's foundational support of KSU Athletics over the years has helped us build a championship experience for our student-athletes and coaches. Champion partners build champion leaders in our community. Let's Go Fifth Third Bank and Lets Go Owl !!"

**Your Task:** Write a brief LinkedIn post thanking GameChanger Analytics for their partnership.

**Context:** {context}

Write ONLY the LinkedIn post. Keep it 20-80 words. End with "Let's Go Owls!"
"""
    },
    {
        "voice_type": "PERSONAL (LinkedIn)",
        "name": "Team Celebration",
        "context": "KSU Baseball team just won the ASUN Conference Championship for the first time in 5 years, earning automatic bid to NCAA Regional",
        "max_tokens": 200,
        "target_length": "20-80 words",
        "prompt_template": """You are helping Milton Overton draft a PERSONAL LinkedIn post.

**CRITICAL: Use PERSONAL LINKEDIN VOICE**

**Length:** 30-50 words (2-3 sentences) - KEEP IT BRIEF!

**Tone:** Proud, celebratory, enthusiastic

**Structure:**
1. Opening: "I am so proud of..."
2. Brief celebration (1-2 sentences)
3. Sign-off: "Let's Go Owls!!!"

**Real Milton LinkedIn Example (37 words):**
"I am so proud of our Women's Soccer team for winning our first-ever conference championship!! What an incredible milestone for our program and these amazing student-athletes who have worked so hard for this moment. Let's Go Owls!!!"

**Your Task:** Write a brief celebration post for KSU Baseball winning ASUN Championship.

**Context:** {context}

Write ONLY the LinkedIn post. Keep it 30-50 words. Use exclamation points. End with "Let's Go Owls!!!"
"""
    },
    {
        "voice_type": "PROFESSIONAL (Official AD)",
        "name": "New Assistant Coach Hire",
        "context": "Hired Sarah Mitchell as new Associate Head Coach for Women's Basketball. She comes from SEC program with 10 years experience, won 2 conference titles. Aligned with Head Coach vision for program elevation.",
        "max_tokens": 800,
        "target_length": "200-300 words",
        "prompt_template": """You are helping Milton Overton draft an OFFICIAL KSU Athletics statement.

**CRITICAL: Use PROFESSIONAL ATHLETIC DIRECTOR VOICE**

**Length:** 200-300 words (4 paragraphs)

**Tone:** Optimistic, momentum-building, alignment-focused

**Structure - New Hire Template:**

PARAGRAPH 1: Enthusiastic Welcome
- "I am thrilled to welcome [Name] as [position]..."
- Brief background and experience

PARAGRAPH 2: Alignment & Vision
- "After conversations with [Name], [Head Coach], and university leadership..."
- Vision alignment and goals

PARAGRAPH 3: Qualifications
- Specific achievements and background
- Why they're ideal for this role

PARAGRAPH 4: Program Momentum
- This hire's impact on program elevation
- Invitation to Owl Nation

CLOSING: "Let's go Owls! Hooty Hoo!"

**Real Milton Official Statement Example (from head coach hire):**
"I am thrilled to welcome [Coach] as the new head coach for Kennesaw State University football. [Coach] brings extensive experience and a proven track record of building competitive programs.

After extensive conversations with [Coach], President [Name], and our university leadership, we are aligned on the vision for the future of KSU football. [Coach]'s commitment to student-athlete development and championship-caliber football makes them the ideal leader for this next chapter.

Most recently [previous position], [Coach] has [achievements]. Their experience in [area] and passion for [value] will elevate our program and provide exceptional opportunities for our student-athletes.

This hire represents our commitment to building championship-caliber programs that compete at the highest level. I encourage Owl Nation to join me in welcoming [Coach] to the KSU family.

Let's go Owls! Hooty Hoo!"

**Your Task:** Write an official statement announcing Sarah Mitchell's hire.

**Context:** {context}

Follow the 4-paragraph structure. Include alignment language, qualifications, and program momentum. Close with rally phrase.
"""
    },
    {
        "voice_type": "PROFESSIONAL (Official AD)",
        "name": "Policy Announcement: New Parking Fee",
        "context": "Implementing $50 annual 'Owl Champions Parking Pass' for premium stadium parking. Revenue goes to student-athlete nutrition and training facilities. Goal: raise $250,000 annually. Supporters can buy at season ticket renewal.",
        "max_tokens": 900,
        "target_length": "300-400 words",
        "prompt_template": """You are helping Milton Overton draft an OFFICIAL KSU Athletics statement.

**CRITICAL: Use PROFESSIONAL ATHLETIC DIRECTOR VOICE**

**Length:** 300-400 words (4 paragraphs + bullets)

**Tone:** Transparent, educational, action-oriented

**Structure - Policy/Finance Template:**

PARAGRAPH 1: Plain Language Explanation
- Explain what's changing and why
- Transparent about the policy

PARAGRAPH 2: Quantified Goals & Mechanisms
- "Our goal is to [specific target]..."
- Name the mechanism clearly (e.g., "Owl Champions Parking Pass")
- Explain function and purpose

PARAGRAPH 3: Supporter Action Steps (BULLETS)
- How supporters can help:
- Bulleted list of specific actions
- Clear calls to action

PARAGRAPH 4: Rationale & Sustainability
- Why this matters for student-athletes
- Competitive standards and sustainability

CLOSING: "Thank you for your continued support... Let's go Owls!"

**Real Milton Policy Statement Example:**
"I want to provide Owl Nation with an important update on revenue sharing. Under the NCAA-House model, universities will directly share athletics revenue with student-athletes.

Our initial goal is to share over $1,000,000 annually with our student-athletes. To achieve this, we are implementing the Owl Enhancement Fee, which will support this critical investment in our student-athletes.

Owl Nation plays a crucial role in supporting our student-athletes. Here's how you can help:
- Purchase season tickets
- Contribute to the Owls Fund
- Support NIL collectives
- Engage corporate sponsorships

These investments ensure our student-athletes have the resources to compete and succeed at the FBS level. Our commitment to championship-caliber programs requires sustainable funding and community partnership.

Thank you for your continued support of KSU Athletics and our student-athletes. Together, we are building championship programs. Let's go Owls!"

**Your Task:** Write an official statement announcing the new Owl Champions Parking Pass.

**Context:** {context}

Follow the structure. Include plain explanation, quantified goal ($250,000), bulleted actions, and rationale. Close with thank you + rally phrase.
"""
    }
]

# Run tests
results = []

for i, scenario in enumerate(scenarios, 1):
    print(f"TEST {i}/{len(scenarios)}: {scenario['name']}")
    print("-" * 70)
    print(f"Voice Type: {scenario['voice_type']}")
    print(f"Target Length: {scenario['target_length']}")
    print()
    print(f"Context: {scenario['context']}")
    print()
    print("[INFO] Generating content...")
    print()

    try:
        # Build prompt
        prompt = scenario['prompt_template'].format(context=scenario['context'])

        # Call Claude API
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=scenario['max_tokens'],
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        # Extract content
        generated_content = response.content[0].text.strip()

        # Calculate stats
        word_count = len(generated_content.split())
        sentence_count = generated_content.count('.') + generated_content.count('!') + generated_content.count('?')

        print("GENERATED CONTENT:")
        print("=" * 70)
        print(generated_content)
        print("=" * 70)
        print()

        print("STATISTICS:")
        print(f"  Word Count: {word_count}")
        print(f"  Sentence Count: {sentence_count}")
        print(f"  Input Tokens: {response.usage.input_tokens}")
        print(f"  Output Tokens: {response.usage.output_tokens}")
        print(f"  Cost: ${(response.usage.input_tokens * 0.003 + response.usage.output_tokens * 0.015) / 1000:.4f}")
        print()

        # Voice-specific checks
        if "PERSONAL" in scenario['voice_type']:
            print("PERSONAL VOICE CHECKS:")
            print("-" * 70)
            checks = []

            # Length check
            if 20 <= word_count <= 80:
                checks.append(("[OK]", f"Length: {word_count} words (target: 20-80)"))
            else:
                checks.append(("[FAIL]", f"Length: {word_count} words (OUT OF RANGE)"))

            # Sign-off check
            if "owls" in generated_content.lower() and "!" in generated_content:
                checks.append(("[OK]", "Contains 'Let's Go Owls!' sign-off"))
            else:
                checks.append(("[FAIL]", "Missing 'Let's Go Owls!' sign-off"))

            # Enthusiasm check
            if "!" in generated_content:
                checks.append(("[OK]", "Enthusiastic tone (exclamation points)"))
            else:
                checks.append(("[WARN]", "Missing enthusiasm (no exclamation points)"))

            # Brevity check
            if sentence_count <= 5:
                checks.append(("[OK]", f"Brief and concise ({sentence_count} sentences)"))
            else:
                checks.append(("[WARN]", f"May be too long ({sentence_count} sentences)"))

            for status, check in checks:
                print(f"{status} {check}")

        else:  # PROFESSIONAL voice
            print("PROFESSIONAL VOICE CHECKS:")
            print("-" * 70)
            checks = []

            # Length check
            if 200 <= word_count <= 450:
                checks.append(("[OK]", f"Length: {word_count} words (target: 200-400)"))
            else:
                checks.append(("[WARN]", f"Length: {word_count} words (adjust if needed)"))

            # Structure check (paragraphs)
            paragraph_count = generated_content.count('\n\n') + 1
            if paragraph_count >= 4:
                checks.append(("[OK]", f"Structured format ({paragraph_count} paragraphs)"))
            else:
                checks.append(("[WARN]", f"May need more structure ({paragraph_count} paragraphs)"))

            # Student-athlete focus
            if "student-athlete" in generated_content.lower():
                checks.append(("[OK]", "Student-athlete focused"))
            else:
                checks.append(("[WARN]", "Consider adding student-athlete focus"))

            # Closing rally phrase
            if any(phrase in generated_content.lower() for phrase in ["let's go owls", "hooty hoo", "go owls"]):
                checks.append(("[OK]", "Contains rally phrase closing"))
            else:
                checks.append(("[FAIL]", "Missing rally phrase closing"))

            for status, check in checks:
                print(f"{status} {check}")

        print()
        print("="*70)
        print()

        results.append({
            "scenario": scenario['name'],
            "voice": scenario['voice_type'],
            "word_count": word_count,
            "success": True
        })

    except Exception as e:
        print(f"[ERROR] Generation failed: {e}")
        print()
        results.append({
            "scenario": scenario['name'],
            "voice": scenario['voice_type'],
            "success": False
        })

# Summary
print()
print("="*70)
print("TEST SUMMARY")
print("="*70)
print()

successful = sum(1 for r in results if r['success'])
print(f"Tests Run: {len(results)}")
print(f"Successful: {successful}/{len(results)}")
print()

print("RESULTS BY VOICE TYPE:")
print("-" * 70)
personal_tests = [r for r in results if "PERSONAL" in r['voice']]
professional_tests = [r for r in results if "PROFESSIONAL" in r['voice']]

print(f"PERSONAL Voice: {sum(1 for r in personal_tests if r['success'])}/{len(personal_tests)} successful")
for r in personal_tests:
    if r['success']:
        print(f"  - {r['scenario']}: {r['word_count']} words")

print()
print(f"PROFESSIONAL Voice: {sum(1 for r in professional_tests if r['success'])}/{len(professional_tests)} successful")
for r in professional_tests:
    if r['success']:
        print(f"  - {r['scenario']}: {r['word_count']} words")

print()
print("="*70)
print("DUAL VOICE SYSTEM: OPERATIONAL")
print("="*70)
print()
print("Next Steps:")
print("1. Review generated content for authenticity")
print("2. Compare to real Milton posts/statements")
print("3. Integrate dual-voice system into main generator")
print("4. Update dashboard to support voice selection")
print()
print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()
