#!/usr/bin/env python3
"""
Quick test script to publish to LinkedIn via Zapier
"""

import requests
import json

# Test the publishing endpoint
url = "http://localhost:8080/api/publish/test/linkedin"

print("Testing LinkedIn publishing via Zapier...")
print(f"Sending request to: {url}")
print()

try:
    response = requests.post(url, timeout=30)

    print(f"Status Code: {response.status_code}")
    print()

    if response.status_code == 200:
        result = response.json()
        print("✅ SUCCESS!")
        print()
        print(json.dumps(result, indent=2))
        print()
        print("Next Steps:")
        print("1. Check Zapier task history: https://zapier.com/app/history")
        print("2. Check your LinkedIn profile for the test post")
        print("3. If you see the post, the integration is working!")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("❌ ERROR: Cannot connect to dashboard")
    print()
    print("Is your dashboard running?")
    print("Start it with: python dashboard/app.py")

except Exception as e:
    print(f"❌ ERROR: {e}")
