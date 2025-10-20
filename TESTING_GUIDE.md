# Testing Guide - Milton Overton AI Publicist

**Purpose:** Step-by-step guide to test the complete system end-to-end

---

## 🚀 Quick Start (5 Minutes)

### **Windows (PowerShell):**
```powershell
cd milton-publicist
.\scripts\quick_test.ps1
```

### **Mac/Linux:**
```bash
cd milton-publicist
chmod +x scripts/quick_test.sh
./scripts/quick_test.sh
```

This will:
1. Check Python installation
2. Create virtual environment
3. Install dependencies
4. Run complete system test
5. Generate sample content

---

## 📋 Pre-Requisites

### **1. Required Software:**
- ✅ Python 3.11+ ([Download](https://www.python.org/downloads/))
- ✅ PostgreSQL 14+ ([Download](https://www.postgresql.org/download/))
- ✅ Git (already have it)

### **2. Required API Keys:**
- ✅ **Anthropic API Key** - Get from https://console.anthropic.com/
  - Sign up for free
  - Get $5 free credit (enough for testing)
  - Copy API key

### **3. Optional (for full features):**
- OpenAI API Key (for voice transcription)
- HeyGen API Key (for avatar videos)

---

## ⚙️ Setup Instructions

### **Step 1: Install PostgreSQL**

**Windows:**
```powershell
# Download from https://www.postgresql.org/download/windows/
# Or use chocolatey:
choco install postgresql

# Start PostgreSQL service
net start postgresql-x64-14
```

**Mac:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Linux:**
```bash
sudo apt-get install postgresql-14
sudo systemctl start postgresql
```

### **Step 2: Create Database**

```bash
# Create database
createdb milton_publicist

# Initialize schema
psql milton_publicist < database/schema.sql

# Verify tables created
psql milton_publicist -c "\dt"
```

Expected output: Should show 14 tables

### **Step 3: Configure Environment**

```bash
# Copy template
cp .env.template .env

# Edit .env (use your favorite editor)
nano .env  # or code .env or notepad .env
```

**Minimum required in .env:**
```bash
# Database
DATABASE_URL=postgresql://localhost:5432/milton_publicist

# API Keys
ANTHROPIC_API_KEY=sk-ant-xxxxx  # ← Your actual key from Anthropic

# Dashboard
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8080

# Feature flags
APPROVAL_REQUIRED=true
```

### **Step 4: Install Python Dependencies**

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Download spaCy model (optional but recommended)
python -m spacy download en_core_web_sm
```

---

## 🧪 Running the Tests

### **Automated Test Suite:**

```bash
python scripts/test_system.py
```

This runs 5 comprehensive tests:

1. **Database Connection** - Verifies PostgreSQL is accessible
2. **Voice Profile Training** - Trains on sample Milton content
3. **Content Generation** - Generates a LinkedIn post using Claude
4. **Quality Assurance** - Runs 6 QA checks on generated content
5. **Approval Dashboard** - Verifies dashboard data is accessible

**Expected output:**
```
============================================================
MILTON OVERTON AI PUBLICIST - SYSTEM TEST
============================================================

============================================================
TEST 1: Database Connection
============================================================
✅ Connected to database
✅ Found 14 tables:
   - analytics_snapshots
   - content_opportunities
   - engagement_interactions
   ... (etc)

============================================================
TEST 2: Voice Profile Training
============================================================
✅ Created 4 sample posts
✅ Voice profile trained successfully
   - Corpus size: 4 documents
   - Avg sentence length: 18.5 words
   - Question ratio: 0.15
   - Primary tone: visionary_strategic_approachable

============================================================
TEST 3: Content Generation
============================================================
✅ Created test insight: TEST-20251019143025
✅ Created test opportunity: 1
⏳ Generating LinkedIn post (this may take 10-15 seconds)...

✅ LinkedIn post generated!
   - Content ID: 1
   - Word count: 425
   - Character count: 2,456
   - Hashtags: #CollegeSports, #AIInnovation, #Leadership

📝 Generated Content Preview:
------------------------------------------------------------
The future of college athletics isn't about bigger budgets—
it's about smarter strategy...
------------------------------------------------------------

============================================================
TEST 4: Quality Assurance
============================================================
⏳ Running QA checks on content 1 (this may take 10-15 seconds)...

✅ QA check complete!
   - Overall score: 85%
   - Passed: ✅ YES
   - Ready for approval: ✅ YES

📊 Individual Check Scores:
   ✅ Voice Authenticity: 88%
   ✅ Brand Alignment: 90%
   ✅ Platform Compliance: 95%
   ✅ Engagement Potential: 75%
   ✅ Readability: 85%

============================================================
TEST 5: Approval Dashboard Data
============================================================
✅ Found 1 items in approval queue

   Content ID: 1
   Platform: linkedin
   QA Score: 85%
   Urgency: today
   Pillars: AI Innovation in Sports Business, Leadership & Vision

📊 Dashboard Statistics:
   - Pending: 1
   - Approved: 0
   - Rejected: 0

============================================================
TEST SUMMARY
============================================================
✅ PASSED - Database Connection
✅ PASSED - Voice Profile Training
✅ PASSED - Content Generation
✅ PASSED - Quality Assurance
✅ PASSED - Approval Dashboard

============================================================
OVERALL: 5/5 tests passed (100%)
============================================================

🎉 ALL TESTS PASSED! System is ready to use.

Next steps:
1. Collect Milton's real LinkedIn posts
2. Retrain voice profile with real data
3. Start the approval dashboard: python dashboard/approval_dashboard.py
4. Open http://localhost:8080 to review generated content
```

---

## 📝 Collecting Milton's Content

### **Method 1: Manual Copy-Paste (Fastest)**

1. **Open Milton's LinkedIn:** https://www.linkedin.com/in/miltonoverton/

2. **Scroll through his posts** and copy recent ones

3. **Save each post:**
```bash
# Create directory
mkdir -p data/milton_content/linkedin_posts

# Save each post as a separate file
# File: data/milton_content/linkedin_posts/post_001.txt
```

**Template for each file:**
```
The future of college athletics isn't about...

[Full post text here - preserve formatting]

#CollegeSports #AIInnovation #Leadership
```

**Target:** 10-20 posts minimum (more is better)

### **Method 2: LinkedIn Data Export**

1. Go to LinkedIn Settings → "Get a copy of your data"
2. Select "Posts" and "Articles"
3. Request archive (arrives in 24 hours)
4. Extract and copy posts to `data/milton_content/linkedin_posts/`

### **Method 3: Use Sample Content (Testing Only)**

The test script creates 4 sample posts automatically. These work for testing but won't capture Milton's real voice.

---

## 🎨 Training Voice Profile with Real Data

Once you have Milton's real posts:

```bash
# Train voice profile
python module_ii/voice_modeling.py \
  --corpus-dir data/milton_content/ \
  --version 2.0.0

# Expected output:
# [VoiceModeling] Training on corpus: data/milton_content/
# [VoiceModeling] Loaded 15 content pieces
# [VoiceModeling] Training complete. Profile version: 2.0.0
```

**Verify in database:**
```bash
psql milton_publicist -c "SELECT version, avg_sentence_length, question_ratio, trained_on_corpus_size FROM voice_profile WHERE is_active = TRUE;"
```

---

## 🖥️ Testing the Dashboard

### **Start the Dashboard:**

```bash
python dashboard/approval_dashboard.py
```

Expected output:
```
[Dashboard] Started on http://0.0.0.0:8080
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

### **Open in Browser:**

Navigate to: **http://localhost:8080**

You should see:
- Purple gradient header
- 3 stat cards (Pending, Approved, Avg QA)
- Connection status (green dot when connected)
- Content queue with generated posts

### **Test Actions:**

1. **Approve Content:**
   - Click "✓ Approve" button
   - Toast notification appears
   - Content disappears from queue
   - Stats update

2. **Edit Content:**
   - Click "✏ Edit" button
   - Modal opens with content
   - Make changes
   - Click "Save & Approve"
   - Content updates and approves

3. **Reject Content:**
   - Click "✗ Reject" button
   - Modal asks for reason
   - Enter: "Testing rejection flow"
   - Click "Confirm Reject"
   - Content marked as rejected

### **Test WebSocket:**

Open browser console (F12) and look for:
```
[WS] Connected
[WS] Message: {type: 'pong', timestamp: '...'}
```

---

## 🔄 Testing Complete Workflow

### **End-to-End Test:**

**Terminal 1 - Start Media Monitor:**
```bash
python module_i/media_monitor.py
```

**Terminal 2 - Start Dashboard:**
```bash
python dashboard/approval_dashboard.py
```

**Terminal 3 - Submit Insight:**
```bash
curl -X POST -H "Authorization: Bearer dev-token" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Division III athletics programs are proving that innovation beats budget size",
    "priority": "high",
    "source": "manual"
  }' \
  http://localhost:8000/api/v1/text-insight
```

**Expected Flow (60-90 seconds):**
1. ✅ Insight stored in database
2. ✅ Media monitor finds related articles (next 30-min cycle)
3. ✅ Synthesis combines insight + news
4. ✅ Content generator creates LinkedIn post
5. ✅ QA runs 6 checks
6. ✅ If passed → appears in dashboard
7. ✅ WebSocket sends update notification
8. ✅ Dashboard shows new content
9. ✅ Review and approve
10. ✅ Ready for publishing

---

## 🎯 Manual Testing Checklist

### **Module I: Insight Capture**
- [ ] Voice note submission works
- [ ] Text insight submission works
- [ ] Insights stored in database
- [ ] Media monitor finds articles
- [ ] Synthesis creates opportunities

### **Module II: Content Generation**
- [ ] Voice profile trains successfully
- [ ] LinkedIn post generation works
- [ ] Twitter thread generation works
- [ ] QA checks run successfully
- [ ] Content stored with scores

### **Dashboard:**
- [ ] Dashboard loads at http://localhost:8080
- [ ] WebSocket connects (green dot)
- [ ] Content appears in queue
- [ ] QA scores display correctly
- [ ] Approve action works
- [ ] Edit action works
- [ ] Reject action works
- [ ] Stats update in real-time
- [ ] Mobile responsive (resize browser)

---

## 🐛 Troubleshooting

### **Test fails at Database Connection:**
```
ERROR: DATABASE_URL not set
```
**Solution:**
1. Ensure `.env` file exists
2. Check `DATABASE_URL` is set correctly
3. Verify PostgreSQL is running: `pg_isready`
4. Test connection: `psql milton_publicist -c "SELECT 1"`

### **Test fails at Voice Profile Training:**
```
ERROR: No content found in corpus directory
```
**Solution:**
1. Check `data/milton_content/` exists
2. Add at least 1 .txt file to `data/milton_content/linkedin_posts/`
3. Or let test script create sample content

### **Test fails at Content Generation:**
```
ERROR: Anthropic API call failed
```
**Solution:**
1. Verify `ANTHROPIC_API_KEY` in .env
2. Check API key is valid at https://console.anthropic.com/
3. Ensure you have credits ($5 free for new accounts)
4. Test API key:
```python
from anthropic import Anthropic
client = Anthropic(api_key="sk-ant-xxxxx")
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.content[0].text)
```

### **Dashboard shows no content:**
```
Queue is empty
```
**Solution:**
1. Run test script to generate content: `python scripts/test_system.py`
2. Or manually create content opportunity
3. Check database: `SELECT * FROM generated_content WHERE status = 'pending_approval';`

### **WebSocket won't connect:**
```
Connection status: Disconnected
```
**Solution:**
1. Refresh browser
2. Check firewall isn't blocking port 8080
3. Verify dashboard is running: `curl http://localhost:8080/health`
4. Check browser console for errors (F12)

---

## 📊 Sample Test Data

If you want to manually insert test data:

```sql
-- Insert test insight
INSERT INTO executive_insights (
    insight_id, input_type, raw_content, priority, processed
) VALUES (
    'MANUAL-TEST-001',
    'text',
    'AI technology is revolutionizing how college athletic departments engage with donors and alumni',
    'high',
    FALSE
);

-- Insert test news article
INSERT INTO news_articles (
    title, url, source, published_date, content, relevance_score
) VALUES (
    'NCAA Explores AI Applications in Athletics',
    'https://example.com/article',
    'ncaa',
    NOW(),
    'The NCAA is investigating how artificial intelligence can help athletic departments improve donor engagement and fundraising efforts...',
    0.85
);
```

---

## ✅ Success Criteria

Your system is working correctly if:

1. **All 5 tests pass** in test script
2. **Dashboard loads** without errors
3. **WebSocket connects** (green dot)
4. **Generated content appears** in queue
5. **QA scores are 70%+** (preferably 80%+)
6. **Actions work** (approve, edit, reject)
7. **Stats update** after actions

---

## 🎓 Next Steps After Testing

Once all tests pass:

1. **Collect Real Data:**
   - Get 20-50 of Milton's actual LinkedIn posts
   - Retrain voice profile with real content

2. **Generate Production Content:**
   - Create real insights (not test data)
   - Review quality of generated posts
   - Adjust thresholds if needed

3. **Deploy Dashboard:**
   - Set up on a server (or keep local)
   - Configure proper authentication
   - Enable HTTPS

4. **Build Module III:**
   - LinkedIn publisher integration
   - Twitter publisher integration
   - Content scheduler

5. **Monitor Performance:**
   - Track approval rates
   - Monitor QA scores over time
   - Refine voice profile as needed

---

## 📞 Getting Help

If tests fail or you encounter issues:

1. **Check logs** - Most errors are printed to console
2. **Review documentation** - See PROJECT_STATUS.md
3. **Verify environment** - Check .env has all required keys
4. **Test components individually** - Isolate the failing module
5. **Check database** - Use psql to verify data

---

**Happy Testing!** 🚀

When all tests pass, you'll have a complete, working AI Publicist system ready to generate voice-authentic content for Milton Overton.
