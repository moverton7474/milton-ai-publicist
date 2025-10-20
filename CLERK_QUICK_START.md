# Clerk Quick Start - Create User & Connect Social Accounts

**Estimated Time:** 15 minutes
**Date:** October 20, 2025

---

## Issue: Frontend URL Shows Blank Page

The URL `https://cool-fish-70.clerk.accounts.dev` shows a blank page because we haven't set up the sign-in UI component.

**Solution:** Create your user account directly in the Clerk Dashboard instead.

---

## Quick Setup (15 minutes)

### Step 1: Create User via Clerk Dashboard (2 minutes)

**1.1 Go to Clerk Dashboard**
- URL: https://dashboard.clerk.com
- Sign in with your Clerk account

**1.2 Navigate to Users**
- Click **"Users"** in the left sidebar
- You should see an empty list (or test users)

**1.3 Create Your User**
- Click **"+ Create user"** button (top right)
- Fill in:
  - **Email address:** Your KSU email (e.g., `moverton@kennesaw.edu`)
  - **First name:** Milton
  - **Last name:** Overton
  - **Password:** Create a password (you'll use this to sign in later)
- Click **"Create user"**

**1.4 Get Your User ID**
- Click on the newly created user in the list
- At the top of the user details page, you'll see **User ID**
- Copy it (format: `user_2xxxxxxxxxxxxx`)
- Keep this handy for the next step

### Step 2: Add User ID to .env (1 minute)

**2.1 Update .env file**

Open your `.env` file at:
```
c:\Users\mover\OneDrive\Documents\GitHub\All State RevShield Engine AJ\milton-publicist\.env
```

Find this line:
```bash
MILTON_USER_ID=
```

Replace with your actual User ID:
```bash
MILTON_USER_ID=user_2xxxxxxxxxxxxx
```

Save the file.

**2.2 Test the connection**

Run this to verify:
```bash
cd milton-publicist
python test_clerk_connection.py
```

You should see:
```
[OK] Found 1 user(s) in Clerk
  - ID: user_2xxxxxxxxxxxxx
    Email: moverton@kennesaw.edu
    Created: 2025-10-20...
```

---

### Step 3: Configure OAuth Providers in Clerk (10 minutes)

Now that you have a user account, let's set up LinkedIn, Twitter, and Instagram OAuth.

**3.1 Enable OAuth Providers**

In Clerk Dashboard:
- Go to: **Configure** → **SSO Connections** (left sidebar)
- Or direct URL: https://dashboard.clerk.com → Your app → SSO connections

**3.2 Add LinkedIn**

1. Find **LinkedIn** in the providers list
2. Toggle it **ON**
3. Clerk will show you:
   - **Authorized redirect URI** (copy this)
   - Fields for Client ID and Client Secret

**3.3 Create LinkedIn OAuth App**

1. Open new tab: https://www.linkedin.com/developers/apps
2. Click **"Create app"**
3. Fill in:
   - **App name:** "Milton AI Publicist" (or your choice)
   - **LinkedIn Page:** Select KSU Athletics page (or create one)
   - **Privacy policy URL:** `https://kennesaw.edu/privacy` (or your choice)
   - **App logo:** Optional (upload KSU or personal logo)
4. Click **"Create app"**
5. Go to **"Auth"** tab
6. Under **"OAuth 2.0 settings"**:
   - Click **"Add redirect URL"**
   - Paste the **Authorized redirect URI** from Clerk
   - Click **"Add"**
7. Under **"Products"**, click **"Request access"** for:
   - **Sign In with LinkedIn using OpenID Connect**
   - **Share on LinkedIn** (for posting)
   - **Marketing Developer Platform** (optional, for analytics)
8. Copy **Client ID** and **Client Secret** from the **"Auth"** tab
9. Go back to Clerk dashboard
10. Paste **Client ID** and **Client Secret** into LinkedIn connection
11. Click **"Save"**

**3.4 Add Twitter (Optional - if you want Twitter publishing)**

1. In Clerk, toggle **Twitter** ON
2. Copy the redirect URI
3. Go to: https://developer.twitter.com/en/portal/dashboard
4. Click **"Create Project"** or select existing
5. Create new app or select existing
6. Go to **"User authentication settings"**
7. Enable **OAuth 2.0**
8. Set **App permissions** to **Read and write**
9. Add **Callback URI** from Clerk
10. Copy **Client ID** and **Client Secret**
11. Paste into Clerk Twitter connection
12. Click **"Save"**

**3.5 Add Instagram (Optional - if you want Instagram publishing)**

1. In Clerk, toggle **Facebook** ON (Instagram uses Facebook OAuth)
2. Copy the redirect URI
3. Go to: https://developers.facebook.com/apps
4. Click **"Create App"**
5. Choose **"Business"** type
6. Fill in app details
7. Go to **Settings → Basic**
8. Add **App Domains**: `clerk.accounts.dev`
9. Click **"Add Product"** → **"Facebook Login"**
10. Add **Valid OAuth Redirect URIs** from Clerk
11. Add **"Instagram Basic Display"** product
12. Copy **App ID** and **App Secret**
13. Paste into Clerk Facebook connection
14. Click **"Save"**

---

### Step 4: Connect Your Social Accounts (2 minutes)

Now that OAuth providers are configured, connect your actual social media accounts.

**Option A: Via Clerk User Impersonation (Recommended)**

1. In Clerk Dashboard → Users
2. Click on your user (Milton Overton)
3. Click **"Impersonate"** button (top right)
4. This will sign you in as yourself
5. Go to **Account** settings
6. Under **"Connected accounts"**, click:
   - **"Connect LinkedIn"**
   - **"Connect Twitter"** (if configured)
   - **"Connect Instagram"** (if configured)
7. Authorize each platform

**Option B: Manual OAuth Flow**

If impersonation doesn't work, we can create a simple sign-in page. Let me know if you need this.

---

### Step 5: Verify Connections (1 minute)

Run the connection test:

```bash
cd milton-publicist
python -m module_iii.clerk_auth
```

Expected output:
```
==================================================================
CLERK OAUTH AUTHENTICATION TEST
==================================================================

[OK] Clerk auth initialized for user: user_2xxxxxxxxxxxxx

[INFO] Checking social media connections...
  [CONNECTED] LinkedIn
  [NOT CONNECTED] Twitter
  [NOT CONNECTED] Instagram

[INFO] User Information:
  Email: moverton@kennesaw.edu
  Connected Accounts: 1

[OK] LinkedIn token retrieved: ya29.Gl0xxxxxxxxxxxxx...
```

---

## Troubleshooting

### Issue: "User not found" error

**Solution:**
1. Make sure you added `MILTON_USER_ID` to `.env`
2. Restart any running Python scripts
3. Re-run `python test_clerk_connection.py`

### Issue: LinkedIn connection shows but no token

**Solution:**
1. In Clerk Dashboard → Users → Your user
2. Click on the LinkedIn connection
3. Click **"Reconnect"** or **"Refresh token"**
4. Re-authorize if needed

### Issue: "Invalid redirect URI" when connecting

**Solution:**
1. Double-check the redirect URI in LinkedIn/Twitter/Facebook app matches exactly what Clerk shows
2. No trailing slashes
3. HTTPS required (Clerk provides this automatically)

---

## Summary Checklist

- [ ] Step 1: Created user in Clerk Dashboard
- [ ] Step 2: Added MILTON_USER_ID to .env
- [ ] Step 3: Configured OAuth providers (LinkedIn, Twitter, Instagram)
- [ ] Step 4: Connected social media accounts
- [ ] Step 5: Verified connections work

**Total Time:** ~15 minutes
**Status after completion:** Ready to publish posts!

---

## What's Next?

Once you complete these steps, you can:

1. **Test LinkedIn publishing:**
   ```python
   python -m module_iii.social_media_publisher
   ```

2. **Generate and publish a post:**
   ```python
   # Generate content
   python test_dual_voice.py

   # Publish it (we'll create this script next)
   python publish_test_post.py
   ```

3. **Build the approval dashboard** (next development phase)

---

**Need help?** If you get stuck on any step, let me know which step and what error you're seeing.

**Let's Go Owls! 🦉**
