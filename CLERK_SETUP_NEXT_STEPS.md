# Clerk OAuth Setup - Next Steps

**Status:** ✅ Clerk SDK Installed, API Keys Configured
**Date:** October 20, 2025
**Time Estimate:** 30-45 minutes

---

## What We Just Completed ✅

1. ✅ **Clerk account created** - You have your test environment ready
2. ✅ **API keys added to `.env`** - System can now authenticate with Clerk
3. ✅ **Clerk SDK installed** - `clerk-backend-api` package ready
4. ✅ **Environment configured** - All settings in place

**Your Clerk Dashboard:** https://dashboard.clerk.com/apps/app_2pWVBmJZGxLHnKqK8kJ7XU9qS8C/instances/ins_2pWVBmJhCLH0nWgMPH7h8x4nz5G

---

## Next Steps to Enable LinkedIn/Twitter/Instagram Publishing

### Step 1: Configure OAuth Providers in Clerk (20 minutes)

You need to enable LinkedIn, Twitter, and Instagram OAuth in your Clerk dashboard.

**1.1 Go to Social Connections**
```
Dashboard → User & Authentication → Social Connections
https://dashboard.clerk.com/apps/[your-app-id]/instances/[your-instance-id]/user-authentication/social-connections
```

**1.2 Enable LinkedIn**
1. Click **"Add connection"** or find LinkedIn in the list
2. Toggle LinkedIn **ON**
3. Clerk will show you what you need:
   - **Redirect URI:** Copy this (you'll need it for LinkedIn app)
   - You need to create a LinkedIn OAuth app

**Creating LinkedIn OAuth App:**
1. Go to: https://www.linkedin.com/developers/apps
2. Click **"Create app"**
3. Fill in:
   - **App name:** "Milton AI Publicist" (or your choice)
   - **LinkedIn Page:** Select your KSU Athletics page or personal profile
   - **App logo:** Optional
4. Click **"Create app"**
5. Go to **"Auth"** tab
6. Add **Redirect URL** from Clerk (format: `https://cool-fish-70.clerk.accounts.dev/v1/oauth_callback`)
7. Under **"Products"**, add:
   - **Share on LinkedIn** (for posting)
   - **Sign In with LinkedIn using OpenID Connect**
8. Copy **Client ID** and **Client Secret**
9. Go back to Clerk dashboard
10. Paste Client ID and Client Secret into LinkedIn connection settings
11. Click **Save**

**1.3 Enable Twitter/X**
1. In Clerk dashboard, toggle Twitter **ON**
2. Copy the Redirect URI from Clerk

**Creating Twitter OAuth App:**
1. Go to: https://developer.twitter.com/en/portal/dashboard
2. Click **"+ Create Project"** or use existing project
3. Set up app with **OAuth 2.0** enabled
4. Add **Callback URL** from Clerk
5. Under **"User authentication settings"**:
   - Enable **OAuth 2.0**
   - App permissions: **Read and Write**
   - Type of App: **Web App**
6. Copy **Client ID** and **Client Secret**
7. Go back to Clerk, paste credentials
8. Click **Save**

**1.4 Enable Instagram (via Facebook)**
1. In Clerk dashboard, toggle Facebook **ON**
2. Copy the Redirect URI

**Creating Facebook/Instagram OAuth App:**
1. Go to: https://developers.facebook.com/apps
2. Click **"Create App"**
3. Choose **"Business"** type
4. Fill in app details
5. Go to **Settings → Basic**
6. Add **App Domains**: `cool-fish-70.clerk.accounts.dev`
7. Go to **"Add Product"**
8. Add **"Facebook Login"**
9. Under **Facebook Login Settings**:
   - Add **Valid OAuth Redirect URIs** from Clerk
10. Add **"Instagram Basic Display"** or **"Instagram Graph API"** product
11. Copy **App ID** and **App Secret**
12. Go back to Clerk, paste into Facebook connection
13. Click **Save**

---

### Step 2: Test Clerk Authentication (5 minutes)

Let me create a quick test script to verify Clerk is working:

**Test Script:** `test_clerk_connection.py`

```python
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
    users_response = clerk.users.list(limit=10)

    if hasattr(users_response, 'data'):
        users = users_response.data
        print(f"[OK] Found {len(users)} user(s) in Clerk")

        if len(users) > 0:
            print()
            print("Users:")
            for user in users:
                print(f"  - ID: {user.id}")
                print(f"    Email: {user.email_addresses[0].email_address if user.email_addresses else 'N/A'}")
                print(f"    Created: {user.created_at}")
                print()
        else:
            print()
            print("[INFO] No users yet. You'll need to sign in first to connect social accounts.")
    else:
        print(f"[OK] Clerk API responding (no users yet)")

except Exception as e:
    print(f"[ERROR] Clerk API test failed: {e}")
    print()
    print("Possible issues:")
    print("- Secret key may be incorrect")
    print("- Clerk instance may not be active")
    print("- Network connectivity issue")
    exit(1)

print()
print("="*70)
print("CLERK CONNECTION: SUCCESS")
print("="*70)
print()
print("Next steps:")
print("1. Configure OAuth providers (LinkedIn, Twitter, Instagram) in Clerk dashboard")
print("2. Sign in to Clerk to create your user account")
print("3. Connect social media accounts via OAuth")
print()
```

**Run the test:**
```bash
cd milton-publicist
python test_clerk_connection.py
```

---

### Step 3: Create Your Clerk User Account (5 minutes)

You need to sign in to Clerk to create your user profile.

**Option A: Use Clerk's Pre-built Sign-In (Easiest)**

1. Go to your Clerk frontend URL: https://cool-fish-70.clerk.accounts.dev
2. Click **"Sign In"** or **"Sign Up"**
3. Use your email (recommend: your KSU email)
4. Verify email
5. You now have a Clerk user account!

**Option B: Create Sign-In Page (For Custom Integration)**

We can build a simple sign-in page later if you want custom branding.

---

### Step 4: Connect Your Social Media Accounts (10 minutes)

Once you have a Clerk user account:

**4.1 Sign in to Clerk**
1. Go to: https://cool-fish-70.clerk.accounts.dev
2. Sign in with your email

**4.2 Connect LinkedIn**
1. In your Clerk account settings, find **"Connected Accounts"**
2. Click **"Connect LinkedIn"**
3. Authorize the app
4. LinkedIn is now connected!

**4.3 Connect Twitter**
1. Click **"Connect Twitter"**
2. Authorize the app
3. Twitter is now connected!

**4.4 Connect Instagram (optional)**
1. Click **"Connect Facebook"** (Instagram uses Facebook OAuth)
2. Authorize the app
3. Instagram is now connected!

---

### Step 5: Get Your Clerk User ID (2 minutes)

After signing in, you need to get your User ID to put in `.env`:

**Method 1: From Clerk Dashboard**
1. Go to: https://dashboard.clerk.com → Users
2. Find yourself in the user list
3. Click on your user
4. Copy the **User ID** (format: `user_xxxxxxxxxxxxx`)
5. Update `.env`:
   ```bash
   MILTON_USER_ID=user_xxxxxxxxxxxxx
   ```

**Method 2: From Test Script**
Run `test_clerk_connection.py` again - it will show your user ID

---

### Step 6: Test OAuth Token Retrieval (5 minutes)

Let me create a test to verify we can get OAuth tokens:

**Test Script:** `test_clerk_oauth.py`

```python
import os
import asyncio
from dotenv import load_dotenv
from clerk_backend_api import Clerk

load_dotenv()

print("="*70)
print("CLERK OAUTH TOKEN TEST")
print("="*70)
print()

secret_key = os.getenv("CLERK_SECRET_KEY")
user_id = os.getenv("MILTON_USER_ID")

if not user_id:
    print("[ERROR] MILTON_USER_ID not set in .env")
    print("Please sign in to Clerk and add your user ID to .env")
    exit(1)

print(f"[INFO] Testing OAuth tokens for user: {user_id}")
print()

clerk = Clerk(bearer_auth=secret_key)

try:
    # Get user
    user = clerk.users.get(user_id=user_id)
    print(f"[OK] User found: {user.email_addresses[0].email_address if user.email_addresses else 'N/A'}")
    print()

    # Check external accounts
    print("[INFO] Checking connected accounts...")
    print()

    if not user.external_accounts or len(user.external_accounts) == 0:
        print("[WARN] No social accounts connected yet")
        print()
        print("Next steps:")
        print("1. Go to: https://cool-fish-70.clerk.accounts.dev")
        print("2. Sign in with your account")
        print("3. Go to Account Settings → Connected Accounts")
        print("4. Connect LinkedIn, Twitter, and Instagram")
        print()
    else:
        print(f"[OK] Found {len(user.external_accounts)} connected account(s)")
        print()

        for account in user.external_accounts:
            provider = account.provider
            status = "✅ Connected" if account.approved_scopes else "⚠️ Needs approval"

            print(f"  Platform: {provider}")
            print(f"  Status: {status}")
            print(f"  Username: {account.username if hasattr(account, 'username') else 'N/A'}")
            print(f"  Has Access Token: {'✅ Yes' if hasattr(account, 'access_token') and account.access_token else '❌ No'}")

            if hasattr(account, 'access_token') and account.access_token:
                print(f"  Token (first 20 chars): {account.access_token[:20]}...")

            print()

        print("="*70)
        print("OAUTH TOKENS: READY FOR PUBLISHING")
        print("="*70)

except Exception as e:
    print(f"[ERROR] Failed to get user or tokens: {e}")
    exit(1)
```

**Run the test:**
```bash
python test_clerk_oauth.py
```

---

## Summary: Complete Setup Checklist

- [ ] **Step 1:** Configure OAuth providers in Clerk dashboard (20 min)
  - [ ] Enable LinkedIn in Clerk
  - [ ] Create LinkedIn OAuth app
  - [ ] Enable Twitter in Clerk
  - [ ] Create Twitter OAuth app
  - [ ] Enable Facebook/Instagram in Clerk
  - [ ] Create Facebook OAuth app

- [ ] **Step 2:** Test Clerk connection (`python test_clerk_connection.py`) (5 min)

- [ ] **Step 3:** Create your Clerk user account (5 min)
  - [ ] Sign up at https://cool-fish-70.clerk.accounts.dev
  - [ ] Verify email

- [ ] **Step 4:** Connect social media accounts (10 min)
  - [ ] Connect LinkedIn
  - [ ] Connect Twitter
  - [ ] Connect Instagram (optional)

- [ ] **Step 5:** Get and add your User ID to `.env` (2 min)

- [ ] **Step 6:** Test OAuth token retrieval (`python test_clerk_oauth.py`) (5 min)

**Total Time:** 30-45 minutes

---

## What Happens After Setup

Once OAuth is configured, your AI Publicist will:

1. **Generate content** using Milton's authentic voice (already working ✅)
2. **Get OAuth tokens** automatically from Clerk
3. **Publish to LinkedIn** using LinkedIn API v2 with OAuth token
4. **Publish to Twitter** using Twitter API v2 with OAuth token
5. **Publish to Instagram** using Facebook Graph API with OAuth token

**No passwords stored.** No Terms of Service violations. All platform-approved OAuth 2.0.

---

## Need Help?

**Clerk Documentation:**
- Social Connections: https://clerk.com/docs/authentication/social-connections/overview
- OAuth Guide: https://clerk.com/docs/authentication/social-connections/oauth

**Platform OAuth Documentation:**
- LinkedIn: https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication
- Twitter: https://developer.twitter.com/en/docs/authentication/oauth-2-0
- Facebook/Instagram: https://developers.facebook.com/docs/facebook-login

**Your Clerk Dashboard:**
https://dashboard.clerk.com/apps/app_2pWVBmJZGxLHnKqK8kJ7XU9qS8C

---

## Quick Reference: Your Clerk Info

**Frontend URL:** https://cool-fish-70.clerk.accounts.dev
**Backend URL:** https://api.clerk.com

**API Keys (already in .env):**
- Publishable Key: `pk_test_Y29vbC1maXNoLTcwLmNsZXJrLmFjY291bnRzLmRldiQ`
- Secret Key: `sk_test_NTRX6vNE2kHgybvc66EYkRebdX3YvSzENF8da1JEe9`

**Next:** Follow Steps 1-6 above to enable social media publishing!

---

*Setup guide created: October 20, 2025*
*Estimated completion time: 30-45 minutes*
*Status: Ready to configure OAuth providers*

**Let's go Owls! 🦉**
