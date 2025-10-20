# Dashboard Quick Start Guide

**Milton AI Publicist - Approval Dashboard**

---

## Launch the Dashboard

### Method 1: Startup Script (Recommended)
```bash
cd milton-publicist
python start_dashboard.py
```

This will:
- Check all dependencies
- Verify configuration
- Check OAuth connection status
- Start the server on port 8080
- Open your browser automatically

### Method 2: Direct Launch
```bash
cd milton-publicist
python dashboard/app.py
```

Then open your browser to: `http://localhost:8080`

---

## Using the Dashboard

### 1. Generate Content

**Left Panel: "Generate Content"**

1. **Select Voice Type:**
   - **Personal (LinkedIn - Brief & Warm)**: 20-80 words, casual tone, "Let's Go Owls!"
   - **Professional (Official Statement)**: 200-400 words, structured, official AD voice

2. **Choose Scenario:**
   - Partner Appreciation
   - Team Celebration
   - Community Service
   - Coaching Announcement
   - Policy Update

3. **Enter Context:**
   - Type details about what you want to post
   - Example: "GameChanger Analytics partnership announcement"

4. **Click "Generate Content"**
   - AI generates post in Milton's authentic voice
   - Content appears in preview panel
   - Post is added to the list

---

### 2. Review Generated Posts

**Left Panel: "Generated Posts" List**

- All generated posts appear here
- Click any post to preview it
- Status badges:
  - **Pending**: Not yet published
  - **Published**: Successfully posted to LinkedIn

---

### 3. Preview & Edit

**Right Panel: "Preview & Publish"**

- **Preview**: See the full post content
- **Edit**: Click the content area to edit inline
- **Metadata**: Word count, timestamp, status
- **Actions**:
  - **Publish to LinkedIn**: Publishes the post (requires OAuth)
  - **Save Edits**: Saves any changes you made
  - **Delete**: Removes the post

---

### 4. Publish to LinkedIn

**Prerequisites:**
- LinkedIn OAuth must be connected (see [CLERK_SETUP_NEXT_STEPS.md](CLERK_SETUP_NEXT_STEPS.md))
- Your Clerk user account must have LinkedIn connected

**Steps:**
1. Review the post content in the preview panel
2. Make any edits if needed
3. Click "Save Edits" if you made changes
4. Click "Publish to LinkedIn"
5. Confirm the publish action
6. Success message appears with LinkedIn post URL
7. Post status changes to "Published"

---

## Dashboard Features

### Status Bar (Top of Page)

Shows real-time system status:
- **LinkedIn**: Connection status
- **Generated**: Total posts created
- **Published**: Total posts published
- **Status**: System online/offline

### Content Generation

**Personal Voice Example:**
- **Input**: "Thank GameChanger Analytics for partnership"
- **Output** (54 words):
  ```
  We want to thank GameChanger Analytics for their incredible partnership
  with Kennesaw State University Athletics! Their cutting-edge AI-powered
  fan engagement tools will transform how we connect with our amazing Owl
  community over the next three years. Champion partners like GameChanger
  Analytics help us build champion experiences for our fans and student-athletes.
  Let's Go Owls!
  ```

**Professional Voice Example:**
- **Input**: "Hiring Sarah Mitchell as Assistant Women's Basketball Coach"
- **Output** (245 words):
  ```
  Kennesaw State University Athletics is excited to announce the hiring of
  Sarah Mitchell as Assistant Women's Basketball Coach. Mitchell brings
  over a decade of coaching experience from the SEC...

  [Structured paragraphs with rationale, qualifications, student-athlete focus]

  Let's go Owls!
  ```

### Inline Editing

- Click any content area marked `contenteditable="true"`
- Edit the text directly
- Click "Save Edits" to persist changes
- Word count updates automatically

---

## API Endpoints

The dashboard uses these REST API endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Main dashboard page |
| `/api/status` | GET | System status and connections |
| `/api/generate` | POST | Generate new content |
| `/api/posts` | GET | List all posts |
| `/api/posts/{id}` | GET | Get specific post |
| `/api/posts/{id}` | PUT | Update post content |
| `/api/posts/{id}/publish` | POST | Publish to LinkedIn |
| `/api/posts/{id}` | DELETE | Delete post |

---

## Testing Without OAuth

**You can test content generation immediately**, even without LinkedIn connected:

1. Launch dashboard
2. Select voice type and scenario
3. Enter context
4. Click "Generate Content"
5. Review the generated post

The **"Publish to LinkedIn"** button will show an error message if OAuth is not connected, but you can still:
- Generate unlimited content
- Preview posts
- Edit content
- Save edits
- Delete posts

---

## Complete Workflow Example

### Scenario: Post About Partner Appreciation

**Step 1: Open Dashboard**
```bash
python start_dashboard.py
```

**Step 2: Select Settings**
- Voice Type: "Personal (LinkedIn - Brief & Warm)"
- Scenario: "Partner Appreciation"
- Context: "Thank Fifth Third Bank for their continued support of KSU Athletics"

**Step 3: Generate**
- Click "Generate Content"
- Wait 2-3 seconds
- Generated post appears in preview panel

**Step 4: Review**
- Read the generated content
- Check authenticity (Should have "Let's Go Owls!", warm tone, 20-80 words)
- Make edits if needed

**Step 5: Publish** (if OAuth connected)
- Click "Publish to LinkedIn"
- Confirm action
- Success! Post appears on LinkedIn

---

## Troubleshooting

### Dashboard Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Install dependencies
```bash
pip install fastapi uvicorn jinja2 aiofiles
```

---

### "LinkedIn Not Connected" Error

**Error**: Clicking "Publish to LinkedIn" shows "LinkedIn not connected"

**Solution**: Complete OAuth setup
1. Follow [CLERK_SETUP_NEXT_STEPS.md](CLERK_SETUP_NEXT_STEPS.md)
2. Create LinkedIn OAuth app
3. Add credentials to Clerk
4. Connect LinkedIn account via Clerk
5. Refresh dashboard

---

### Generated Content Seems Generic

**Issue**: Content doesn't sound like Milton

**Solution**:
1. Check voice type selection (Personal vs. Professional)
2. Provide more specific context
3. Regenerate with more details

**Example**:
- Bad context: "Post about partnership"
- Good context: "Thank GameChanger Analytics for 3-year AI-powered fan engagement partnership"

---

### Port 8080 Already in Use

**Error**: `OSError: [Errno 48] Address already in use`

**Solution**:
1. Stop any other process using port 8080
2. Or edit `dashboard/app.py` line 377 to use different port:
```python
uvicorn.run(app, host="0.0.0.0", port=8081)  # Changed from 8080
```

---

## Next Steps

### 1. Complete LinkedIn OAuth Setup

Follow the guide in [CLERK_SETUP_NEXT_STEPS.md](CLERK_SETUP_NEXT_STEPS.md):

1. Add OAuth redirect URL to LinkedIn app
2. Enable "Share on LinkedIn" product
3. Get Client ID and Secret
4. Add to Clerk dashboard
5. Connect your LinkedIn account

**Estimated Time**: 15-20 minutes

---

### 2. Test End-to-End Publishing

Once OAuth is connected:

1. Generate test post
2. Review in dashboard
3. Publish to LinkedIn
4. Verify post appears on profile
5. Check LinkedIn post URL

---

### 3. Expand to More Platforms

**Twitter/X**:
- Create Twitter OAuth app
- Add credentials to Clerk
- Connect Twitter account
- Test tweeting from dashboard

**Instagram**:
- Create Facebook OAuth app
- Connect Instagram Business Account
- Link to Facebook Page
- Test image posting

---

## Security Notes

**OAuth Tokens**:
- Stored securely in Clerk (encrypted)
- Never stored in dashboard code
- Automatically refreshed when expired
- Can be revoked at any time

**Content Storage**:
- Currently in-memory (demo mode)
- Production: Use PostgreSQL database
- All content is private to your session

**API Keys**:
- Stored in `.env` file
- Never committed to git
- Should be kept secret

---

## Dashboard Architecture

```
milton-publicist/
├── dashboard/
│   ├── app.py                 # FastAPI backend (350+ lines)
│   ├── templates/
│   │   └── index.html         # Web UI (500+ lines)
│   └── static/                # Static assets
│
├── module_iii/                # Social media publisher
│   ├── clerk_auth.py          # OAuth management
│   └── social_media_publisher.py  # LinkedIn/Twitter/Instagram
│
├── start_dashboard.py         # Startup script
├── .env                       # Configuration
└── DASHBOARD_QUICK_START.md   # This file
```

---

## Support

**Issue**: Dashboard not working as expected

**Debugging Steps**:
1. Check console output for errors
2. Open browser DevTools (F12)
3. Look at Network tab for failed requests
4. Check Console tab for JavaScript errors
5. Verify `.env` file has all required keys

**Common Fixes**:
- Refresh the page
- Clear browser cache
- Restart the dashboard server
- Check API key validity

---

**Ready to launch the dashboard and start generating content in Milton's authentic voice!**

**Let's Go Owls!**
