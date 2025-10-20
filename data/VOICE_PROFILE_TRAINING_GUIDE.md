# Voice Profile Training Guide for Milton Overton

**Purpose:** Collect Milton's existing content to train the AI voice modeling system for authentic content generation.

---

## 📋 Data Collection Checklist

### 1. LinkedIn Profile Data (Manual Collection Required)

**LinkedIn Profile:** https://www.linkedin.com/in/miltonoverton/

#### Information to Extract:

**Current Position:**
- [ ] Job title
- [ ] Organization (Keuka College)
- [ ] Location
- [ ] Duration in current role

**About/Summary Section:**
- [ ] Copy full bio text
- [ ] Note key phrases and positioning statements
- [ ] Identify core messaging themes

**Experience History:**
- [ ] Previous roles and organizations
- [ ] Career progression timeline
- [ ] Key achievements listed

**Education:**
- [ ] Degrees and institutions
- [ ] Relevant certifications
- [ ] Academic background

**Skills & Endorsements:**
- [ ] Listed professional skills
- [ ] Top endorsed skills
- [ ] Areas of expertise

---

### 2. LinkedIn Posts Collection (Target: 50+ posts)

**How to Collect:**
1. Visit Milton's LinkedIn profile
2. Scroll through "Posts" or "Activity" section
3. Copy text of at least 50 recent posts
4. Save each post as a separate text file in `data/milton_content/linkedin_posts/`

**File naming:** `linkedin_post_YYYYMMDD_001.txt`

**For each post, capture:**
- [ ] Full post text
- [ ] Date posted
- [ ] Engagement metrics (likes, comments, shares) if visible
- [ ] Hashtags used
- [ ] Links or media referenced
- [ ] Post type (text-only, image, article share, etc.)

**Sample format for each file:**
```
Date: 2024-10-15
Engagement: 42 likes, 8 comments, 3 shares
Hashtags: #CollegeSports #AIInnovation #Leadership
Type: Text with image

[FULL POST TEXT HERE]
```

---

### 3. Articles & Long-form Content

**Sources to Check:**
- [ ] LinkedIn articles (if published)
- [ ] Medium posts
- [ ] Blog posts
- [ ] Guest articles
- [ ] Conference presentations
- [ ] Podcast transcripts (if available)

**Save to:** `data/milton_content/articles/`

---

### 4. Twitter/X Content (if available)

**Profile:** [To be determined]

- [ ] Recent tweets (last 6 months)
- [ ] Thread formats
- [ ] Reply patterns
- [ ] Hashtag usage

**Save to:** `data/milton_content/twitter/`

---

### 5. Public Speeches/Presentations

- [ ] Conference talks
- [ ] Webinar presentations
- [ ] Panel discussions
- [ ] Video interviews

**Save to:** `data/milton_content/speeches/`

---

### 6. Media Mentions & Interviews

- [ ] News articles quoting Milton
- [ ] Interview transcripts
- [ ] Press releases

**Save to:** `data/milton_content/media/`

---

## 🎯 Voice Analysis Dimensions to Note

As you collect content, manually note these patterns:

### Lexical (Vocabulary)
- [ ] Common words/phrases Milton uses frequently
- [ ] Domain-specific terminology
- [ ] Unique expressions or catchphrases
- [ ] Technical vs. accessible language balance

### Syntactic (Sentence Structure)
- [ ] Typical sentence length (short/medium/long)
- [ ] Use of questions
- [ ] Use of lists or bullet points
- [ ] Paragraph length preferences

### Rhetorical Devices
- [ ] Does he use data/statistics often?
- [ ] Personal stories vs. analytical content ratio
- [ ] Use of metaphors or analogies
- [ ] Calls-to-action patterns

### Tone & Formality
- [ ] Professional but approachable? Formal? Casual?
- [ ] Optimistic? Analytical? Visionary?
- [ ] First-person vs. third-person perspective
- [ ] Emotional tone (excited, measured, inspiring)

### Content Themes
- [ ] What topics appear most often?
- [ ] How does he position himself?
- [ ] What stories does he tell repeatedly?
- [ ] What values come through?

---

## 📊 Minimum Training Data Requirements

For high-quality voice modeling, we need:

| Content Type | Minimum | Recommended | Status |
|--------------|---------|-------------|--------|
| LinkedIn Posts | 30 | 50+ | ⬜ |
| Long-form Articles | 5 | 10+ | ⬜ |
| Speeches/Presentations | 2 | 5+ | ⬜ |
| Twitter/Threads | 20 | 50+ | ⬜ |
| Total Word Count | 10,000 | 25,000+ | ⬜ |

---

## 🔍 Known Information from Implementation Guide

Based on the system specification, we know:

**Milton Overton's Profile:**
- **Position:** Athletic Director at Keuka College
- **Location:** Keuka College (New York)
- **Key Innovation:** Built KSU (Keuka State University?) Donor Fund AI system
- **Positioning:** AI Technology Innovator in college sports
- **Avatar Usage:** Uses Synthesia/HeyGen AI avatar for donor outreach

**Thought Leadership Pillars:**
1. **AI Innovation in Sports Business** (The Founder)
   - Practical AI implementation
   - Technology in athletics
   - Data-driven decision making

2. **Leadership & Vision** (The AD)
   - Executive strategy
   - Athletic department management
   - Organizational transformation

3. **Future of College Sports** (The Futurist)
   - NIL trends
   - Conference realignment
   - Industry evolution

**Voice Profile Characteristics (from spec):**
- **Tone:** Visionary, Strategic, Approachable
- **Style:** 80% strategic insights, 20% personal stories
- **Avg Sentence Length:** ~18 words
- **Question Ratio:** ~15% of sentences
- **Avoids:** Generic AI speak, jargon without context
- **Embraces:** Data/statistics, specific examples, forward-thinking perspective

---

## 📁 File Structure for Training Data

Create this structure in `data/milton_content/`:

```
data/
└── milton_content/
    ├── profile/
    │   └── linkedin_profile.txt
    ├── linkedin_posts/
    │   ├── linkedin_post_20241015_001.txt
    │   ├── linkedin_post_20241014_001.txt
    │   └── ... (50+ files)
    ├── articles/
    │   ├── article_001_title.txt
    │   └── ...
    ├── twitter/
    │   ├── tweet_thread_001.txt
    │   └── ...
    ├── speeches/
    │   ├── conference_talk_001.txt
    │   └── ...
    └── media/
        ├── interview_001.txt
        └── ...
```

---

## 🚀 Quick Start Data Collection

**Step 1:** Visit Milton's LinkedIn profile
- Copy the "About" section → Save to `data/milton_content/profile/linkedin_profile.txt`

**Step 2:** Scroll through activity
- Copy 10 recent posts → Save to `data/milton_content/linkedin_posts/`

**Step 3:** Run preliminary training
```bash
python scripts/train_voice_profile.py --corpus-dir data/milton_content/ --preliminary
```

This will give us a baseline voice profile that can be refined as more content is added.

---

## 🤖 Automated Collection (Alternative)

If Milton provides access, we can use:

**LinkedIn API** (requires authorization):
- Can fetch recent posts programmatically
- Requires Milton's LinkedIn API credentials
- Limited by API rate limits

**Manual Export** (easier):
- LinkedIn allows downloading your data
- Milton can request archive from LinkedIn Settings
- Includes all posts, comments, messages

---

## 📝 Template: LinkedIn Post Collection

Copy and paste this for each post you collect:

```
---
POST ID: [Sequential number]
DATE: YYYY-MM-DD
URL: [LinkedIn post URL if available]
ENGAGEMENT:
  Likes: [number]
  Comments: [number]
  Shares: [number]
HASHTAGS: [list]
MEDIA: [none | image | video | link]
PILLAR: [AI Innovation | Leadership | Future of Sports]
---

[FULL POST TEXT HERE - PRESERVE FORMATTING]

---
NOTES:
- [Any observations about voice, tone, style]
- [Notable phrases or patterns]
---
```

---

## ✅ Next Steps After Data Collection

Once you have the training data:

1. **Run Voice Profile Training:**
   ```bash
   python scripts/train_voice_profile.py --corpus-dir data/milton_content/
   ```

2. **Review Generated Profile:**
   - Check `voice_profile` table in database
   - Verify captured patterns match Milton's actual style

3. **Test Content Generation:**
   - Generate sample LinkedIn post
   - Compare against real Milton posts
   - Adjust parameters if needed

4. **Iterate:**
   - Add more training data if voice match is low
   - Fine-tune voice profile parameters
   - Test on different content types

---

## 🎓 Content Collection Tips

**Do:**
- Preserve exact formatting (line breaks, capitalization)
- Note context (what prompted the post)
- Include full text even if long
- Capture variety (different topics, tones)

**Don't:**
- Edit or clean up typos (we need authentic voice)
- Skip posts that seem similar (patterns matter)
- Exclude comments/replies (conversational tone is valuable)
- Forget metadata (dates, engagement help with analysis)

---

## 🔒 Privacy & Ethics

**Important:**
- Only collect publicly available content
- This is for Milton's own brand automation
- Training data stays local/in Milton's control
- No sharing of training data with third parties
- Voice profile used only for Milton's authenticated content

---

## 📞 Support

If you have questions about:
- What content to collect
- How to structure files
- Technical issues with training

Contact: [System administrator]

---

**Status:** Ready for data collection | **Target:** 50+ LinkedIn posts + 10 articles | **ETA:** 2-4 hours manual work
