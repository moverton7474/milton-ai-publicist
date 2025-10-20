# Instagram Connection - Quick Start Checklist

**45-minute setup to connect Instagram to Milton AI Publicist**

---

## Prerequisites (Check First!)

- [ ] Instagram account is **Business** or **Creator** type (not personal)
- [ ] Instagram is linked to a **Facebook Page**
- [ ] You have **admin access** to both

**Don't have these?** See [INSTAGRAM_CONNECTION_GUIDE.md](INSTAGRAM_CONNECTION_GUIDE.md) for detailed setup.

---

## Part 1: Facebook Developer (20 min)

### 1. Create Facebook App
- [ ] Go to https://developers.facebook.com
- [ ] Create App → **Business** type
- [ ] Name: `Milton AI Publicist`

### 2. Add Instagram Product
- [ ] App Dashboard → **Add Product**
- [ ] Find **Instagram Graph API** → **Set up**

### 3. Configure App
- [ ] Settings → Basic
- [ ] App Domains: `clerk.accounts.dev`
- [ ] Privacy Policy URL: (use KSU's)
- [ ] **Save changes**

### 4. Get Credentials
- [ ] Copy **App ID**: `________________`
- [ ] Copy **App Secret**: `________________`

### 5. Connect Instagram Account
- [ ] Instagram Graph API → **Quickstart**
- [ ] **Add Instagram Business Account**
- [ ] Log in and grant permissions

---

## Part 2: Clerk Integration (15 min)

### 6. Configure Clerk
- [ ] Go to https://dashboard.clerk.com
- [ ] **Social Connections** → **Facebook**
- [ ] **Enable** Facebook
- [ ] Paste App ID and App Secret
- [ ] Add scopes:
  - [ ] `instagram_basic`
  - [ ] `instagram_content_publish`
  - [ ] `pages_show_list`
  - [ ] `pages_read_engagement`
- [ ] **Save**

### 7. Update Facebook OAuth
- [ ] Back to Facebook Developer
- [ ] Instagram Graph API → **Settings**
- [ ] Add OAuth Redirect URI:
  ```
  https://cool-fish-70.clerk.accounts.dev/v1/oauth_callback
  ```
  (Use YOUR Clerk domain from .env)
- [ ] **Save changes**

---

## Part 3: Connect Account (10 min)

### 8. Connect Milton's Instagram
- [ ] Clerk Dashboard → **Users**
- [ ] Find user: `user_34Jc17HoSPgAcmiSO6AtqGuzjo3`
- [ ] Click **Impersonate**
- [ ] Account Settings → **Connected Accounts**
- [ ] Click **Connect** next to Facebook/Instagram
- [ ] Log in and grant ALL permissions
- [ ] Verify "Instagram: Connected" shows

---

## Part 4: Test (5 min)

### 9. Test Post
- [ ] Open dashboard: http://localhost:8081
- [ ] Generate post with graphic (Instagram requires media!)
- [ ] Click **"Publish to LinkedIn"** (publishes to all connected platforms)
- [ ] Check Instagram app - post should appear!

---

## Troubleshooting Quick Fixes

**"Instagram not connected"**
→ Verify Instagram is Business type and linked to Facebook Page

**"Invalid OAuth redirect"**
→ Check Facebook app redirect URI matches Clerk domain exactly

**"Cannot publish"**
→ Always include graphic (Instagram requires image/video)

**"Token expired"**
→ Disconnect and reconnect Instagram in Clerk dashboard

---

## Success Criteria

You're done when:
- ✅ Test post appears on Instagram
- ✅ Caption matches generated text
- ✅ Graphic displays correctly
- ✅ No error messages in dashboard

---

## Your Credentials

**Facebook App**:
- App ID: `________________` (fill in)
- App Secret: `________________` (fill in)
- App URL: https://developers.facebook.com/apps/YOUR_APP_ID

**Clerk**:
- Publishable Key: `pk_test_Y29vbC1maXNoLTcwLmNsZXJrLmFjY291bnRzLmRldiQ` (from .env)
- OAuth Callback: `https://cool-fish-70.clerk.accounts.dev/v1/oauth_callback`

**Milton's User**:
- User ID: `user_34Jc17HoSPgAcmiSO6AtqGuzjo3` (from .env)

---

## Next Steps After Connection

1. **Post regularly**: Instagram algorithm favors consistent posting
2. **Use hashtags**: Add relevant hashtags to captions
3. **Optimize graphics**: Square (1:1) or vertical (4:5) performs best
4. **Track engagement**: Monitor which posts perform best

---

**Need detailed steps?** See [INSTAGRAM_CONNECTION_GUIDE.md](INSTAGRAM_CONNECTION_GUIDE.md)

**Ready?** Start with checklist item #1! ✅
