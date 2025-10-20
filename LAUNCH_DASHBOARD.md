# Launch Dashboard - Quick Start

## Click to Launch Dashboard

Open your terminal in the `milton-publicist` directory and run:

```bash
python start_dashboard.py
```

**Dashboard URL**: http://localhost:8080

---

## What You Can Test Right Now

### 1. Content Generation (No OAuth Required)

**Test Personal Voice**:
- Voice Type: "Personal (LinkedIn - Brief & Warm)"
- Scenario: "Partner Appreciation"
- Context: "Thank GameChanger Analytics for their 3-year partnership"
- Click "Generate Content"

**Expected Result**: 20-80 word post with "Let's Go Owls!"

**Test Professional Voice**:
- Voice Type: "Professional (Official Statement)"
- Scenario: "Coaching Announcement"
- Context: "Hiring Sarah Mitchell as Assistant Women's Basketball Coach"
- Click "Generate Content"

**Expected Result**: 200-400 word structured announcement

---

### 2. Preview & Edit

- Click any generated post in the list
- Review content in preview panel
- Click content to edit inline
- Click "Save Edits"

---

### 3. Publishing (Requires LinkedIn OAuth)

Once you complete LinkedIn OAuth setup:
- Generate content
- Review in preview
- Click "Publish to LinkedIn"
- Confirm action
- Success! Post appears on LinkedIn

---

## Complete LinkedIn OAuth Setup

**Time**: 15-20 minutes

**Guide**: See [CLERK_SETUP_NEXT_STEPS.md](CLERK_SETUP_NEXT_STEPS.md)

**Steps**:
1. LinkedIn Developer Portal → Auth tab → Add redirect URL
2. Clerk Dashboard → Add LinkedIn credentials
3. Enable "Share on LinkedIn" product
4. Connect LinkedIn account via Clerk

---

## Troubleshooting

**Dependencies Missing?**
```bash
pip install fastapi uvicorn jinja2 aiofiles anthropic clerk-backend-api aiohttp python-dotenv
```

**Port 8080 in use?**
Edit [dashboard/app.py](dashboard/app.py) line 377 to use port 8081

---

**Ready to test! Let's Go Owls!**
