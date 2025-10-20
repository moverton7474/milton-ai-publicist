# Connect Instagram to Milton AI Publicist

Complete step-by-step guide to connect your Instagram account and start posting automatically.

**Time Required**: 45-60 minutes
**Prerequisites**: Instagram Business Account (required for API access)

---

## Overview

Instagram posting requires:
1. **Instagram Business Account** (not personal account)
2. **Facebook Page** (Instagram must be linked to it)
3. **Facebook Developer App** (for API access)
4. **Clerk OAuth** (for secure authentication)

The Milton AI Publicist already has the code built - you just need to configure OAuth.

---

## Prerequisites Check

### ✅ Step 1: Verify Your Instagram Account Type

Instagram API only works with **Business** or **Creator** accounts, not personal accounts.

**Check your account type**:
1. Open Instagram app on your phone
2. Go to your profile
3. Tap the menu (☰) → **Settings**
4. Look for **"Account"** → **"Switch to Professional Account"**

**If you see "Switch Back to Personal"**:
- ✅ You have a Business/Creator account - proceed!

**If you see "Switch to Professional Account"**:
- ❌ You have a personal account
- **Action**: Tap "Switch to Professional Account"
- Choose "Business" (recommended for KSU Athletics)
- Follow the setup wizard

---

### ✅ Step 2: Link Instagram to Facebook Page

Instagram Business accounts must be connected to a Facebook Page.

**Check if already linked**:
1. Instagram app → Profile → Menu (☰)
2. **Settings** → **Account Center**
3. Look for your Facebook Page listed

**If not linked**:
1. Create a Facebook Page:
   - Go to https://www.facebook.com/pages/create
   - Choose "Community or Public Figure"
   - Name: "Kennesaw State Athletics" (or your preference)
   - Category: "Sports"
   - Complete setup

2. Link Instagram to Facebook Page:
   - Instagram → Settings → Account Center
   - **Add accounts** → **Add Facebook Page**
   - Log in and select your KSU Athletics page
   - Grant permissions

---

## Part 1: Facebook Developer Setup (20 minutes)

### Step 1: Create Facebook App

1. Go to **https://developers.facebook.com**
2. Click **"My Apps"** (top right)
3. Click **"Create App"**

**App Setup**:
- **Use case**: Select **"Other"**
- **App type**: Select **"Business"**
- Click **"Next"**

**App Details**:
- **App name**: `Milton AI Publicist`
- **Contact email**: Your email
- Click **"Create App"**

**You'll see**: App Dashboard

---

### Step 2: Add Instagram Graph API Product

1. In your new app dashboard, scroll to **"Add products to your app"**
2. Find **"Instagram Graph API"**
3. Click **"Set up"**

**You'll see**: Instagram Graph API settings page

---

### Step 3: Configure App Settings

1. Left sidebar → **Settings** → **Basic**

2. Fill in required fields:
   - **App Domains**: `clerk.accounts.dev`
   - **Privacy Policy URL**: `https://your-domain.com/privacy` (use KSU Athletics privacy policy)
   - **Terms of Service URL**: `https://your-domain.com/terms` (optional)
   - **Category**: Choose "Sports"

3. Click **"Save Changes"** (bottom of page)

---

### Step 4: Get App Credentials

Still in **Settings** → **Basic**:

1. **Copy** these values (you'll need them for Clerk):
   - **App ID**: (e.g., `1234567890123456`)
   - **App Secret**: Click **"Show"**, then copy

**Keep these secure!** They're like passwords for your app.

---

### Step 5: Configure OAuth Settings

1. Left sidebar → **Instagram Graph API** → **Settings**

2. Add OAuth Redirect URIs:
   ```
   https://your-clerk-domain.clerk.accounts.dev/v1/oauth_callback
   ```
   (Replace `your-clerk-domain` with your actual Clerk subdomain from next section)

3. Add **Valid OAuth Redirect URIs**:
   - Same URL as above

4. Click **"Save Changes"**

---

### Step 6: Connect Your Instagram Business Account

1. Left sidebar → **Instagram Graph API** → **Quickstart**

2. Click **"Add Instagram Business Account"**

3. **Log in with Facebook** (the one connected to your Instagram Business account)

4. **Select your Facebook Page** that's linked to Instagram

5. Grant all requested permissions

**You'll see**: Your Instagram account listed in the app

---

## Part 2: Clerk Integration (15 minutes)

### Step 7: Access Your Clerk Dashboard

1. Go to **https://dashboard.clerk.com**

2. Log in with your account

3. Select your **Milton AI Publicist** application
   (Or create one if you haven't yet)

Your Clerk publishable key is in your `.env` file:
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_Y29vbC1maXNoLTcwLmNsZXJrLmFjY291bnRzLmRldiQ
```

This shows your Clerk domain is: `cool-fish-70.clerk.accounts.dev`

---

### Step 8: Enable Facebook/Instagram in Clerk

1. Clerk Dashboard → **User & Authentication** → **Social Connections**

2. Find **"Facebook"** (Instagram uses Facebook OAuth)

3. Click **"Enable"** or gear icon to configure

4. **Add credentials** from Facebook app:
   - **Client ID**: Paste your Facebook App ID (from Step 4)
   - **Client Secret**: Paste your Facebook App Secret (from Step 4)

5. **Configure scopes** (very important!):
   Click **"Add scope"** and add:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`

6. Click **"Save"**

---

### Step 9: Update OAuth Redirect in Facebook

Now that you have your Clerk OAuth callback URL, update Facebook app:

1. Back to **https://developers.facebook.com** → Your App

2. Instagram Graph API → **Settings**

3. **Valid OAuth Redirect URIs**: Add:
   ```
   https://cool-fish-70.clerk.accounts.dev/v1/oauth_callback
   ```
   (Use YOUR actual Clerk domain from .env)

4. Save changes

---

## Part 3: Connect Your Instagram Account (10 minutes)

### Step 10: Get Milton's User ID

You need Milton's Clerk User ID to connect social accounts.

**From your .env file**:
```bash
MILTON_USER_ID=user_34Jc17HoSPgAcmiSO6AtqGuzjo3
```

✅ You already have this!

---

### Step 11: Impersonate Milton's Account

**Via Clerk Dashboard**:

1. Clerk Dashboard → **Users**

2. Find user with ID: `user_34Jc17HoSPgAcmiSO6AtqGuzjo3`
   (Search by User ID)

3. Click on the user

4. Click **"Impersonate"** button (top right)

**You'll be logged in as Milton**

---

### Step 12: Connect Instagram

While impersonated as Milton:

1. Go to **Account Settings** (Clerk user portal)

2. Look for **"Connected Accounts"** or **"Social Connections"**

3. Find **"Facebook"** / **"Instagram"**

4. Click **"Connect"**

5. **Facebook OAuth Flow**:
   - Log in to Facebook (the one linked to Instagram Business)
   - Grant all permissions
   - **IMPORTANT**: When asked for Instagram permissions, **grant them all**

6. You'll be redirected back

**Success**: Instagram should now show as "Connected"

---

## Part 4: Test Instagram Posting (5 minutes)

### Step 13: Test Via Dashboard

1. Open Milton AI Publicist Dashboard: **http://localhost:8081**

2. Generate a test post:
   - Voice: Personal
   - Scenario: Partner Appreciation
   - Context: "Test Instagram posting"
   - ✅ Check "Generate Branded Graphic" (Instagram requires media!)

3. Click **"Generate Content"**

4. In preview panel, click **"Publish to LinkedIn"** button

**Behind the scenes**: The system will attempt to publish to all connected platforms

---

### Step 14: Verify Instagram Post

1. Open Instagram on your phone or web

2. Check your KSU Athletics Instagram Business account

3. Look for your test post

**Expected**:
- Post should appear in your feed
- Caption matches generated text
- Branded graphic with KSU logo included

---

## Troubleshooting

### Issue: "Instagram not connected"

**Possible causes**:
1. Instagram Business account not linked to Facebook Page
2. Facebook Page not added to Facebook app
3. OAuth scopes missing in Clerk

**Solution**:
- Verify Facebook Page is linked to Instagram (Instagram app → Account Center)
- In Facebook Developer app → Instagram Graph API → Add your Facebook Page
- In Clerk → Facebook settings → Add all required scopes

---

### Issue: "Invalid OAuth redirect URI"

**Cause**: Facebook app redirect URI doesn't match Clerk's

**Solution**:
1. Check your Clerk domain in .env: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_***`
2. Extract domain: `cool-fish-70.clerk.accounts.dev`
3. Facebook app → Instagram Settings → Valid OAuth Redirect URIs:
   ```
   https://cool-fish-70.clerk.accounts.dev/v1/oauth_callback
   ```

---

### Issue: "App not approved for Instagram"

**Cause**: Facebook app is in Development mode

**Solution**:
This is normal! For testing with your own account, Development mode is fine.

**For production** (posting on behalf of other users):
1. Facebook app → App Review → Request Instagram permissions
2. Submit for review with use case documentation
3. Wait 2-5 days for approval

**But for Milton's personal use**: Development mode works perfectly!

---

### Issue: "Cannot publish to Instagram"

**Possible causes**:
1. No media attached (Instagram requires image/video)
2. Image URL not publicly accessible
3. Instagram account is still Personal (not Business)

**Solution**:
- Always generate branded graphic when posting to Instagram
- Ensure graphics are served via HTTP (not file://)
- Verify Instagram account is Business type

---

### Issue: "Token expired"

**Cause**: Instagram access tokens expire after 60 days

**Solution**:
- Disconnect and reconnect Instagram in Clerk dashboard
- Implement token refresh (I can add this if needed)

---

## Instagram API Limits

### Rate Limits

**Per user**:
- 25 posts per day
- 200 API calls per hour

**Best practices**:
- Don't spam posts (rate limited at 25/day anyway)
- Space posts throughout the day
- Instagram penalizes rapid posting

---

## Technical Details

### How It Works

**1. OAuth Flow** (one-time setup):
```
User clicks "Connect Instagram"
  ↓
Clerk redirects to Facebook OAuth
  ↓
User grants Instagram permissions
  ↓
Facebook returns access token
  ↓
Clerk stores encrypted token
```

**2. Publishing Flow** (each post):
```
Generate content + graphic
  ↓
Get Instagram access token from Clerk
  ↓
Upload graphic to Instagram (container)
  ↓
Publish container with caption
  ↓
Return published post ID
```

---

### Code Reference

**Instagram publisher**: `module_iii/social_media_publisher.py`

**Method**: `publish_to_instagram(caption, image_url)`

**Instagram Graph API endpoints used**:
- `https://graph.facebook.com/v18.0/{ig_account}/media` (create container)
- `https://graph.facebook.com/v18.0/{ig_account}/media_publish` (publish)

---

## Success Checklist

Before considering setup complete, verify:

- [ ] Instagram account is Business type (not personal)
- [ ] Instagram is linked to Facebook Page
- [ ] Facebook Page added to Facebook Developer app
- [ ] Facebook app has Instagram Graph API enabled
- [ ] OAuth redirect URI matches Clerk domain
- [ ] Facebook app credentials added to Clerk
- [ ] All Instagram scopes enabled in Clerk
- [ ] Milton's Clerk account connected to Instagram
- [ ] Test post published successfully to Instagram
- [ ] Graphic appears correctly in Instagram post

---

## What Happens After Setup

Once connected, the Milton AI Publicist will automatically:

1. **Generate post** with Milton's authentic voice
2. **Create branded graphic** with KSU colors + logos
3. **Publish to Instagram** with one click
4. **Include caption** optimized for Instagram (emojis, hashtags)
5. **Track engagement** (coming soon)

**All from the dashboard!**

---

## Next Steps After Connection

### Immediate

1. **Test posting**: Generate 2-3 test posts to verify everything works
2. **Delete test posts**: Remove from Instagram after verification
3. **Create content calendar**: Plan your Instagram strategy

### Short-term

1. **Customize captions**: Instagram benefits from emojis and hashtags
2. **Optimize graphics**: Instagram prefers square (1:1) or vertical (4:5)
3. **Post timing**: Schedule posts for peak engagement times

### Optional

1. **Instagram Stories**: Add story posting capability (I can build this)
2. **Instagram Reels**: Add video posting for Reels
3. **Auto-hashtags**: Automatically add relevant hashtags
4. **Engagement tracking**: Monitor likes, comments, shares

---

## Summary

**Setup Complete When**:
- ✅ Instagram Business account linked to Facebook Page
- ✅ Facebook Developer app created and configured
- ✅ Clerk OAuth integration enabled
- ✅ Milton's account connected via Clerk
- ✅ Test post published successfully

**Time Investment**: 45-60 minutes (one-time setup)

**Ongoing**: Zero maintenance - just post!

**Cost**: FREE (Instagram API has no fees)

---

## Support

**Issues with setup?**

1. **Check logs**: Dashboard shows detailed error messages
2. **Review checklist**: Verify each step completed
3. **Common fix**: Disconnect and reconnect in Clerk
4. **Facebook support**: https://developers.facebook.com/support

**Need help?** Let me know which step is causing issues!

---

**Ready to connect Instagram?** Start with Step 1 and follow each step carefully!

**Let's Go Owls! 🦉📸**
