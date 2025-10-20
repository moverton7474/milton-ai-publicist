# Dashboard Media Generation Update

The Milton AI Publicist dashboard has been updated to include media generation options (graphics and videos).

**Date**: October 20, 2025
**Version**: 1.1

---

## What's New

### Media Generation Checkboxes

The dashboard now includes two new checkboxes in the content generation form:

**1. Generate Branded Graphic ($0.04)**
- Checkbox to enable AI graphic generation
- Uses DALL-E 3 to create KSU-branded visuals
- HD quality (1792x1024 pixels)
- Cost: $0.04 per graphic

**2. Partner Logo Selection**
- Dropdown appears when "Generate Branded Graphic" is checked
- Options:
  - None (KSU only)
  - VyStar Credit Union
  - GameChanger
- Automatically adds selected partner logo to bottom-right corner
- KSU logo always added to bottom-left corner

**3. Generate Avatar Video ($1.60/min) - Optional**
- Checkbox to enable HeyGen avatar video generation
- Creates photorealistic video of Milton speaking
- 1080p HD quality
- Cost: ~$1.60 per 1-minute video
- Requires HeyGen setup (see HEYGEN_QUICK_START.md)

---

## How to Use

### Step 1: Fill in Basic Information

1. **Voice Type**: Select Personal or Professional
2. **Scenario**: Choose the type of post
3. **Context**: Enter your message details

### Step 2: Enable Media Generation

**For Graphics**:
1. Check ☑ "Generate Branded Graphic ($0.04)"
2. Partner logo dropdown appears
3. Select partner (VyStar, GameChanger) or leave as "None"

**For Videos** (optional):
1. Check ☑ "Generate Avatar Video ($1.60/min)"
2. Requires HeyGen setup (see documentation)

### Step 3: Generate Content

1. Click "Generate Content"
2. Wait 30-90 seconds (longer if video is included)
3. Preview panel shows:
   - Generated text
   - Generated graphic (if enabled)
   - Generated video (if enabled and HeyGen configured)

### Step 4: Download Media

**Graphics**:
- Preview appears in right panel
- Click "Download Graphic" link
- PNG file (1792x1024 pixels)

**Videos** (if configured):
- Video player appears in right panel
- Click "Download Video" link
- MP4 file (1920x1080 pixels)

---

## Features

### Graphic Generation

**What You Get**:
- AI-generated branded visual
- KSU colors (gold #FDB913 / black #000000)
- Quote or message displayed prominently
- Professional typography and design
- KSU logo (bottom-left corner)
- Partner logo (bottom-right corner, if selected)

**Themes**:
- KSU Athletics (bold, energetic)
- Professional (clean, authoritative)
- Celebration (vibrant, exciting)

**Quality**:
- HD resolution (1792x1024)
- Perfect for LinkedIn, Twitter
- Optimized for social media

---

### Video Generation

**What You Get** (requires HeyGen setup):
- Photorealistic avatar video
- Milton speaking your announcement
- Perfect lip-sync
- Natural expressions
- Professional background
- 1080p HD quality

**Video Length**:
- Auto-calculated based on text length
- ~30-45 seconds for personal posts
- ~1-2 minutes for professional statements

**Cost**:
- Calculated at $1.60 per minute
- 30-second video = $0.80
- 1-minute video = $1.60
- 2-minute video = $3.20

---

## Dashboard UI Updates

### New Form Elements

**HTML Structure**:
```html
<!-- Graphic Generation Checkbox -->
<div class="form-group">
    <label>
        <input type="checkbox" id="includeGraphic">
        Generate Branded Graphic ($0.04)
    </label>
</div>

<!-- Partner Logo Dropdown (shown when graphic checked) -->
<div id="partnerLogoGroup">
    <label for="partnerLogo">Partner Logo:</label>
    <select id="partnerLogo">
        <option value="">None (KSU only)</option>
        <option value="vystar">VyStar Credit Union</option>
        <option value="gamechanger">GameChanger</option>
    </select>
</div>

<!-- Video Generation Checkbox -->
<div class="form-group">
    <label>
        <input type="checkbox" id="includeVideo">
        Generate Avatar Video ($1.60/min) - Optional
    </label>
</div>
```

---

### Updated API Request

**New Parameters Sent to `/api/generate`**:
```json
{
  "voice_type": "personal",
  "scenario": "partner_appreciation",
  "context": "Thank VyStar for partnership",
  "include_graphic": true,
  "include_video": false,
  "partner_logo": "vystar"
}
```

---

### Enhanced Preview Panel

**Shows Generated Media**:
```html
<!-- Graphic Preview -->
<div>
    <strong>Generated Graphic:</strong>
    <img src="/media/graphics/graphic_123.png" />
    <a href="/media/graphics/graphic_123.png" download>
        Download Graphic
    </a>
</div>

<!-- Video Preview -->
<div>
    <strong>Generated Video:</strong>
    <video controls>
        <source src="/media/videos/video_123.mp4" />
    </video>
    <a href="/media/videos/video_123.mp4" download>
        Download Video
    </a>
</div>
```

---

## Backend Integration

### API Changes

**The `/api/generate` endpoint now**:
1. Accepts `include_graphic`, `include_video`, `partner_logo` parameters
2. Generates text content (existing)
3. If `include_graphic`: Calls DALL-E 3 to generate branded image
4. If `include_graphic`: Adds KSU logo + partner logo
5. If `include_video`: Calls HeyGen to generate avatar video
6. Returns URLs for graphic and video

**Response Format**:
```json
{
  "success": true,
  "post": {
    "id": 123,
    "content": "Generated text...",
    "voice_type": "personal",
    "scenario": "partner_appreciation",
    "graphic_url": "/media/graphics/graphic_personal_123.png",
    "video_url": null,
    "word_count": 55,
    "created_at": "2025-10-20T07:00:00Z",
    "status": "pending"
  }
}
```

---

## Testing

### Test Graphic Generation

1. Open http://localhost:8081
2. Fill in form:
   - Voice: Personal
   - Scenario: Partner Appreciation
   - Context: "Thank VyStar for their incredible support"
3. Check ☑ "Generate Branded Graphic"
4. Select "VyStar Credit Union" from partner dropdown
5. Click "Generate Content"
6. Wait ~30 seconds
7. Graphic appears in preview panel

**Expected Result**:
- Text post generated (~55 words)
- AI graphic with KSU branding
- KSU logo (bottom-left)
- VyStar logo (bottom-right)
- Download link functional

---

### Test Video Generation

**Prerequisites**: HeyGen setup complete (see HEYGEN_QUICK_START.md)

1. Complete graphic generation test (above)
2. Also check ☑ "Generate Avatar Video"
3. Click "Generate Content"
4. Wait ~1-3 minutes (video takes longer)
5. Video player appears in preview panel

**Expected Result**:
- Text post generated
- Graphic generated
- Video generated (Milton speaking)
- All download links functional

---

## Costs Summary

### Per Post Examples

**Text Only** (existing):
- Cost: ~$0.10 (Claude API)
- Time: 10 seconds

**Text + Graphic**:
- Cost: ~$0.14 ($0.10 text + $0.04 graphic)
- Time: 30 seconds

**Text + Graphic + Video**:
- Cost: ~$1.74 ($0.10 text + $0.04 graphic + $1.60 video)
- Time: 1-3 minutes

---

### Monthly Costs (100 posts)

**All Text Only**:
- 100 posts = ~$10/month

**All With Graphics**:
- 100 posts = ~$14/month

**Mixed Strategy** (recommended):
- 85 posts with graphics = ~$12
- 15 posts with graphics + video = ~$26
- **Total**: ~$38/month

**Recommendation**: Use graphics for all posts ($0.04), videos for important announcements only

---

## Files Modified

**dashboard/templates/index.html**:
- Added graphic generation checkbox
- Added partner logo dropdown
- Added video generation checkbox
- Added toggle logic for partner dropdown
- Updated `generateContent()` function
- Enhanced `selectPost()` preview function
- Added graphic/video preview in preview panel

**Changes**:
- 30 new lines of HTML
- 50 new lines of JavaScript
- Fully backward compatible

---

## Troubleshooting

### Checkboxes Not Appearing

**Problem**: Dashboard doesn't show media generation options

**Solution**:
1. Hard refresh browser (Ctrl+F5)
2. Clear browser cache
3. Verify dashboard was restarted after HTML update

---

### Graphics Not Generating

**Problem**: Checkbox works, but no graphic is created

**Solution**:
1. Check OpenAI API key in .env: `OPENAI_API_KEY=sk-proj-...`
2. Check .env file was loaded: Restart dashboard
3. Check OpenAI account has credits
4. Check dashboard logs for errors

---

### Video Not Generating

**Problem**: Video checkbox works, but no video created

**Solution**:
1. Verify HeyGen setup complete (see HEYGEN_QUICK_START.md)
2. Check HeyGen API key in .env: `HEYGEN_API_KEY=hg_...`
3. Check avatar ID and voice ID configured
4. Check HeyGen account has credits remaining
5. Dashboard logs will show "Video generation not available" if not configured

---

### Partner Logo Dropdown Not Showing

**Problem**: Check graphic checkbox, but dropdown doesn't appear

**Solution**:
1. Hard refresh browser (Ctrl+F5)
2. Check browser console for JavaScript errors
3. Verify HTML includes the toggle event listener

---

### Graphic Preview Not Loading

**Problem**: Graphic generated but image doesn't display

**Solution**:
1. Check file exists: `generated_media/graphics/graphic_*.png`
2. Verify static files mounting in dashboard
3. Check image URL starts with `/media/graphics/`
4. Try accessing URL directly in browser

---

## Next Steps

### Immediate

1. **Refresh browser** at http://localhost:8081
2. **Test graphic generation** with sample post
3. **Verify preview** shows graphic correctly
4. **Download graphic** and verify quality

### Optional

1. **Set up HeyGen** for video generation (see HEYGEN_QUICK_START.md)
2. **Test video generation** once HeyGen configured
3. **Replace placeholder logos** with real logos
4. **Develop content strategy** (when to use graphics vs videos)

---

## Documentation

**Related Guides**:
- [MEDIA_GENERATION_READY.md](MEDIA_GENERATION_READY.md) - Graphics overview
- [HEYGEN_QUICK_START.md](HEYGEN_QUICK_START.md) - Video setup guide
- [HEYGEN_SETUP_GUIDE.md](HEYGEN_SETUP_GUIDE.md) - Complete video guide
- [SETUP_COMPLETE_SUMMARY.md](SETUP_COMPLETE_SUMMARY.md) - System status

---

## Summary

**Dashboard now includes**:
- ✅ Media generation checkboxes
- ✅ Partner logo selection
- ✅ Graphic preview in UI
- ✅ Video preview in UI (when HeyGen configured)
- ✅ Download links for all media
- ✅ Fully integrated workflow

**To use**:
1. Refresh browser at http://localhost:8081
2. Check "Generate Branded Graphic"
3. Select partner logo (optional)
4. Generate content
5. Preview and download graphic

**Your complete content creation system is ready!**

**Let's Go Owls! 🦉🎨**
