# Backend Access Guide

**Milton AI Publicist - Backend Configuration**

---

## 1. Social Media Account Connections

### Current Status
- **LinkedIn**: OAuth app created, needs final connection (15-20 min)
- **Twitter/X**: Not yet configured
- **Instagram**: Not yet configured

---

### A. Connect LinkedIn (15-20 Minutes)

**You already created the LinkedIn app! Now complete the connection:**

#### Step 1: Configure OAuth Redirect URL (5 min)

1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps)
2. Click on **"Milton AI Publicist"** app
3. Click **"Auth"** tab
4. Under **"OAuth 2.0 settings"**:
   - Click "Add redirect URL"
   - Enter: `https://cool-fish-70.clerk.accounts.dev/v1/oauth_callback`
   - Click "Update"

#### Step 2: Enable "Share on LinkedIn" Product (5 min)

1. Still in LinkedIn Developer Portal
2. Click **"Products"** tab
3. Find **"Share on LinkedIn"**
4. Click **"Request access"** or **"Select"**
5. Wait for approval (usually instant)

#### Step 3: Get Client Credentials (2 min)

1. Go back to **"Auth"** tab
2. Copy **"Client ID"**
3. Copy **"Client Secret"** (click "Show" if hidden)

#### Step 4: Add to Clerk (3 min)

1. Go to [Clerk Dashboard](https://dashboard.clerk.com)
2. Click **"Social Connections"** (left sidebar under "User & Authentication")
3. Find **"LinkedIn"**
4. Paste **Client ID** in the field
5. Paste **Client Secret** in the field
6. Click **"Save"**

#### Step 5: Connect Your Account (5 min)

1. Go to [Clerk Dashboard](https://dashboard.clerk.com) → **"Users"**
2. Find your user: `moverton@kennesaw.edu`
3. Click the user to open details
4. Click **"Impersonate"** button (top right)
5. In the impersonated session, go to Account Settings
6. Click **"Connect LinkedIn"**
7. Authorize the **"Milton AI Publicist"** app
8. Done! LinkedIn is now connected

**Verify**: Refresh dashboard at http://localhost:8081 - LinkedIn status should show "Connected"

---

### B. Connect Twitter/X (30 Minutes)

#### Step 1: Create Twitter Developer Account

1. Go to [Twitter Developer Portal](https://developer.twitter.com)
2. Sign in with the Twitter account you want to use
3. Click **"Sign up for Free Account"**
4. Complete application (Name: Milton Overton AI Publicist)

#### Step 2: Create Twitter App

1. In Developer Portal, click **"Projects & Apps"**
2. Click **"Create App"**
3. App Name: `Milton AI Publicist`
4. Click "Complete"

#### Step 3: Configure OAuth 2.0

1. Click on your app
2. Click **"Settings"** tab
3. Scroll to **"User authentication settings"**
4. Click **"Set up"**
5. Settings:
   - App permissions: **Read and write**
   - Type of App: **Web App**
   - Callback URL: `https://cool-fish-70.clerk.accounts.dev/v1/oauth_callback`
   - Website URL: `https://kennesaw.edu` (or your website)
6. Click "Save"

#### Step 4: Get API Keys

1. Click **"Keys and tokens"** tab
2. Under **"OAuth 2.0 Client ID and Client Secret"**:
   - Copy **Client ID**
   - Copy **Client Secret**

#### Step 5: Add to Clerk

1. Clerk Dashboard → **"Social Connections"**
2. Find **"X / Twitter"**
3. Click to enable
4. Paste Client ID and Client Secret
5. Click **"Save"**

#### Step 6: Connect Account

Same process as LinkedIn:
1. Impersonate your user in Clerk
2. Account Settings → Connect Twitter
3. Authorize the app

---

### C. Connect Instagram (45 Minutes)

**Note**: Instagram requires a Facebook Developer account and Business Page

#### Step 1: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com)
2. Click **"Create App"**
3. Type: **Business**
4. App Name: `Milton AI Publicist`

#### Step 2: Add Instagram Graph API

1. In your app, click **"Add Product"**
2. Find **"Instagram Graph API"**
3. Click **"Set Up"**

#### Step 3: Configure OAuth

1. Settings → Basic
2. Add App Domain: `clerk.accounts.dev`
3. Add Privacy Policy URL (required)
4. Save changes

#### Step 4: Get Credentials

1. Settings → Basic
2. Copy **App ID**
3. Copy **App Secret**

#### Step 5: Add to Clerk

1. Clerk Dashboard → Social Connections
2. Find **"Facebook"** (Instagram uses Facebook OAuth)
3. Enable and add App ID and Secret
4. Enable **"Instagram"** scope

#### Step 6: Connect Instagram Business Account

1. You need an Instagram Business Account
2. Must be connected to a Facebook Page
3. Impersonate user → Connect Facebook
4. Grant Instagram permissions

---

## 2. Knowledge Base Management

### Current Knowledge Base Location

```
milton-publicist/data/
├── milton_linkedin_posts.txt          ← 25 real posts
├── milton_official_statements.txt     ← 6 official statements
└── MILTON_VOICE_KNOWLEDGE_BASE.md     ← 100+ page guide
```

---

### A. Add New LinkedIn Posts

**Option 1: Manual Addition**

1. Open `data/milton_linkedin_posts.txt`
2. Add new posts in this format:

```
=== POST 26 ===
[Date: 2025-10-20]

[Your new LinkedIn post content here]

Let's Go Owls!
```

**Option 2: Automated Scraping** (Not yet built - would you like me to create this?)

---

### B. Add New Official Statements

1. Open `data/milton_official_statements.txt`
2. Add new statements:

```
=== STATEMENT 7: [Title] ===
Source: [URL or source]
Date: [Date]
Type: [Announcement/Policy/etc.]

[Full statement text]

Let's go Owls!
```

---

### C. Update Voice Knowledge Base

The knowledge base is auto-generated from your posts. To update:

**Retrain Voice Model** (would require building this feature):
```bash
python scripts/train_voice_model.py --update
```

---

## 3. Backend API Endpoints

### Currently Available Endpoints

**Dashboard API**: http://localhost:8081/api/

```
GET  /api/status              - System status, connections
POST /api/generate             - Generate content
GET  /api/posts                - Get all posts
GET  /api/posts?status=pending - Filter by status
PUT  /api/posts/{id}           - Update post
POST /api/posts/{id}/publish   - Publish to LinkedIn
DELETE /api/posts/{id}         - Delete post
GET  /api/published            - Get published posts
```

### Example API Usage

**Generate Content via API**:
```bash
curl -X POST http://localhost:8081/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "voice_type": "personal",
    "scenario": "Partner Appreciation",
    "context": "Thank VyStar Credit Union for naming rights partnership"
  }'
```

**Get All Posts**:
```bash
curl http://localhost:8081/api/posts
```

**Publish to LinkedIn**:
```bash
curl -X POST http://localhost:8081/api/posts/1/publish
```

---

## 4. Configuration Files

### Environment Variables (.env)

```bash
# Current configuration
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
CLERK_SECRET_KEY=sk_test_NTRX6vNE2kHgybvc66EYkRebdX3YvSzENF8da1JEe9
MILTON_USER_ID=user_34Jc17HoSPgAcmiSO6AtqGuzjo3
DASHBOARD_PORT=8081
```

**To add more variables**:
1. Edit `.env` file
2. Add new keys
3. Restart dashboard

---

## 5. Database Backend

### Current: In-Memory (Resets on Restart)

Posts are stored in memory and lost when you restart the server.

### Upgrade to Persistent Database (Already Built!)

The database module is ready. To enable:

**Option 1: Quick Switch to SQLite**

Edit `dashboard/app.py` and replace lines 32-34:

```python
# OLD (in-memory):
generated_posts = []
published_posts = []

# NEW (database):
from database.database_manager import DatabaseManager
db = DatabaseManager()
```

Then update the endpoints to use `db.create_post()`, `db.get_all_posts()`, etc.

**Option 2: I can do this for you** - Want me to implement database persistence now?

---

## 6. Access Logs & Monitoring

### Server Logs

Currently running in terminal. To see logs:

```bash
# Check the running dashboard process
cd "c:\Users\mover\OneDrive\Documents\GitHub\All State RevShield Engine AJ\milton-publicist"
# Logs appear in the terminal where you ran run_dashboard_8081.py
```

### Add Logging to File

Create `dashboard/logging_config.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dashboard.log'),
        logging.StreamHandler()
    ]
)
```

---

## Quick Reference Summary

| Feature | Status | How to Access |
|---------|--------|---------------|
| Dashboard | ✅ Running | http://localhost:8081 |
| LinkedIn OAuth | ⚠️ 15 min setup | Follow steps above |
| Twitter OAuth | ❌ Not configured | 30 min setup |
| Instagram OAuth | ❌ Not configured | 45 min setup |
| Knowledge Base | ✅ Ready | `data/` folder |
| API Endpoints | ✅ Available | http://localhost:8081/api/ |
| Database | ✅ Built, not enabled | Can enable now |
| Logging | ⚠️ Console only | Can add file logging |

---

## Next Steps

**Priority 1**: Complete LinkedIn OAuth (15-20 min)
- Follow LinkedIn connection steps above
- Test publishing from dashboard

**Priority 2**: Enable database persistence
- Want me to implement this now?

**Priority 3**: Add Twitter/Instagram
- Follow setup guides above when ready

---

**Questions?** Let me know which feature you want to tackle first!
