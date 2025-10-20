# Milton AI Publicist - Quick Start Guide

**Dashboard**: http://localhost:8080
**Admin Panel**: http://localhost:8080/admin

---

## ✅ UI ACCESSIBILITY - FIXED

All 28 API endpoints and 5 modules are now accessible via the web interface!

- **Main Dashboard** - Create posts, upload photos, generate graphics
- **Admin Panel** - Access analytics, scheduling, news, PR, media gallery
- **Photo Upload** - Added UI button to upload custom media
- **Analytics Dashboard** - Fixed database schema errors

---

## Quick Start (3 Steps)

### 1. Dashboard is Already Running
```
http://localhost:8080 - Running on port 8080
```

### 2. Open in Browser
- **Create Posts**: http://localhost:8080
- **Manage Features**: http://localhost:8080/admin

### 3. Start Creating Content
1. Select voice type and scenario
2. Add context about the post
3. Upload photo (optional)
4. Click "Generate Content"
5. Review and publish!

---

## Main Features

### 📝 Create Posts (Main Dashboard)
**URL**: http://localhost:8080

1. Choose **voice**: Personal | Coach | Professional
2. Choose **scenario**: Game Highlights | Recruiting | Partner Appreciation
3. Enter **context**: "KSU volleyball won 4 straight CUSA games"
4. **Upload photo** (NEW!): Click "📤 Upload Photo/Video"
5. Check **Include AI graphic** for free Gemini-generated image
6. Click "✨ Generate Content"
7. Review, edit if needed
8. Publish or save for later

### 📊 View Analytics (Admin Panel)
**URL**: http://localhost:8080/admin

- Click **"View Analytics"** - Complete metrics dashboard
- Click **"Best Times"** - Optimal posting schedule
- Click **"Content Performance"** - Voice/scenario analysis
- Click **"Top Posts"** - Highest performers

### 📅 Manage Scheduled Posts (Admin Panel)
- Click **"View Scheduled"** - See queued posts
- Click **"View Upcoming"** - Next 7 days
- Posts auto-publish via scheduler daemon (runs every 60 seconds)

### 🖼️ Media Gallery (Admin Panel)
- Click **"View Gallery"** - Browse all media with thumbnails
- See uploaded photos and AI-generated graphics
- Delete media directly from gallery

### 📰 News Monitor (Admin Panel)
- Click **"Run News Monitor"** - Find trending KSU news
- Get AI-powered post suggestions based on current events

### 🎯 PR Opportunities (Admin Panel)
- Click **"Run PR Finder"** - Trending topics + hashtags
- Competitive analysis vs CUSA rivals
- Content opportunity recommendations

---

## Voice Types

| Voice | Use For | Tone | Example |
|-------|---------|------|---------|
| **Personal** | Celebrations, fan engagement | Warm, first-person | "I am so proud of our Lady Owls..." |
| **Coach** | Team updates, motivation | Supportive, encouraging | "Our team showed incredible resilience..." |
| **Professional** | Official announcements, press releases | Formal, institutional | "Kennesaw State Athletics is pleased to announce..." |

---

## All Features Now Accessible

### ✅ Via Main Dashboard (http://localhost:8080)
- Generate content (3 voice types)
- Upload custom photos/videos
- Include AI-generated graphics
- Preview and edit posts
- Publish to LinkedIn
- View post history

### ✅ Via Admin Panel (http://localhost:8080/admin)
- **Analytics**: 8 endpoints (engagement, best times, insights)
- **Scheduling**: View/manage scheduled posts
- **Media Gallery**: Browse all uploaded/generated media
- **News Monitor**: Find trending news opportunities
- **PR Finder**: Trending topics + hashtag recommendations
- **Post Management**: View all posts, filter by status

---

## Database

**Location**: `milton_publicist.db` (SQLite)

**Current Data**:
- 5 posts generated
- 1 post scheduled
- 5+ AI graphics created
- 0 analytics records (none recorded yet)

**Record Engagement** (via Admin Panel or API):
```bash
curl -X POST http://localhost:8080/api/analytics/engagement \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": 1,
    "platform": "linkedin",
    "views": 250,
    "likes": 18,
    "comments": 5,
    "shares": 3
  }'
```

---

## API Endpoints (28 Total)

All accessible via **Admin Panel** buttons:

### Posts (6)
- Generate | View All | Get Specific | Edit | Delete | Publish

### Scheduling (4)
- View Scheduled | View Upcoming | Schedule Post | Cancel

### Analytics (8)
- Record Engagement | Post Performance | Overview | Best Times | Content Performance | Top Posts | Insights | Dashboard

### Media (4)
- Gallery | Upload | Delete | Serve Files

### News & PR (4)
- News Monitor | Trending Topics | Hashtags | Opportunities

### System (2)
- Status | OAuth Connections

---

## Testing The Fixes

### ✅ Dashboard Running
```bash
curl http://localhost:8080/api/status
# Returns: {"status":"online","user":{"email":"moverton@kennesaw.edu"},...}
```

### ✅ Analytics Fixed (No More Errors!)
```bash
curl http://localhost:8080/api/analytics/dashboard
# Returns: Complete metrics (no database schema errors)
```

### ✅ Media Gallery Working
```bash
curl http://localhost:8080/api/media/gallery
# Returns: List of 5+ generated graphics with thumbnails
```

### ✅ Scheduled Posts
```bash
curl http://localhost:8080/api/scheduled
# Returns: 1 post scheduled for 2025-10-20T09:00:00Z
```

---

## What Was Fixed

| Issue | Fix | Status |
|-------|-----|--------|
| Analytics database error | Updated 6 SQL queries to match flat schema | ✅ Fixed |
| No photo upload UI | Added file input + preview to main dashboard | ✅ Fixed |
| Features not accessible | Created admin.html with buttons for all 28 endpoints | ✅ Fixed |
| No media gallery UI | Added thumbnail grid view | ✅ Fixed |
| No analytics UI | Added analytics section with 8 endpoints | ✅ Fixed |
| No scheduling UI | Added scheduled posts view | ✅ Fixed |

---

## Documentation

**Complete Guides**:
- [UI_ACCESS_FIXED.md](UI_ACCESS_FIXED.md) - Detailed fix documentation
- [FEATURE_AUDIT.md](FEATURE_AUDIT.md) - Complete feature list
- [PRIORITY_4_COMPLETE.md](PRIORITY_4_COMPLETE.md) - Analytics documentation

**Test Scripts**:
- `test_analytics.py` - Test analytics system
- `test_authentic_voice.py` - Test content generation

---

## Summary

✅ **All 28 API endpoints** accessible via web UI
✅ **Photo upload** added to main dashboard
✅ **Admin panel** provides one-click access to all features
✅ **Analytics engine** fixed (database schema corrected)
✅ **Media gallery** with thumbnail previews
✅ **No more hidden features** - everything accessible!

**Start Here**:
1. Main Dashboard: http://localhost:8080
2. Admin Panel: http://localhost:8080/admin

**You're ready to use all features!** 🎉
