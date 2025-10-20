# Zapier Integration Setup - Quick Start Guide

## ✅ Implementation Status: COMPLETE

All code has been successfully implemented! The database migration has been applied. You just need to restart the dashboard and configure your Zapier webhooks.

---

## What Was Done

### ✅ Database Migration Applied
- `post_publications` table created
- 5 indexes created for performance
- 2 views created (successful_publications, failed_publications)
- Migration verified successfully

### ✅ Files Created
1. `dashboard/zapier_publisher.py` - Webhook handler
2. `dashboard/publishing_endpoints.py` - API endpoints
3. `dashboard/static/zapier_publisher.js` - Frontend JavaScript
4. `dashboard/static/zapier_publisher.css` - UI styling
5. `database/add_zapier_publishing_table.sql` - Database schema

### ✅ Files Modified
1. `dashboard/app.py` - Publishing router added
2. `dashboard/templates/index.html` - CSS/JS links added
3. `.env.template` - Zapier webhook variables added

---

## Quick Setup Steps

### Step 1: Restart Dashboard (Required)

**For PowerShell:**
```powershell
# Navigate to project directory
cd "c:\Users\mover\OneDrive\Documents\GitHub\All State RevShield Engine AJ\milton-publicist"

# Stop any running dashboards (press Ctrl+C in their terminals)

# Start dashboard
python dashboard/app.py
```

The dashboard will start on **http://localhost:8080**

### Step 2: Verify New Endpoints Work

Open a **new** terminal and test:

```powershell
# Test platform status endpoint
curl http://localhost:8080/api/publish/platforms
```

**Expected output:**
```json
{
  "platforms": {
    "linkedin": false,
    "instagram": false,
    "twitter": false,
    "facebook": false
  },
  "configured_count": 0,
  "total_platforms": 4
}
```

If you see this, the integration is working! ✅

---

## Step 3: Configure Zapier Webhooks

### A. Create Zaps in Zapier

For each platform you want to use:

1. **Go to Zapier**: https://zapier.com/app/editor
2. **Click "Create"** → **"New Zap"**
3. **Configure Trigger**:
   - Search for: **"Webhooks by Zapier"**
   - Event: **"Catch Hook"**
   - Click **"Continue"**
   - **COPY THE WEBHOOK URL** (you'll need this!)

4. **Configure Action**:
   - **For LinkedIn**:
     - App: "LinkedIn"
     - Event: "Create Share Update"
     - Update Text: `{{1__content}}`
     - Visibility: Public

   - **For Instagram**:
     - App: "Instagram for Business"
     - Event: "Create Photo Post"
     - Caption: `{{1__content}}`
     - Image URL: `{{1__image_url}}`

   - **For Twitter**:
     - App: "Twitter"
     - Event: "Create Tweet"
     - Message: `{{1__content}}`

   - **For Facebook**:
     - App: "Facebook Pages"
     - Event: "Create Page Post"
     - Message: `{{1__content}}`

5. **Test & Turn ON**
6. **Name your Zap**: e.g., "Milton AI → LinkedIn"

### B. Add Webhook URLs to .env File

1. **Open** `.env` file in the `milton-publicist` directory

2. **Add your webhook URLs**:
```bash
# Zapier Webhooks
ZAPIER_LINKEDIN_WEBHOOK=https://hooks.zapier.com/hooks/catch/12345678/abcdefg/
ZAPIER_INSTAGRAM_WEBHOOK=https://hooks.zapier.com/hooks/catch/12345678/hijklmn/
ZAPIER_TWITTER_WEBHOOK=https://hooks.zapier.com/hooks/catch/12345678/opqrstu/
ZAPIER_FACEBOOK_WEBHOOK=https://hooks.zapier.com/hooks/catch/12345678/vwxyz12/
```

Replace the URLs with your actual webhook URLs from Zapier!

3. **Save** the `.env` file

4. **Restart dashboard** (press Ctrl+C and run `python dashboard/app.py` again)

---

## Step 4: Test Publishing

### Via API:

```powershell
# Check platform status (should now show configured platforms)
curl http://localhost:8080/api/publish/platforms

# Test webhook (sends test message to Zapier)
curl -X POST http://localhost:8080/api/publish/test/linkedin
```

### Via Dashboard UI:

1. **Open**: http://localhost:8080
2. **Generate a test post**
3. **Click "Publish to LinkedIn"** (button will appear once you integrate it in UI)
4. **Check Zapier task history**: https://zapier.com/app/history
5. **Check LinkedIn** to see if post appeared!

---

## API Endpoints Reference

All endpoints are now available at `/api/publish/*`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/publish/platforms` | Check which platforms are configured |
| POST | `/api/publish/posts/{post_id}/linkedin` | Publish to LinkedIn |
| POST | `/api/publish/posts/{post_id}/instagram` | Publish to Instagram |
| POST | `/api/publish/posts/{post_id}/twitter` | Publish to Twitter |
| POST | `/api/publish/posts/{post_id}/facebook` | Publish to Facebook |
| POST | `/api/publish/posts/{post_id}/multi` | Publish to multiple platforms |
| GET | `/api/publish/history` | View publishing history |
| GET | `/api/publish/stats` | Get publishing statistics |
| POST | `/api/publish/test/{platform}` | Test platform webhook |

---

## Troubleshooting

### Problem: Dashboard won't start

**Error**: `ModuleNotFoundError: No module named 'dashboard.publishing_endpoints'`

**Solution**: Make sure you're in the right directory:
```powershell
cd "c:\Users\mover\OneDrive\Documents\GitHub\All State RevShield Engine AJ\milton-publicist"
python dashboard/app.py
```

### Problem: "Not Found" error when accessing /api/publish/*

**Cause**: Dashboard needs to be restarted

**Solution**:
1. Stop dashboard (Ctrl+C)
2. Restart: `python dashboard/app.py`
3. Test again: `curl http://localhost:8080/api/publish/platforms`

### Problem: All platforms show `false` in status

**Cause**: Webhook URLs not configured in `.env` file

**Solution**: Add your Zapier webhook URLs to `.env` file and restart dashboard

### Problem: Publish fails with timeout

**Cause**: Zap is turned OFF or webhook URL is incorrect

**Solution**:
1. Check Zap is ON: https://zapier.com/app/zaps
2. Verify webhook URL matches exactly (no extra spaces)
3. Test webhook directly:
```powershell
curl -X POST "https://hooks.zapier.com/hooks/catch/YOUR_WEBHOOK_HERE/" -H "Content-Type: application/json" -d '{\"content\": \"Test\"}'
```

---

## Next Steps

### Immediate (Required):
1. ✅ Database migration applied
2. ⏳ Restart dashboard
3. ⏳ Configure Zapier webhooks
4. ⏳ Test publishing

### Optional Enhancements:
1. Add publish buttons to existing post cards in UI
2. Implement webhook callbacks for post URLs
3. Create analytics dashboard for publishing stats
4. Add platform-specific options (hashtags, mentions)
5. Integrate with scheduling system

---

## Documentation Files

- **[ZAPIER_INTEGRATION_GUIDE.md](ZAPIER_INTEGRATION_GUIDE.md)** - Original Zapier setup guide
- **[ZAPIER_IMPLEMENTATION_COMPLETE.md](ZAPIER_IMPLEMENTATION_COMPLETE.md)** - Technical implementation details
- **[SETUP_ZAPIER_COMPLETE.md](SETUP_ZAPIER_COMPLETE.md)** - This file (quick start guide)

---

## Success Checklist

- [x] Database migration applied
- [x] New files created
- [x] Existing files modified
- [ ] Dashboard restarted
- [ ] New endpoints accessible
- [ ] Zapier Zaps created
- [ ] Webhook URLs added to .env
- [ ] Test publish successful
- [ ] Post appears on social media

---

## Support

If you encounter issues:

1. **Check dashboard logs** - Look in terminal where dashboard is running
2. **Check Zapier task history** - https://zapier.com/app/history
3. **Test webhooks directly** - Use curl commands above
4. **Check database** - Query `post_publications` table for errors

---

**Status**: Ready for final configuration
**Time to Complete**: 15 minutes (Zapier setup + testing)
**Estimated Time to First Publish**: 20 minutes

🎉 You're almost there! Just restart the dashboard and configure your Zapier webhooks!
