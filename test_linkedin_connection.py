"""
LinkedIn Connection Test Script
Tests the Zapier webhook connection for LinkedIn publishing

Usage:
    python test_linkedin_connection.py
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_linkedin_connection():
    """Test the LinkedIn Zapier webhook connection"""

    print("=" * 60)
    print("MILTON AI PUBLICIST - LINKEDIN CONNECTION TEST")
    print("=" * 60)
    print()

    # Get webhook URL from environment
    webhook_url = os.getenv('ZAPIER_LINKEDIN_WEBHOOK')

    # Check if webhook is configured
    if not webhook_url or 'XXXXX' in webhook_url:
        print("[X] ERROR: Zapier webhook not configured!")
        print()
        print("Steps to fix:")
        print("1. Go to https://zapier.com/")
        print("2. Create a new Zap with Webhooks trigger")
        print("3. Copy the webhook URL")
        print("4. Update your .env file:")
        print("   ZAPIER_LINKEDIN_WEBHOOK=https://hooks.zapier.com/hooks/catch/YOUR_ID/")
        print()
        print("See LINKEDIN_ZAPIER_SETUP_GUIDE.md for detailed instructions")
        return False

    print(f"[OK] Webhook URL found: {webhook_url[:50]}...")
    print()

    # Create test post data
    test_data = {
        "content": f"🧪 Test post from Milton AI Publicist\n\nThis is an automated test post to verify the LinkedIn integration is working correctly.\n\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n#TestPost #MiltonAI",
        "platform": "linkedin",
        "user_id": "milton_overton",
        "post_id": "test_001",
        "timestamp": datetime.now().isoformat(),
        "test_mode": True
    }

    print("Test post content:")
    print("-" * 60)
    print(test_data['content'])
    print("-" * 60)
    print()

    # Send test request to Zapier
    print("Sending test request to Zapier...")

    try:
        response = requests.post(
            webhook_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        print()

        if response.status_code == 200:
            print("[SUCCESS] Webhook request sent successfully!")
            print()
            print("Next steps:")
            print("1. Go to Zapier.com → Your Zaps → Task History")
            print("2. You should see this test request in the history")
            print("3. Check if your LinkedIn Company Page shows the test post")
            print("4. If you see the post on LinkedIn, the integration is working!")
            print()
            print("Note: It may take 10-30 seconds for the post to appear on LinkedIn")
            return True
        else:
            print(f"[WARNING] Unexpected response code: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("[X] ERROR: Request timed out")
        print("This usually means:")
        print("- The webhook URL is incorrect")
        print("- Zapier is down (unlikely)")
        print("- Network connectivity issue")
        return False

    except requests.exceptions.RequestException as e:
        print(f"[X] ERROR: Request failed: {e}")
        print()
        print("Common issues:")
        print("- Invalid webhook URL in .env file")
        print("- No internet connection")
        print("- Firewall blocking the request")
        return False

def check_environment():
    """Check if all required environment variables are set"""

    print("Checking environment configuration...")
    print()

    required_vars = {
        'ZAPIER_LINKEDIN_WEBHOOK': 'LinkedIn webhook URL',
        'DASHBOARD_BASE_URL': 'Dashboard base URL'
    }

    all_configured = True

    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and 'XXXXX' not in value:
            print(f"[OK] {var}: Configured")
        else:
            print(f"[X] {var}: NOT configured")
            all_configured = False

    print()
    return all_configured

def main():
    """Main test function"""

    # Check environment
    env_ok = check_environment()

    if not env_ok:
        print("Please configure your environment variables in .env file")
        print("See LINKEDIN_ZAPIER_SETUP_GUIDE.md for instructions")
        return

    # Test connection
    success = test_linkedin_connection()

    if success:
        print()
        print("=" * 60)
        print("TEST COMPLETE - Integration appears to be working!")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("TEST FAILED - Please check the errors above")
        print("=" * 60)

if __name__ == "__main__":
    main()
