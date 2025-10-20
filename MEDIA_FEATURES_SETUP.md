# Media Features Setup Guide

**AI-Generated Graphics + Avatar Videos + Logo Overlays**

---

## ✅ What's Been Built

All media generation features are now complete and integrated into the dashboard!

### Module VI: Media Generation
1. ✅ **Google Imagen 3 / DALL-E 3 Graphics** - AI-generated quote graphics
2. ✅ **HeyGen Avatar Videos** - Photorealistic video avatars
3. ✅ **Logo Overlay System** - KSU + partner logo placement
4. ✅ **Complete Workflow** - Text → Graphic → Logos → Video → Publish
5. ✅ **Dashboard Integration** - All features accessible from web UI

**Total Code**: 800+ lines across 4 new files

---

## 🚀 Quick Start

### Option 1: Use DALL-E 3 (Easiest - Recommended)

**What you need**: OpenAI API key

**Setup** (2 minutes):
```bash
# Install OpenAI
pip install openai Pillow

# Set API key in .env
echo "OPENAI_API_KEY=your_key_here" >> .env
```

**Cost**: $0.04 per image (1792x1024 HD quality)

**Test it**:
```bash
cd milton-publicist
python module_vi/imagen_graphics.py
```

---

### Option 2: Use Google Imagen 3 (Best Quality)

**What you need**: Google Cloud account + Imagen API access

**Setup** (30 minutes):
1. Create Google Cloud project
2. Enable Vertex AI API
3. Create service account
4. Download credentials JSON
5. Set environment variables

**Cost**: $0.02 per image (50% cheaper than DALL-E)

**See**: [MEDIA_GENERATION_GUIDE.md](MEDIA_GENERATION_GUIDE.md) Section 2A

---

### Option 3: HeyGen Avatar Videos (Optional)

**What you need**: HeyGen account

**Setup** (10 minutes):
1. Sign up at [HeyGen.com](https://www.heygen.com)
2. Get API key from dashboard
3. Add to .env: `HEYGEN_API_KEY=your_key_here`

**Cost**: $24/month for 15 minutes of video

**Test it**:
```bash
python module_vi/heygen_videos.py
```

---

## 📋 Complete Setup Steps

### Step 1: Install Dependencies

```bash
cd milton-publicist

# For graphics (choose one):
pip install openai Pillow              # DALL-E 3
# OR
pip install google-cloud-aiplatform Pillow  # Imagen 3

# For videos (optional):
pip install requests

# For logo overlay:
pip install Pillow
```

---

### Step 2: Configure API Keys

Edit `.env` file:

```bash
# For DALL-E 3 graphics (recommended)
OPENAI_API_KEY=sk-your-openai-key-here

# OR for Google Imagen 3 (optional, better quality)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# For HeyGen videos (optional)
HEYGEN_API_KEY=your-heygen-key-here
MILTON_AVATAR_ID=your-avatar-id  # After creating custom avatar
MILTON_VOICE_ID=your-voice-id    # After voice cloning
```

---

### Step 3: Add Logo Files

Place your logo files in `assets/logos/`:

```bash
mkdir -p assets/logos

# Add your logo files:
# assets/logos/ksu_logo.png          ← KSU logo (PNG with transparency)
# assets/logos/vystar_logo.png       ← VyStar logo
# assets/logos/gamechanger_logo.png  ← GameChanger logo
```

**Don't have logos yet?** The system will create placeholders automatically.

**Logo Requirements**:
- Format: PNG with transparent background (RGBA)
- Recommended size: 400x200 pixels or similar
- File names: exactly `ksu_logo.png`, `vystar_logo.png`, etc.

---

### Step 4: Test Media Generation

**Test graphics**:
```bash
python module_vi/imagen_graphics.py
```

**Expected output**:
```
[INFO] Initialized OpenAI DALL-E 3
[INFO] Generating KSU Athletics quote graphic...
[OK] Graphic saved to: generated_media/graphics/ksu_quote_example.png
```

**Test logos**:
```bash
python module_vi/logo_overlay.py
```

**Test complete workflow**:
```bash
python module_vi/complete_media_workflow.py
```

---

## 🎨 Using Media Features in Dashboard

### From the Web UI (http://localhost:8081)

The dashboard has been updated with media generation options!

**Generate Content with Graphic**:
1. Select voice type and scenario
2. Enter context
3. Check ✓ **"Generate Branded Graphic"** (new checkbox)
4. Select partner logo from dropdown (KSU, VyStar, GameChanger)
5. Click "Generate Content"

**Result**: Text post + AI-generated graphic with logos

**Generate Content with Video** (if HeyGen configured):
1. Follow steps above
2. Also check ✓ **"Generate Avatar Video"**
3. Wait 1-3 minutes for video rendering

**Result**: Text post + Graphic + Avatar video

---

## 📊 Feature Comparison

| Feature | DALL-E 3 | Google Imagen 3 | HeyGen Videos |
|---------|----------|-----------------|---------------|
| **Quality** | Excellent | Best | Photorealistic |
| **Cost per use** | $0.04 | $0.02 | $1.60 (based on $24/15min) |
| **Setup time** | 2 min | 30 min | 10 min |
| **Speed** | 10-30 sec | 10-30 sec | 1-3 min |
| **Ease of use** | Easiest | Moderate | Easy |
| **Recommendation** | ✅ Start here | ⭐ Best quality | 🎥 Optional |

---

## 💡 Usage Examples

### Example 1: Simple Partner Appreciation with Graphic

**Dashboard Input**:
- Voice: Personal
- Scenario: Partner Appreciation
- Context: "Thank VyStar for Arena naming rights partnership"
- ✓ Generate Graphic
- Partner Logo: VyStar

**Output**:
- ✅ 55-word authentic post ("Let's Go Owls!")
- ✅ AI-generated graphic (KSU colors, professional design)
- ✅ KSU logo (bottom left)
- ✅ VyStar logo (bottom right)

**Time**: 30-60 seconds
**Cost**: $0.04 (DALL-E) or $0.02 (Imagen)

---

### Example 2: Complete Media Package

**Dashboard Input**:
- Voice: Professional
- Scenario: Coaching Announcement
- Context: "Hiring Sarah Mitchell as Assistant Coach"
- ✓ Generate Graphic
- ✓ Generate Video
- Partner Logo: None

**Output**:
- ✅ 245-word professional statement
- ✅ AI-generated announcement graphic
- ✅ KSU logo overlay
- ✅ 1-minute avatar video of Milton speaking the announcement

**Time**: 3-5 minutes (video rendering)
**Cost**: $0.04 (graphic) + $1.60 (video) = $1.64

---

## 🔧 Advanced Usage

### API Endpoints

**Generate with media via API**:
```bash
curl -X POST http://localhost:8081/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "voice_type": "personal",
    "scenario": "Partner Appreciation",
    "context": "Thank VyStar for partnership",
    "include_graphic": true,
    "include_video": false,
    "partner_logo": "vystar"
  }'
```

**Response**:
```json
{
  "success": true,
  "post": {
    "id": 1,
    "content": "We want to thank VyStar...",
    "graphic_url": "/media/graphics/graphic_personal_20251020_143022.png",
    "video_url": null
  }
}
```

---

### Python API

**Use media workflow directly**:
```python
from module_vi.complete_media_workflow import CompleteMediaWorkflow

workflow = CompleteMediaWorkflow()

package = workflow.create_post_package(
    text_content="Your post text here",
    voice_type="personal",
    include_graphic=True,
    include_video=True,
    partner_logo="vystar"
)

print(f"Graphic: {package['graphic_path']}")
print(f"Video: {package['video_path']}")
```

---

## 🎓 Customization

### Custom Graphic Themes

Edit `module_vi/imagen_graphics.py` to add your own themes:

```python
# Add to _build_prompt() method
"your_theme_name": f"""
    Your custom prompt here...

    Text to Display:
    "{quote}"

    Visual Style:
    - Your style guidelines
"""
```

### Custom Logo Layouts

Edit `module_vi/logo_overlay.py` to add layouts:

```python
# In add_logos() method
elif layout == "your_layout":
    # Your custom logo positioning
```

---

## 🐛 Troubleshooting

### Graphics not generating

**Error**: `No AI graphics provider available`

**Solution**: Install OpenAI and set API key
```bash
pip install openai
echo "OPENAI_API_KEY=your_key" >> .env
```

---

### Logos not appearing

**Issue**: Generated graphic doesn't have logos

**Check**:
1. Logo files exist in `assets/logos/`
2. Files are PNG format with transparency
3. File names match exactly: `ksu_logo.png`, `vystar_logo.png`

**Create placeholders**:
```bash
python module_vi/logo_overlay.py
```

---

### Video generation fails

**Error**: `HeyGen API key required`

**Solution**:
1. Sign up at HeyGen.com
2. Get API key
3. Add to .env: `HEYGEN_API_KEY=your_key`

---

### "Module not found" errors

**Solution**: Install missing dependencies
```bash
pip install openai Pillow requests
```

---

## 📈 Performance Optimization

### Caching Generated Graphics

Graphics are saved to `generated_media/graphics/` and reused if you regenerate the same content.

### Async Video Generation

Videos generate in the background. The dashboard continues working while video renders.

### Cost Optimization

**Tips to reduce costs**:
1. Use DALL-E 3 standard quality instead of HD: Save 50%
2. Generate graphics only for important posts
3. Batch generate multiple posts, then add graphics later
4. Reuse graphics for similar content

---

## 🎯 Next Steps

**Immediate** (Ready now):
1. Install OpenAI: `pip install openai Pillow`
2. Set OPENAI_API_KEY in .env
3. Test: `python module_vi/imagen_graphics.py`
4. Use in dashboard: Check "Generate Graphic"

**Optional** (Better quality):
1. Set up Google Cloud + Imagen 3 (30 min)
2. Save 50% on graphic costs

**Optional** (Videos):
1. Sign up for HeyGen ($24/month)
2. Create custom avatar
3. Clone your voice
4. Generate avatar videos

---

## 📚 Documentation

**Full guides**:
- [MEDIA_GENERATION_GUIDE.md](MEDIA_GENERATION_GUIDE.md) - Complete technical guide
- [IMPLEMENTATION_STATUS_REVIEW.md](IMPLEMENTATION_STATUS_REVIEW.md) - What's been built
- [COMPLETE_SYSTEM_OVERVIEW.md](COMPLETE_SYSTEM_OVERVIEW.md) - Everything

**Code files**:
- `module_vi/imagen_graphics.py` - AI graphics generation
- `module_vi/logo_overlay.py` - Logo system
- `module_vi/heygen_videos.py` - Avatar videos
- `module_vi/complete_media_workflow.py` - Complete workflow

---

## ✅ Summary

**What's Ready**:
- ✅ AI-generated graphics (DALL-E 3 or Imagen 3)
- ✅ Logo overlay system (KSU + partners)
- ✅ Avatar videos (HeyGen)
- ✅ Dashboard integration
- ✅ Complete workflow

**Setup Time**: 2 minutes (DALL-E) to 30 minutes (full features)

**Cost**: $0.02-0.04 per graphic, $1.60 per minute of video

**Ready to use!** Set your OPENAI_API_KEY and start generating!

---

**Let's Go Owls!** 🦉
