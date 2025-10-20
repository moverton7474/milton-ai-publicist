# Clerk OAuth Redirect URI Setup

**IMPORTANT**: You need to add these Redirect URIs to your Clerk OAuth application before OAuth will work.

---

## Step-by-Step Instructions

### 1. Go to Clerk Dashboard
- You're already there: https://dashboard.clerk.com
- Your application: **Milton AI Agent Publicist**

### 2. Scroll Down to "Redirect URIs"
On the page you're currently viewing, scroll down to find the **"Redirect URIs"** section.

### 3. Add These Three Redirect URIs

Click "Add URI" and enter each of these URLs:

```
http://localhost:8080/auth/callback/linkedin
http://localhost:8080/auth/callback/twitter
http://localhost:8080/auth/callback/instagram
```

**Screenshot shows**: You need to enter these in the blank "Enter URI" field and click "Add URI" button.

### 4. Save Changes
Click the "Save" or "Update" button at the bottom of the page.

---

## What These URIs Do

When a user clicks "Connect LinkedIn" in the settings page:
1. Browser redirects to Clerk OAuth page
2. User authorizes on LinkedIn
3. **Clerk redirects back to your app** at: `http://localhost:8080/auth/callback/linkedin`
4. Your app receives the authorization code
5. Shows success page

**Without these redirect URIs configured**, Clerk will reject the OAuth request with an error like:
- "Invalid redirect_uri"
- "Redirect URI not whitelisted"

---

## Your Clerk OAuth Configuration

**Found in your screenshots:**

- **Client ID**: `mhOx7MwgWEvvYqkm`
- **Client Secret**: `UoN7Ka143jcUfVyVWlatiS6xjUGTpkLi`
- **Authorize URL**: `https://cool-fish-70.clerk.accounts.dev/oauth/authorize`
- **Token URL**: `https://cool-fish-70.clerk.accounts.dev/oauth/token`

✅ **Already configured in app.py** (lines 100-110)

---

## After Adding Redirect URIs

1. **Restart the dashboard** (if running):
   ```bash
   # Press Ctrl+C to stop, then:
   python dashboard/app.py
   ```

2. **Test OAuth flow**:
   - Go to http://localhost:8080/settings
   - Click "🔗 Connect LinkedIn"
   - Should redirect to Clerk OAuth page
   - Authorize
   - Should redirect back to success page

---

## For Production Deployment

When deploying to production (not localhost), add production redirect URIs:

```
https://your-domain.com/auth/callback/linkedin
https://your-domain.com/auth/callback/twitter
https://your-domain.com/auth/callback/instagram
```

And set the `APP_URL` environment variable:
```bash
APP_URL=https://your-domain.com
```

---

## Troubleshooting

### Error: "Invalid redirect_uri"
**Solution**: Make sure you've added all three redirect URIs in Clerk dashboard and clicked Save.

### Error: "Client authentication failed"
**Solution**: Check that Client ID and Client Secret match in both Clerk and your code.

### OAuth page doesn't load
**Solution**:
1. Check that Clerk OAuth application is in "Development" mode (or "Production" if deployed)
2. Verify Consent Screen is enabled (should see toggle in first screenshot)

---

## Current Status

✅ **Client ID configured** in app.py
✅ **OAuth URLs updated** to use cool-fish-70.clerk.accounts.dev
✅ **Redirect logic implemented** in callback handler
❌ **Redirect URIs NOT YET ADDED** in Clerk dashboard (you need to do this now)

---

## Next Steps

1. **Add the 3 redirect URIs** in Clerk dashboard (scroll down on current page)
2. **Save changes**
3. **Go to** http://localhost:8080/settings
4. **Click "Connect LinkedIn"** to test
5. **Authorize** and see if it redirects back successfully

Once this works for localhost, you can set up actual LinkedIn/Twitter/Instagram OAuth apps!
