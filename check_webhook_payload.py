#!/usr/bin/env python3
"""
Check what data is being sent to Zapier webhook
"""

import json
import os
from dotenv import load_dotenv

load_dotenv()

# This is what should be sent to Zapier
correct_payload = {
    "content": "This is a test post from Milton AI Publicist",
    "platform": "linkedin",
    "post_id": 999,
    "timestamp": "2025-10-20T09:00:00Z"
}

print("=" * 80)
print("CORRECT WEBHOOK PAYLOAD FOR ZAPIER")
print("=" * 80)
print()
print(json.dumps(correct_payload, indent=2))
print()
print("=" * 80)
print("WHAT ZAPIER SHOULD RECEIVE")
print("=" * 80)
print()
print("Field Mappings in Zapier:")
print("  1__content     → 'This is a test post from Milton AI Publicist'")
print("  1__platform    → 'linkedin'")
print("  1__post_id     → 999")
print("  1__timestamp   → '2025-10-20T09:00:00Z'")
print()
print("=" * 80)
print("YOUR LINKEDIN ACTION CONFIGURATION")
print("=" * 80)
print()
print("REQUIRED:")
print("  Comment: 1__content")
print()
print("OPTIONAL (leave ALL blank):")
print("  Content - Title: [EMPTY]")
print("  Content - Description: [EMPTY]")
print("  Content - Image URL: [EMPTY]")
print("  Content - URL: [EMPTY]")
print()
print("OTHER:")
print("  Visible To: anyone")
print()
print("=" * 80)
print("COMMON MISTAKES")
print("=" * 80)
print()
print("❌ WRONG: Content - URL has a value (like a LinkedIn URL)")
print("✅ CORRECT: Content - URL is completely empty")
print()
print("❌ WRONG: Fields have webhook URLs in them")
print("✅ CORRECT: Only Comment field has 1__content")
print()
print("❌ WRONG: Using 1.content (with dot)")
print("✅ CORRECT: Using 1__content (with double underscore)")
print()
print("=" * 80)

webhook_url = os.getenv("ZAPIER_LINKEDIN_WEBHOOK")
if webhook_url:
    print(f"Your webhook URL: {webhook_url}")
else:
    print("⚠️ Warning: ZAPIER_LINKEDIN_WEBHOOK not found in .env")
