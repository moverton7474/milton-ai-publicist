"""
Test Clerk API connection
Verifies that Clerk SDK is working and API keys are valid
"""

import os
from dotenv import load_dotenv
from clerk_backend_api import Clerk

load_dotenv()

print("="*70)
print("CLERK CONNECTION TEST")
print("="*70)
print()

# Get API key
secret_key = os.getenv("CLERK_SECRET_KEY")

if not secret_key:
    print("[ERROR] CLERK_SECRET_KEY not found in .env")
    exit(1)

print(f"[OK] Clerk secret key loaded: {secret_key[:20]}...")
print()

# Initialize Clerk
try:
    clerk = Clerk(bearer_auth=secret_key)
    print("[OK] Clerk client initialized")
    print()
except Exception as e:
    print(f"[ERROR] Failed to initialize Clerk: {e}")
    exit(1)

# Test: List users (should be empty or show test users)
try:
    print("[INFO] Fetching users from Clerk...")
    users_response = clerk.users.list()

    if hasattr(users_response, 'data'):
        users = users_response.data
        print(f"[OK] Found {len(users)} user(s) in Clerk")

        if len(users) > 0:
            print()
            print("Users:")
            for user in users:
                email = user.email_addresses[0].email_address if user.email_addresses else 'N/A'
                print(f"  - ID: {user.id}")
                print(f"    Email: {email}")
                print(f"    Created: {user.created_at}")

                # Show connected accounts
                if user.external_accounts and len(user.external_accounts) > 0:
                    print(f"    Connected Accounts: {len(user.external_accounts)}")
                    for account in user.external_accounts:
                        print(f"      - {account.provider}")
                print()
        else:
            print()
            print("[INFO] No users yet. You'll need to sign in first to connect social accounts.")
            print()
            print("Next step:")
            print("Go to: https://cool-fish-70.clerk.accounts.dev")
            print("Sign up with your email, then run this test again.")
    else:
        print(f"[OK] Clerk API responding (no users yet)")

except Exception as e:
    print(f"[ERROR] Clerk API test failed: {e}")
    print()
    print("Possible issues:")
    print("- Secret key may be incorrect")
    print("- Clerk instance may not be active")
    print("- Network connectivity issue")
    print()
    print("Check your Clerk dashboard:")
    print("https://dashboard.clerk.com")
    exit(1)

print()
print("="*70)
print("CLERK CONNECTION: SUCCESS")
print("="*70)
print()
print("Next steps:")
print("1. Configure OAuth providers (LinkedIn, Twitter, Instagram) in Clerk dashboard")
print("   https://dashboard.clerk.com > User & Authentication > Social Connections")
print()
print("2. Sign in to create your user account")
print("   https://cool-fish-70.clerk.accounts.dev")
print()
print("3. Connect social media accounts via OAuth")
print()
