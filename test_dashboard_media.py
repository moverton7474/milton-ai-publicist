"""
Test Dashboard Media Generation via API
Simulates generating content through the dashboard
"""

import requests
import json

# Dashboard URL
DASHBOARD_URL = "http://localhost:8081"

print("="*70)
print("DASHBOARD MEDIA GENERATION TEST")
print("="*70)
print()

# Test 1: Generate post with graphic
print("[TEST 1] Generate post with branded graphic")
print()

payload = {
    "voice_type": "personal",
    "scenario": "Partner Appreciation",
    "context": "Thank VyStar Credit Union for their incredible partnership with KSU Athletics",
    "include_graphic": True,
    "include_video": False,
    "partner_logo": "vystar"
}

print(f"POST {DASHBOARD_URL}/api/generate")
print(f"Payload: {json.dumps(payload, indent=2)}")
print()
print("Generating...")
print()

try:
    response = requests.post(
        f"{DASHBOARD_URL}/api/generate",
        json=payload,
        timeout=120
    )

    if response.status_code == 200:
        result = response.json()

        print("[OK] Content generated successfully!")
        print()
        print(f"Post ID: {result.get('id')}")
        print(f"Voice Type: {result.get('voice_type')}")
        print(f"Word Count: {len(result.get('content', '').split())} words")
        print()
        print("Content Preview:")
        print("-" * 70)
        print(result.get('content')[:200] + "...")
        print("-" * 70)
        print()

        if result.get('graphic_url'):
            print(f"[OK] Graphic generated: {DASHBOARD_URL}{result['graphic_url']}")
        else:
            print("[WARN] No graphic URL in response")

        print()
        print("="*70)
        print("Test completed successfully!")
        print("="*70)

    else:
        print(f"[ERROR] Request failed with status {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("[ERROR] Could not connect to dashboard")
    print()
    print("Is the dashboard running?")
    print("Start it with: python run_dashboard_8081.py")
    print("Or open: http://localhost:8081")

except Exception as e:
    print(f"[ERROR] {e}")
