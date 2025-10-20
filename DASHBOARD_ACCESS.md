# Milton AI Publicist Dashboard - Access Guide

## Dashboard is Now Running!

**Milton AI Publicist Dashboard URL**: **http://localhost:8081**

(Using port 8081 because 8080 is in use by the recruiting app)

---

## How to Start the Dashboard

**Method 1: Python Script (Recommended)**
```bash
cd "c:\Users\mover\OneDrive\Documents\GitHub\All State RevShield Engine AJ\milton-publicist"
python run_dashboard_8081.py
```

**Method 2: Batch File (Windows)**
```bash
cd "c:\Users\mover\OneDrive\Documents\GitHub\All State RevShield Engine AJ\milton-publicist"
start_milton_dashboard.bat
```

---

## Quick Test - Generate Your First Post

### Step 1: Open Dashboard
Open your browser to: **http://localhost:8081**

### Step 2: Try Personal Voice (20-80 words)
- **Voice Type**: Select "Personal (LinkedIn - Brief & Warm)"
- **Scenario**: Select "Partner Appreciation"
- **Context**: Type "Thank GameChanger Analytics for their 3-year partnership with KSU Athletics"
- Click **"Generate Content"**

**Expected Result**: 20-80 word post with "Let's Go Owls!"

### Step 3: Try Professional Voice (200-400 words)
- **Voice Type**: Select "Professional (Official Statement)"
- **Scenario**: Select "Coaching Announcement"
- **Context**: Type "Hiring Sarah Mitchell as Assistant Women's Basketball Coach from the SEC"
- Click **"Generate Content"**

**Expected Result**: 200-400 word structured announcement

---

## Dashboard Features

### Left Panel: "Generate Content"
- Voice type selector (Personal / Professional)
- Scenario dropdown
- Context input field
- Generate button

### Middle Panel: "Generated Posts"
- List of all generated posts
- Status badges (Pending / Published)
- Click any post to preview

### Right Panel: "Preview & Publish"
- Full post content
- Word count and timestamp
- Edit button (click content to edit)
- Save edits button
- Publish to LinkedIn button (requires OAuth)
- Delete button

### Top Status Bar:
- LinkedIn connection status
- Total generated posts
- Total published posts
- System status

---

## What Works Right Now (No OAuth Required)

✅ **Generate unlimited content** in Milton's authentic voice
✅ **Preview** generated posts
✅ **Edit** content inline
✅ **Save** edits
✅ **Delete** posts
✅ **View** all generated posts

---

## What Requires LinkedIn OAuth Setup

⏳ **Publish to LinkedIn** button (needs 15-20 min OAuth setup)

**To enable publishing**: See [CLERK_SETUP_NEXT_STEPS.md](CLERK_SETUP_NEXT_STEPS.md)

---

## Troubleshooting

### Dashboard won't load at localhost:8081

**Check if server is running**:
```bash
netstat -ano | findstr :8081
```

**Restart the server**:
1. Press Ctrl+C in the terminal running the dashboard
2. Run `python run_dashboard_8081.py` again

### Generated content seems generic

**Check**:
- Correct voice type selected (Personal vs. Professional)
- Specific context provided
- Look for signature phrase "Let's Go Owls!"
- Word count matches (20-80 or 200-400)

### Can't click "Publish to LinkedIn"

**This is expected!** Publishing requires OAuth setup first.
**See**: [CLERK_SETUP_NEXT_STEPS.md](CLERK_SETUP_NEXT_STEPS.md)

---

## Two Applications Running

You now have TWO apps running on localhost:

1. **Port 8080**: Hero Hype Hub (recruiting app) - http://localhost:8080
2. **Port 8081**: Milton AI Publicist - http://localhost:8081

Make sure you're accessing the correct one!

---

## Next Steps

1. ✅ **Dashboard is running** - http://localhost:8081
2. ✅ **Generate test content** - Try both voice types
3. ⏳ **Complete LinkedIn OAuth** - Enable publishing (15-20 min)
4. ⏳ **Publish first post** - One-click to LinkedIn!

---

**Ready to test! Let's Go Owls!** 🦉

---

**Dashboard URL**: http://localhost:8081
**Server Status**: Running (Process ID shown in terminal)
**To Stop**: Press Ctrl+C in the terminal
