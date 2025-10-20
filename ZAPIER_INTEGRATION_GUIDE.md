# Zapier Integration Guide - LinkedIn & Instagram OAuth

**Perfect Solution**: Use your existing Zapier account to handle OAuth authentication for LinkedIn and Instagram!

**Status**: ✅ Your Claude AI is already connected to Zapier (seen in screenshot)

---

## Why Zapier is Perfect for This

### What You Get:
✅ **No OAuth coding required** - Zapier handles all authentication
✅ **LinkedIn & Instagram already supported** - Just click "Connect"
✅ **Secure & reliable** - Enterprise-grade OAuth
✅ **Works immediately** - No developer apps needed
✅ **Your Claude AI already integrated** - Seen in your settings

### How It Works:
```
Milton Dashboard → Generate Post → Zapier Webhook → LinkedIn/Instagram
```

---

## Complete Setup (15 Minutes)

### Step 1: Connect LinkedIn to Zapier

1. **Go to Zapier**: https://zapier.com/app/connections
2. **Click "Add Connection"**
3. **Search for "LinkedIn"**
4. **Click "Connect"** - Zapier will open LinkedIn OAuth
5. **Authorize** - Grant Zapier permission to post
6. **Done!** - LinkedIn is now connected to your Zapier account

### Step 2: Connect Instagram to Zapier

1. **In Zapier Connections**: https://zapier.com/app/connections
2. **Click "Add Connection"**
3. **Search for "Instagram"**
4. **Click "Connect"** - Zapier will open Facebook OAuth
5. **Select Instagram Business Account**
6. **Authorize** - Grant Zapier permission
7. **Done!** - Instagram is now connected

---

## Create Zapier Workflows (Zaps)

### Zap 1: Post to LinkedIn

**Trigger**: Webhooks by Zapier → Catch Hook
**Action**: LinkedIn → Create Share Update

#### Setup Steps:

1. **Create New Zap**: https://zapier.com/app/editor
2. **Trigger**:
   - App: **Webhooks by Zapier**
   - Event: **Catch Hook**
   - Click "Continue"
   - **Copy the webhook URL** (save for later)

3. **Action**:
   - App: **LinkedIn**
   - Event: **Create Share Update**
   - Account: **Select your connected LinkedIn**
   - Update Text: **{{1__content}}** (from webhook data)
   - Visibility: **Public**
   - Click "Test & Continue"

4. **Name it**: "Milton AI → LinkedIn"
5. **Turn it ON**

#### Webhook URL Format:
```
https://hooks.zapier.com/hooks/catch/XXXXX/YYYYY/
```

---

### Zap 2: Post to Instagram

**Trigger**: Webhooks by Zapier → Catch Hook
**Action**: Instagram for Business → Create Photo Post

#### Setup Steps:

1. **Create New Zap**: https://zapier.com/app/editor
2. **Trigger**:
   - App: **Webhooks by Zapier**
   - Event: **Catch Hook**
   - Click "Continue"
   - **Copy the webhook URL** (save for later)

3. **Action**:
   - App: **Instagram for Business**
   - Event: **Create Photo Post**
   - Account: **Select your connected Instagram**
   - Caption: **{{1__content}}** (from webhook data)
   - Image URL: **{{1__image_url}}** (optional)
   - Click "Test & Continue"

4. **Name it**: "Milton AI → Instagram"
5. **Turn it ON**

---

## Configure Milton Dashboard to Use Zapier

### Option 1: Update Settings Page

Add your Zapier webhook URLs to the Settings page so users can enter them via UI.

**File**: `dashboard/templates/settings.html`

Add after the OAuth section:

```html
<div class="card">
    <h2>Zapier Webhooks</h2>
    <p>Connect Milton AI to LinkedIn/Instagram via Zapier</p>

    <div class="form-group">
        <label>LinkedIn Webhook URL:</label>
        <input type="text" id="linkedinWebhook"
               placeholder="https://hooks.zapier.com/hooks/catch/..."
               style="width: 100%; padding: 12px;">
        <button onclick="saveWebhook('linkedin')">Save</button>
    </div>

    <div class="form-group">
        <label>Instagram Webhook URL:</label>
        <input type="text" id="instagramWebhook"
               placeholder="https://hooks.zapier.com/hooks/catch/..."
               style="width: 100%; padding: 12px;">
        <button onclick="saveWebhook('instagram')">Save</button>
    </div>
</div>
```

### Option 2: Add to .env File (Simpler)

Add your Zapier webhook URLs directly to `.env`:

```bash
# Zapier Webhook URLs
ZAPIER_LINKEDIN_WEBHOOK=https://hooks.zapier.com/hooks/catch/XXXXX/YYYYY/
ZAPIER_INSTAGRAM_WEBHOOK=https://hooks.zapier.com/hooks/catch/AAAAA/BBBBB/
```

Then update the publish endpoint to use these webhooks when OAuth isn't available.

---

## Update Publish Endpoint to Use Zapier

**File**: `dashboard/app.py` (around line 471)

Modify the publish endpoint to check for Zapier webhooks:

```python
@app.post("/api/posts/{post_id}/publish")
async def publish_post(post_id: int, platform: str):
    """Publish post to social media via OAuth or Zapier"""

    # Get post from database
    post = db.get_post(post_id)
    if not post:
        return {"error": "Post not found"}

    # Check if Zapier webhook is configured
    zapier_webhook = None
    if platform == "linkedin":
        zapier_webhook = os.getenv('ZAPIER_LINKEDIN_WEBHOOK')
    elif platform == "instagram":
        zapier_webhook = os.getenv('ZAPIER_INSTAGRAM_WEBHOOK')

    if zapier_webhook:
        # Use Zapier webhook
        import requests

        payload = {
            "content": post['content'],
            "voice_type": post['voice_type'],
            "scenario": post['scenario'],
            "image_url": post.get('graphic_url'),
            "platform": platform
        }

        response = requests.post(zapier_webhook, json=payload)

        if response.status_code == 200:
            return {
                "success": True,
                "platform": platform,
                "method": "zapier",
                "message": f"Posted to {platform} via Zapier"
            }
        else:
            return {
                "error": f"Zapier webhook failed: {response.status_code}"
            }
    else:
        # Fall back to direct OAuth (existing code)
        # ... existing OAuth publishing code ...
        pass
```

---

## Testing the Integration

### Test Zapier Webhooks:

1. **In Zapier**, go to your Zap
2. **Click "Test"** on the trigger step
3. **Send test data** from Postman or curl:

```bash
curl -X POST https://hooks.zapier.com/hooks/catch/XXXXX/YYYYY/ \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Test post from Milton AI Publicist! Let''s Go Owls!",
    "platform": "linkedin"
  }'
```

4. **Check LinkedIn** - You should see the post!

### Test from Milton Dashboard:

1. **Generate a post** in dashboard
2. **Click "Publish to LinkedIn"**
3. **Dashboard sends** webhook to Zapier
4. **Zapier posts** to LinkedIn automatically
5. **Check LinkedIn** - Post should appear!

---

## Zapier Workflow Examples

### Example 1: Simple Post
```
Trigger: Webhook receives post content
Action: Post to LinkedIn with content
```

### Example 2: Post with Image
```
Trigger: Webhook receives post + image URL
Action: Download image → Post to Instagram with caption
```

### Example 3: Multi-Platform
```
Trigger: Webhook receives post
Action 1: Post to LinkedIn
Action 2: Post to Instagram (same content, different format)
Action 3: Post to Twitter
```

### Example 4: Scheduled Posts
```
Trigger: Webhook receives post + schedule time
Action 1: Delay until scheduled time
Action 2: Post to LinkedIn
```

### Example 5: Analytics Tracking
```
Trigger: Webhook receives post
Action 1: Post to LinkedIn
Action 2: Log to Google Sheets (track what was posted when)
```

---

## Benefits of Zapier Approach

### vs. Direct OAuth:
| Feature | Direct OAuth | Zapier |
|---------|--------------|---------|
| Setup Time | 4-6 hours | 15 minutes |
| Coding Required | Yes (200+ lines) | No |
| Maintenance | Token refresh logic | None |
| Multi-Platform | Build each separately | Just add Zap |
| Error Handling | Must code | Built-in |
| Cost | Free (dev time) | $20/month |

### Security:
✅ **OAuth handled by Zapier** - Enterprise-grade security
✅ **No tokens in your code** - Zapier stores them
✅ **Easy to revoke** - Just disconnect in Zapier
✅ **Compliant with TOS** - Zapier is approved by all platforms

---

## Cost Analysis

### Zapier Pricing:
- **Starter Plan**: $19.99/month
  - 750 tasks/month
  - Multi-step Zaps
  - Premium apps (LinkedIn, Instagram)

### Tasks Used:
- 1 task = 1 post published
- 750 tasks = 25 posts per day
- More than enough for Athletics Department

### ROI:
- **Save 4-6 hours** of OAuth development
- **No maintenance** for token refresh
- **Reliable & supported** by Zapier team
- **$20/month vs. hours of debugging**

---

## Alternative: Zapier + Claude AI Integration

Since your Claude AI is already connected to Zapier, you can create an advanced workflow:

### AI-Enhanced Posting Workflow:

```
Trigger: Webhook from Milton Dashboard
↓
Action 1: Claude AI - Review content for tone
↓
Action 2: Paths (if tone is good → continue, if not → send back for edit)
↓
Action 3: Post to LinkedIn
↓
Action 4: Send confirmation email
```

This adds an extra AI review step before posting!

---

## Quick Start Checklist

- [ ] Connect LinkedIn to Zapier
- [ ] Connect Instagram to Zapier
- [ ] Create "Milton AI → LinkedIn" Zap
- [ ] Create "Milton AI → Instagram" Zap
- [ ] Copy webhook URLs
- [ ] Add webhooks to `.env` file
- [ ] Update publish endpoint (optional)
- [ ] Test with curl command
- [ ] Test from dashboard
- [ ] Monitor Zap task history

---

## Troubleshooting

### Webhook not triggering:
**Solution**: Check Zap is turned ON, webhook URL is correct

### LinkedIn post failed:
**Solution**: Reconnect LinkedIn in Zapier connections

### Instagram requires image:
**Solution**: Ensure `image_url` is included in webhook payload

### Hit task limit:
**Solution**: Upgrade Zapier plan or combine multi-platform into one Zap

---

## Summary

✅ **Zapier is the perfect solution** for LinkedIn/Instagram OAuth
✅ **Your Claude AI is already connected** - leverage existing integration
✅ **15-minute setup** vs. hours of OAuth coding
✅ **Reliable & secure** - Enterprise-grade infrastructure
✅ **No maintenance** - Zapier handles everything

**Next Steps**:
1. Connect LinkedIn & Instagram to Zapier (5 min)
2. Create 2 Zaps with webhook triggers (10 min)
3. Add webhook URLs to `.env` (1 min)
4. Test posting from dashboard (2 min)

**Total Time**: ~20 minutes to fully working OAuth!
