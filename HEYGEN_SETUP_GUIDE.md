# HeyGen Avatar Video Setup Guide

Complete step-by-step guide to set up photorealistic avatar videos of Milton Overton speaking your announcements.

---

## Overview

**What is HeyGen?**
- AI avatar video generation platform
- Creates photorealistic videos of people speaking
- Can clone voices and faces
- Professional quality output

**What You'll Get**:
- Videos of Milton speaking announcements
- Photorealistic lip-sync and expressions
- Professional video quality (1080p)
- 1-3 minute generation time per video

**Cost**:
- **Creator Plan**: $24/month
- Includes: 15 minutes of video credit
- Additional: $8 per extra minute
- **Recommended for testing**: Start with Creator plan

---

## Step 1: Sign Up for HeyGen (5 minutes)

### 1.1 Create Account

1. Go to **https://www.heygen.com**
2. Click **"Get Started Free"** or **"Sign Up"**
3. Sign up with:
   - Email address (use Milton's work email or your own)
   - Google account
   - Microsoft account

4. Verify your email address

### 1.2 Choose Plan

**Free Trial** (recommended first):
- 1 minute of video credit
- Test the system before committing
- No credit card required

**Creator Plan** ($24/month):
- 15 minutes of video per month
- Custom avatars (upload photos)
- Voice cloning
- 1080p quality
- **Recommended for production use**

**Business Plan** ($120/month):
- 30 minutes of video
- Priority rendering
- API access with higher limits

**For now**: Start with **Free Trial** to test, then upgrade to **Creator Plan** ($24/month)

---

## Step 2: Get Your API Key (2 minutes)

### 2.1 Access API Settings

1. Log in to HeyGen dashboard: **https://app.heygen.com**
2. Click your profile icon (top right)
3. Select **"Settings"** from dropdown
4. Click **"API Keys"** in left sidebar

### 2.2 Generate API Key

1. Click **"Generate New API Key"**
2. Give it a name: `Milton AI Publicist`
3. Click **"Create"**
4. **IMPORTANT**: Copy the API key immediately
   - Format: `hg_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - You won't be able to see it again!
   - Save it somewhere secure

### 2.3 Save API Key

**Copy your API key** - it looks like this:
```
hg_1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t
```

Keep this ready for Step 4.

---

## Step 3: Create Milton's Avatar (10 minutes)

### Option A: Use Stock Avatar (Quick Start)

**Fastest way to test**:

1. Go to **https://app.heygen.com/avatars**
2. Browse **"Public Avatars"**
3. Find a professional-looking male avatar
4. Click on the avatar you like
5. Note the **Avatar ID** (shown in URL or avatar details)
   - Format: `avatar_xxxxxxxx`
   - Example: `avatar_john_doe_v1`

**Recommended stock avatars**:
- Look for professional business attire
- Mature, authoritative appearance
- Friendly facial expressions
- Similar to Milton's appearance if possible

---

### Option B: Create Custom Avatar (Recommended)

**For best results** - create avatar from Milton's photo:

#### 3.1 Prepare Milton's Photo

**Photo Requirements**:
- High resolution (at least 1024x1024)
- Well-lit, professional photo
- Face clearly visible, looking at camera
- Shoulders and upper chest visible
- Neutral or friendly expression
- No sunglasses or hats
- Plain background (or will be removed)

**Recommended**:
- Professional headshot
- LinkedIn profile photo
- Official KSU Athletics photo

#### 3.2 Upload Photo to HeyGen

1. Go to **https://app.heygen.com/avatars**
2. Click **"Create Avatar"** or **"Upload Photo"**
3. Select **"Photo Avatar"** (instant, no training needed)
4. Upload Milton's photo
5. Crop and adjust if needed
6. Click **"Create Avatar"**
7. Wait 1-2 minutes for processing

#### 3.3 Get Avatar ID

1. Once created, click on the avatar
2. Note the **Avatar ID** shown in details
3. Save it for later (format: `avatar_xxxxxxxxxx`)

**Alternative**: Use **Talking Photo** feature:
- Fastest option (instant)
- Upload photo → Get instant avatar
- Good quality for most use cases

---

## Step 4: Clone Milton's Voice (15 minutes)

### Option A: Use Stock Voice (Quick Start)

**Fastest way to test**:

1. Go to **https://app.heygen.com/voices**
2. Browse **"AI Voices"**
3. Listen to voice samples
4. Find a professional male voice that sounds similar to Milton
5. Note the **Voice ID**
   - Format: `voice_xxxxxxxx`
   - Example: `voice_professional_male_1`

**Recommended stock voices**:
- Professional, authoritative tone
- Mature male voice
- Warm, friendly but professional
- American English accent

---

### Option B: Clone Milton's Voice (Recommended)

**For authentic Milton voice**:

#### 4.1 Prepare Audio Sample

**Audio Requirements**:
- High-quality recording
- At least 30 seconds of clear speech
- Milton speaking naturally
- No background noise
- No music
- One speaker only (Milton)

**Recommended**:
- Extract audio from video interview
- Record Milton reading a prepared script
- Use existing presentation audio
- Use podcast or interview audio

**Format**:
- MP3 or WAV
- 44.1kHz or higher sample rate
- Mono or stereo

#### 4.2 Create Voice Clone

**HeyGen Voice Cloning** (Creator Plan required):

1. Go to **https://app.heygen.com/voices**
2. Click **"Create Voice"** or **"Clone Voice"**
3. Upload Milton's audio sample
4. Give it a name: `Milton Overton Voice`
5. Click **"Create"**
6. Wait 5-10 minutes for processing
7. Test the voice with sample text
8. Note the **Voice ID** (format: `voice_xxxxxxxxxx`)

**Alternative Services for Voice Cloning**:
- **ElevenLabs** (https://elevenlabs.io) - Better voice quality
  - $5/month for voice cloning
  - Can use with HeyGen via audio file
- **Descript Overdub** - Good for longer content

#### 4.3 Get Voice ID

1. Once created, go to voice library
2. Click on Milton's cloned voice
3. Note the **Voice ID**
4. Save it for configuration

---

## Step 5: Configure .env File (2 minutes)

Add the credentials you collected to your `.env` file:

```bash
# HeyGen API Configuration
HEYGEN_API_KEY=hg_your_api_key_here

# Milton's Avatar ID (from Step 3)
MILTON_AVATAR_ID=avatar_xxxxxxxxxx

# Milton's Voice ID (from Step 4)
MILTON_VOICE_ID=voice_xxxxxxxxxx
```

**Example**:
```bash
HEYGEN_API_KEY=hg_1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t
MILTON_AVATAR_ID=avatar_milton_overton_v1
MILTON_VOICE_ID=voice_milton_clone_v1
```

---

## Step 6: Test Video Generation (3 minutes)

### 6.1 Test via Python Script

```bash
cd milton-publicist
python module_vi/heygen_videos.py
```

**Expected Output**:
```
======================================================================
HEYGEN AVATAR VIDEO GENERATION - DEMO
======================================================================

[INFO] Initialized HeyGen API
[INFO] Testing video generation...
[INFO] Submitting video request to HeyGen...
[OK] Video generation started!

Video ID: video_xxxxxxxxxx
Status: generating

[INFO] Checking video status (this may take 1-3 minutes)...
[INFO] Status: processing... (10 seconds)
[INFO] Status: processing... (20 seconds)
[INFO] Status: completed! (35 seconds)

[OK] Video saved to: generated_media/videos/heygen_test_20251020_123456.mp4

======================================================================
Video generation complete!
======================================================================
```

### 6.2 Test via Dashboard

1. Open **http://localhost:8081**
2. Fill in form:
   - Voice: Personal
   - Scenario: Test
   - Context: "Testing avatar video generation"
3. Check **"Generate Avatar Video"** ✓
4. Click **"Generate Content"**
5. Wait 1-3 minutes
6. Video will appear in results

---

## Step 7: Verify Video Quality

### 7.1 Check Video Output

**Location**: `generated_media/videos/`

**Expected**:
- Video file: `.mp4` format
- Resolution: 1920x1080 (1080p)
- Duration: Matches text length
- File size: 2-5MB per 30 seconds

### 7.2 Quality Checklist

**Visual Quality**:
- [ ] Avatar looks photorealistic
- [ ] Lip movements match audio perfectly
- [ ] Natural facial expressions
- [ ] Smooth motion (no stuttering)
- [ ] Professional appearance

**Audio Quality**:
- [ ] Voice sounds natural
- [ ] Clear pronunciation
- [ ] Appropriate tone and emotion
- [ ] No robotic artifacts
- [ ] Matches Milton's actual voice (if voice clone)

**If Quality Issues**:
- Try different stock avatar
- Upload higher quality photo for custom avatar
- Use longer/clearer audio sample for voice clone
- Contact HeyGen support

---

## Pricing & Usage

### HeyGen Pricing

**Creator Plan** ($24/month):
- 15 minutes of video credit
- Custom avatars
- Voice cloning
- API access
- 1080p quality

**Cost Per Video**:
- 30-second video = 0.5 minutes = $0.80
- 1-minute video = 1 minute = $1.60
- 2-minute video = 2 minutes = $3.20

**Monthly Examples**:
- 15 posts with 1-min videos = 15 minutes = $24/month (included)
- 30 posts with 30-sec videos = 15 minutes = $24/month (included)
- 50 posts with 1-min videos = 50 minutes = $24 + ($35 extra) = $59/month

### Combined System Costs

**Graphics Only** (Current):
- 100 posts with graphics = $4/month

**Graphics + Videos**:
- 15 posts with graphics + 1-min videos = $4.60/month
  - Graphics: $0.60 (15 x $0.04)
  - Videos: $24 (HeyGen subscription, includes 15 minutes)

**Recommendation**:
- Start with graphics only ($4/month)
- Add videos for important announcements (not every post)
- Use videos strategically for maximum impact

---

## Dashboard Integration

### Video Generation Options

Once HeyGen is configured, dashboard will show:

**Checkboxes**:
- [ ] Generate Branded Graphic ($0.04)
- [ ] Generate Avatar Video ($1.60 per minute)

**Video Settings**:
- Avatar: Milton Overton (custom) or select stock avatar
- Voice: Milton's voice (clone) or select stock voice
- Background: KSU colors, professional, or custom
- Duration: Auto (matches text) or specify max length

**Output**:
- MP4 video file (1080p)
- Downloadable from dashboard
- Web preview available
- Ready to post to LinkedIn/Twitter

---

## Advanced Features

### Custom Backgrounds

**Options**:
- KSU Athletics branding (gold/black)
- Office setting
- KSU stadium/arena
- Solid color
- Custom image upload

**Configuration**:
```python
# In module_vi/heygen_videos.py
background = {
    "type": "image",
    "url": "https://your-cdn.com/ksu-office-background.jpg"
}
```

### Multiple Avatars

**Use Cases**:
- Milton for personal voice posts
- Generic professional for official statements
- Different avatars for different scenarios

**Configuration**:
```python
# .env file
MILTON_AVATAR_PERSONAL=avatar_milton_v1
MILTON_AVATAR_PROFESSIONAL=avatar_milton_suit_v1
MILTON_AVATAR_CASUAL=avatar_milton_polo_v1
```

### Video Templates

**Create reusable templates**:
- Game day announcement template
- Partner appreciation template
- Coaching announcement template
- Each with specific background and styling

---

## Best Practices

### When to Use Videos

**Use avatar videos for**:
- Major announcements (coaching hires, facility updates)
- Partner appreciation (high-value relationships)
- Important milestones (championships, records)
- Personal messages to team/staff
- Weekly video updates

**Don't use videos for**:
- Every single post (too expensive)
- Quick updates or news shares
- Simple game scores
- Routine content

**Cost-Effective Strategy**:
- Graphics for all posts ($0.04 each)
- Videos for 1-2 important posts per week
- Use 15 minutes/month allocation strategically

### Script Optimization

**Keep videos short**:
- 30-45 seconds = sweet spot for social media
- 1-2 minutes max for important announcements
- Shorter = lower cost + better engagement

**Write for speech**:
- Conversational tone
- Short sentences
- Natural pauses
- Avoid complex words

### Quality Tips

**Better Avatar Results**:
- Use high-quality source photo
- Good lighting in photo
- Clear facial features
- Professional appearance

**Better Voice Results**:
- Longer audio samples = better clone
- Clean audio (no background noise)
- Natural speaking pace
- Variety of tones and expressions

---

## Troubleshooting

### API Key Issues

**Error**: `Invalid API key`
- Check key is correct in .env file
- No extra spaces or quotes
- Key starts with `hg_`
- Regenerate key if needed

### Avatar Not Found

**Error**: `Avatar ID not found`
- Verify avatar ID is correct
- Check avatar is in your account
- Try using stock avatar first

### Voice Not Found

**Error**: `Voice ID not found`
- Verify voice ID is correct
- Check voice clone completed successfully
- Try using stock voice first

### Video Generation Failed

**Error**: `Video generation failed`
- Check HeyGen account has credits remaining
- Verify text isn't too long (max ~500 words)
- Try shorter text
- Check HeyGen status page

### Slow Generation

**Issue**: Videos taking >5 minutes
- Normal during peak hours
- HeyGen queues requests
- Try off-peak hours
- Upgrade to Business plan for priority

---

## Alternative Services

If HeyGen doesn't meet your needs:

### D-ID

**Website**: https://www.d-id.com
**Pricing**: $5.90/month for 10 minutes
**Pros**: Cheaper, good quality
**Cons**: Less realistic than HeyGen

### Synthesia

**Website**: https://www.synthesia.io
**Pricing**: $30/month for 10 minutes
**Pros**: Very professional, many avatars
**Cons**: More expensive than HeyGen

### Colossyan

**Website**: https://www.colossyan.com
**Pricing**: $28/month for 10 minutes
**Pros**: Good for training videos
**Cons**: Less natural expressions

**Recommendation**: Start with HeyGen - best balance of quality, cost, and features

---

## Next Steps

### Immediate

1. **Sign up for HeyGen free trial**
   - Test with stock avatar + stock voice
   - Generate 1 test video
   - Verify quality meets expectations

2. **If satisfied, upgrade to Creator Plan**
   - $24/month for 15 minutes
   - Unlock custom avatar + voice cloning

3. **Create custom avatar**
   - Upload Milton's photo
   - Test avatar quality

4. **Clone Milton's voice**
   - Record or find good audio sample
   - Create voice clone
   - Test voice quality

5. **Configure .env file**
   - Add API key, avatar ID, voice ID
   - Test integration

6. **Generate first video**
   - Use dashboard or Python script
   - Create partner appreciation video
   - Post to LinkedIn

### Long-term

- Create multiple avatars (different settings/outfits)
- Build video template library
- Develop video posting strategy
- Track engagement (video vs graphic posts)
- Optimize video usage for budget

---

## Summary

**Setup Time**: 30 minutes total
- HeyGen signup: 5 min
- API key: 2 min
- Custom avatar: 10 min
- Voice clone: 15 min
- Configuration: 2 min
- Testing: 5 min

**Cost**: $24/month (Creator Plan)
- Includes 15 minutes of video
- $1.60 per 1-minute video
- Great for 10-15 important posts/month

**Value**:
- Photorealistic avatar videos
- Milton's face and voice
- Professional quality
- Higher engagement than text/graphics alone

**Recommendation**:
1. Start with free trial to test
2. If quality is good, upgrade to Creator Plan
3. Use videos strategically (not every post)
4. Combine with graphics for maximum impact

**Your complete content arsenal**:
- Text (free) - Milton's authentic voice
- Graphics ($0.04) - Branded visuals
- Videos ($1.60/min) - Maximum impact

**Ready to get started?** Go to https://www.heygen.com and sign up!
