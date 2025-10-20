"""
Test Milton's specific Clerk user account
"""

import os
from dotenv import load_dotenv
from clerk_backend_api import Clerk

load_dotenv()

print("="*70)
print("MILTON'S CLERK USER TEST")
print("="*70)
print()

secret_key = os.getenv("CLERK_SECRET_KEY")
user_id = os.getenv("MILTON_USER_ID")

print(f"[INFO] Testing user ID: {user_id}")
print()

clerk = Clerk(bearer_auth=secret_key)

try:
    # Get Milton's user directly
    user = clerk.users.get(user_id=user_id)

    print("[SUCCESS] User found!")
    print()
    print("User Details:")
    print(f"  User ID: {user.id}")

    # Email
    if user.email_addresses and len(user.email_addresses) > 0:
        print(f"  Email: {user.email_addresses[0].email_address}")
    else:
        print(f"  Email: Not set")

    # Name
    if hasattr(user, 'first_name') and user.first_name:
        print(f"  Name: {user.first_name} {user.last_name if hasattr(user, 'last_name') else ''}")

    # Created
    print(f"  Created: {user.created_at}")

    # External accounts (social media connections)
    print()
    print("Connected Social Accounts:")
    if user.external_accounts and len(user.external_accounts) > 0:
        for account in user.external_accounts:
            provider = account.provider.replace('oauth_', '').capitalize()
            print(f"  - {provider}")
            if hasattr(account, 'username'):
                print(f"    Username: {account.username}")
            if hasattr(account, 'access_token') and account.access_token:
                print(f"    Has Token: YES (ready to publish)")
            else:
                print(f"    Has Token: NO (need to connect)")
    else:
        print("  None connected yet")
        print()
        print("  [ACTION NEEDED] Connect social accounts:")
        print("  1. Go to Clerk Dashboard > Users")
        print("  2. Click on your user (Milton Overton)")
        print("  3. Click 'Impersonate' button")
        print("  4. In the impersonated session, connect LinkedIn/Twitter/Instagram")

    print()
    print("="*70)
    print("USER VERIFICATION: SUCCESS")
    print("="*70)
    print()
    print("Next steps:")
    print("1. Configure OAuth providers in Clerk Dashboard:")
    print("   https://dashboard.clerk.com > SSO Connections")
    print()
    print("2. Connect your social media accounts (use 'Impersonate' feature)")
    print()
    print("3. Run this test again to see connected accounts")
    print()

except Exception as e:
    print(f"[ERROR] Failed to get user: {e}")
    print()
    print("Possible issues:")
    print("- User ID may be incorrect")
    print("- User may be in a different Clerk instance")
    print("- API key may not have permission")
    print()
    print("Verify in Clerk Dashboard:")
    print("https://dashboard.clerk.com > Users")
    print()
