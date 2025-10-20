# HeyGen Quick Start Checklist

30-minute setup to add avatar videos to your Milton AI Publicist.

---

## Quick Setup Checklist

### ☐ Step 1: Sign Up (5 min)

1. Go to https://www.heygen.com
2. Click "Get Started Free"
3. Sign up with email or Google
4. Start with **Free Trial** (1 minute of video credit)

---

### ☐ Step 2: Get API Key (2 min)

1. Log in to https://app.heygen.com
2. Click profile icon → **Settings**
3. Click **API Keys** in sidebar
4. Click **"Generate New API Key"**
5. Name it: `Milton AI Publicist`
6. **Copy the key** (starts with `hg_`)
7. Save it somewhere secure

**Your API Key**:
```
hg_____________________________________
```

---

### ☐ Step 3: Choose Avatar (5 min)

**Option A: Use Stock Avatar** (fastest):
1. Go to https://app.heygen.com/avatars
2. Browse "Public Avatars"
3. Pick professional male avatar
4. Copy **Avatar ID**

**Option B: Create Custom Avatar** (recommended):
1. Get high-quality photo of Milton
   - Professional headshot
   - Face clearly visible
   - Good lighting
   - Plain background
2. Upload to HeyGen avatars
3. Wait 1-2 minutes for processing
4. Copy **Avatar ID**

**Your Avatar ID**:
```
avatar_____________________________________
```

---

### ☐ Step 4: Choose Voice (5 min)

**Option A: Use Stock Voice** (fastest):
1. Go to https://app.heygen.com/voices
2. Browse "AI Voices"
3. Listen to samples
4. Pick professional male voice
5. Copy **Voice ID**

**Option B: Clone Milton's Voice** (recommended):
1. Get 30+ seconds of Milton speaking clearly
   - No background noise
   - Natural speaking pace
2. Upload to HeyGen voice cloning
3. Wait 5-10 minutes for processing
4. Test the cloned voice
5. Copy **Voice ID**

**Your Voice ID**:
```
voice_____________________________________
```

---

### ☐ Step 5: Update .env File (2 min)

Open `.env` file and add:

```bash
# HeyGen Configuration
HEYGEN_API_KEY=hg_your_key_here
MILTON_AVATAR_ID=avatar_your_id_here
MILTON_VOICE_ID=voice_your_id_here
```

**Replace with your actual IDs from Steps 2-4**

---

### ☐ Step 6: Test Video Generation (3 min)

**Option A: Test via Python**:
```bash
cd milton-publicist
python module_vi/heygen_videos.py
```

**Option B: Test via Dashboard**:
1. Restart dashboard to load new .env
2. Open http://localhost:8081
3. Fill in form
4. Check "Generate Avatar Video"
5. Click "Generate Content"
6. Wait 1-3 minutes

**Expected**: Video saved to `generated_media/videos/`

---

### ☐ Step 7: Upgrade to Creator Plan (2 min)

**If free trial worked well**:

1. Go to https://app.heygen.com/settings/billing
2. Click **"Upgrade"**
3. Select **Creator Plan** ($24/month)
4. Enter payment details
5. Confirm

**You now have**:
- 15 minutes of video per month
- Custom avatars
- Voice cloning
- API access

---

## Verification Checklist

After setup, verify everything works:

- [ ] API key is valid (no errors)
- [ ] Avatar appears in HeyGen dashboard
- [ ] Voice sounds good when tested
- [ ] Video generates successfully
- [ ] Video quality looks professional
- [ ] Dashboard shows video checkbox
- [ ] Video downloads correctly

---

## Quick Reference

**HeyGen Dashboard**: https://app.heygen.com

**API Settings**: https://app.heygen.com/settings/api-keys

**Avatars**: https://app.heygen.com/avatars

**Voices**: https://app.heygen.com/voices

**Billing**: https://app.heygen.com/settings/billing

**Support**: https://help.heygen.com

---

## Cost Summary

**Free Trial**:
- 1 minute of video credit
- Test before committing
- No credit card required

**Creator Plan** ($24/month):
- 15 minutes of video
- $1.60 per 1-minute video
- Custom avatars + voice cloning
- **Recommended**

**Usage Examples**:
- 15 posts with 1-min videos = $24/month (all included)
- 30 posts with 30-sec videos = $24/month (all included)

---

## Next Steps After Setup

1. **Generate first real video**:
   - Partner appreciation post
   - 30-45 seconds
   - Test on LinkedIn

2. **Develop video strategy**:
   - Use for important announcements only
   - Combine graphics + videos for max impact
   - Track engagement vs text-only posts

3. **Optimize usage**:
   - Keep videos short (30-60 sec)
   - Use 15 minutes strategically
   - Graphics for routine posts, videos for big news

---

## Troubleshooting

**Video not generating?**
- Check API key is correct in .env
- Verify avatar ID and voice ID
- Check HeyGen credits remaining
- Restart dashboard after .env changes

**Poor video quality?**
- Use higher quality source photo
- Try different stock avatar
- Re-record voice sample with better audio
- Contact HeyGen support

**Need help?**
- HeyGen Help Center: https://help.heygen.com
- HeyGen Discord: https://discord.gg/heygen
- Email: support@heygen.com

---

## Complete Setup Summary

**Total Time**: 30 minutes
**Total Cost**: $0 (free trial) or $24/month (Creator Plan)

**What You'll Have**:
- Photorealistic avatar videos
- Milton's face and voice
- Professional quality output
- Integrated with dashboard

**Your Content Arsenal**:
1. **Text**: Milton's authentic voice (free)
2. **Graphics**: Branded visuals ($0.04 each)
3. **Videos**: Maximum impact ($1.60/minute)

**Ready?** Start at https://www.heygen.com 🎬
