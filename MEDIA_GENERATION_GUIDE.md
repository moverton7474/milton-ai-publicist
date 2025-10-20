# Media Generation Guide

**AI-Generated Graphics, Avatars, and Branded Content**

---

## 1. Personal Avatar Videos

### Option A: HeyGen (Recommended - Best Quality)

**HeyGen** creates photorealistic avatar videos from scripts.

#### Step 1: Create HeyGen Account

1. Go to [HeyGen.com](https://www.heygen.com)
2. Sign up (Free tier: 1 minute/month, Paid: $24/month for 15 min)
3. Create avatar or use stock avatars

#### Step 2: Train Custom Avatar (Optional)

**Requirements**:
- 5-10 minutes of video footage
- Good lighting, clear audio
- Looking at camera
- Various expressions

**Process**:
1. Upload training video
2. Wait 24-48 hours for processing
3. Avatar is ready to use

#### Step 3: Integrate with Milton AI Publicist

Create `module_vi/heygen_integration.py`:

```python
import requests
import os

class HeyGenIntegration:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("HEYGEN_API_KEY")
        self.base_url = "https://api.heygen.com/v1"

    def create_video(self, script: str, avatar_id: str):
        """Generate avatar video from script"""

        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,  # Your custom avatar
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": script,
                    "voice_id": "your_voice_id"  # Cloned voice
                },
                "background": {
                    "type": "color",
                    "value": "#0066CC"  # KSU blue
                }
            }],
            "dimension": {
                "width": 1920,
                "height": 1080
            }
        }

        response = requests.post(
            f"{self.base_url}/video.generate",
            headers=headers,
            json=payload
        )

        return response.json()
```

#### Step 4: Add to Dashboard

Add button in dashboard UI:
```html
<button onclick="generateVideo(postId)">Generate Avatar Video</button>
```

---

### Option B: D-ID (Alternative)

Similar to HeyGen, specializes in talking head videos.

**Pricing**: $5.90/month for 20 minutes

[D-ID.com](https://www.d-id.com)

---

### Option C: Synthesia (Enterprise)

Most professional, used by Fortune 500 companies.

**Pricing**: $22/month (Starter)

[Synthesia.io](https://www.synthesia.io)

---

## 2. AI-Generated Graphics

### Option A: Google Imagen 3 (Latest, Best Quality)

**Google's Imagen 3** is now available via Vertex AI.

#### Setup

1. Create Google Cloud Project
2. Enable Vertex AI API
3. Get API credentials

#### Integration

Create `module_vi/imagen_graphics.py`:

```python
from google.cloud import aiplatform
from google.oauth2 import service_account
import base64
import os

class ImagenGraphicsGenerator:
    def __init__(self, project_id=None, location="us-central1"):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location

        # Initialize Vertex AI
        credentials = service_account.Credentials.from_service_account_file(
            'google-cloud-credentials.json'
        )

        aiplatform.init(
            project=self.project_id,
            location=self.location,
            credentials=credentials
        )

    def generate_quote_graphic(
        self,
        quote: str,
        theme: str = "ksu_athletics",
        include_logo: bool = True
    ):
        """
        Generate branded quote graphic

        Args:
            quote: The quote text
            theme: Visual theme (ksu_athletics, professional, celebration)
            include_logo: Whether to include KSU logo
        """

        # Build prompt based on theme
        prompts = {
            "ksu_athletics": f"""
                Professional athletic department social media graphic.

                Design elements:
                - Kennesaw State University gold (#FDB913) and black (#000000) colors
                - Modern, clean design
                - Athletic energy
                - Professional typography

                Text overlay: "{quote}"

                Style: Bold, inspiring, collegiate athletics branding
                Layout: Horizontal 16:9 ratio for LinkedIn/Twitter

                Include subtle owl motif (KSU mascot)
            """,

            "professional": f"""
                Executive leadership quote graphic.

                Design: Minimalist, sophisticated
                Colors: Navy blue, gold accents, white
                Typography: Modern serif for quote, sans-serif for attribution

                Text: "{quote}"

                Style: Forbes/Harvard Business Review aesthetic
            """,

            "celebration": f"""
                Vibrant celebration announcement graphic.

                Design: Energetic, bold
                Colors: Gold, black, with dynamic gradients
                Elements: Confetti, stars, celebratory motifs

                Text: "{quote}"

                Style: ESPN/Athletic Department social media
            """
        }

        prompt = prompts.get(theme, prompts["ksu_athletics"])

        # Call Imagen 3 API
        endpoint = aiplatform.Endpoint(
            endpoint_name=f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/imagen-3.0-generate-001"
        )

        instances = [{
            "prompt": prompt,
            "aspectRatio": "16:9",
            "numberOfImages": 1,
            "outputOptions": {
                "mimeType": "image/png"
            }
        }]

        response = endpoint.predict(instances=instances)

        # Get generated image
        image_data = response.predictions[0]["bytesBase64Encoded"]
        image_bytes = base64.b64decode(image_data)

        # Optionally overlay KSU logo
        if include_logo:
            image_bytes = self._overlay_logo(image_bytes)

        return image_bytes

    def _overlay_logo(self, image_bytes):
        """Overlay KSU logo on generated image"""
        from PIL import Image
        import io

        # Load generated image
        img = Image.open(io.BytesIO(image_bytes))

        # Load KSU logo
        logo = Image.open("assets/ksu_logo.png")

        # Resize logo (10% of image width)
        logo_width = int(img.width * 0.1)
        logo_height = int(logo.height * (logo_width / logo.width))
        logo = logo.resize((logo_width, logo_height))

        # Position in bottom right corner
        position = (
            img.width - logo_width - 50,  # 50px from right edge
            img.height - logo_height - 50  # 50px from bottom
        )

        # Paste logo with transparency
        img.paste(logo, position, logo if logo.mode == 'RGBA' else None)

        # Convert back to bytes
        output = io.BytesIO()
        img.save(output, format='PNG')
        return output.getvalue()
```

#### Pricing

**Google Imagen 3**:
- $0.02 per image (1024x1024)
- $0.04 per image (high quality)

**Super affordable** - 100 images = $2

---

### Option B: DALL-E 3 (OpenAI)

Alternative to Imagen, good quality.

**Pricing**: $0.040 per image (1024x1024)

```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.images.generate(
    model="dall-e-3",
    prompt="Professional KSU Athletics quote graphic...",
    size="1792x1024",
    quality="hd",
    n=1
)

image_url = response.data[0].url
```

---

### Option C: Midjourney (Manual - Best Artistic)

Currently no API, requires Discord bot usage.

**Pricing**: $10/month (Basic)

---

## 3. Logo Overlay System

### Automated Logo Placement

Create `module_vi/logo_overlay.py`:

```python
from PIL import Image, ImageDraw, ImageFont
import io

class LogoOverlaySystem:
    def __init__(self):
        self.ksu_logo_path = "assets/logos/ksu_logo.png"
        self.vystar_logo_path = "assets/logos/vystar_logo.png"

    def add_dual_logos(
        self,
        base_image_bytes: bytes,
        primary_logo: str = "ksu",
        secondary_logo: str = None,
        layout: str = "bottom_corners"
    ):
        """
        Add logos to generated graphic

        Args:
            base_image_bytes: The generated image
            primary_logo: 'ksu', 'vystar', etc.
            secondary_logo: Optional partner logo
            layout: 'bottom_corners', 'bottom_center', 'top_right'
        """

        img = Image.open(io.BytesIO(base_image_bytes))

        # Load logos
        primary = self._load_logo(primary_logo)
        secondary_img = self._load_logo(secondary_logo) if secondary_logo else None

        if layout == "bottom_corners":
            # KSU logo bottom left
            self._place_logo(img, primary, position="bottom_left")

            # Partner logo bottom right
            if secondary_img:
                self._place_logo(img, secondary_img, position="bottom_right")

        elif layout == "bottom_center":
            # Both logos centered at bottom
            logos_combined = self._combine_logos_horizontal([primary, secondary_img])
            self._place_logo(img, logos_combined, position="bottom_center")

        # Convert back to bytes
        output = io.BytesIO()
        img.save(output, format='PNG')
        return output.getvalue()

    def _load_logo(self, logo_name: str):
        """Load logo file"""
        logo_paths = {
            "ksu": self.ksu_logo_path,
            "vystar": self.vystar_logo_path
        }

        path = logo_paths.get(logo_name)
        if not path:
            return None

        return Image.open(path)

    def _place_logo(self, base_img, logo, position: str, padding: int = 50):
        """Place logo on base image at specified position"""

        # Calculate logo size (10% of base image width)
        logo_width = int(base_img.width * 0.1)
        logo_height = int(logo.height * (logo_width / logo.width))
        logo_resized = logo.resize((logo_width, logo_height))

        # Calculate position
        positions = {
            "bottom_left": (padding, base_img.height - logo_height - padding),
            "bottom_right": (base_img.width - logo_width - padding, base_img.height - logo_height - padding),
            "bottom_center": ((base_img.width - logo_width) // 2, base_img.height - logo_height - padding),
            "top_right": (base_img.width - logo_width - padding, padding)
        }

        pos = positions.get(position, positions["bottom_right"])

        # Paste with transparency
        base_img.paste(logo_resized, pos, logo_resized if logo_resized.mode == 'RGBA' else None)
```

---

## 4. Complete Workflow Integration

### End-to-End: Post → Graphic → Video → Publish

Create `workflows/complete_media_workflow.py`:

```python
import asyncio
from module_vi import ImagenGraphicsGenerator, HeyGenIntegration, LogoOverlaySystem

async def create_complete_post_package(
    text_content: str,
    voice_type: str,
    include_graphic: bool = True,
    include_video: bool = False,
    partner_logo: str = None
):
    """
    Generate complete social media package

    Returns:
        - Text post
        - Branded graphic (optional)
        - Avatar video (optional)
        - Publishing URLs
    """

    package = {
        "text": text_content,
        "graphic_url": None,
        "video_url": None
    }

    # Generate branded graphic
    if include_graphic:
        imagen = ImagenGraphicsGenerator()

        # Determine theme based on voice type
        theme = "professional" if voice_type == "professional" else "ksu_athletics"

        # Generate base graphic
        graphic_bytes = imagen.generate_quote_graphic(
            quote=text_content[:200],  # First 200 chars
            theme=theme,
            include_logo=False  # We'll add logos separately
        )

        # Add logos
        logo_system = LogoOverlaySystem()
        final_graphic = logo_system.add_dual_logos(
            base_image_bytes=graphic_bytes,
            primary_logo="ksu",
            secondary_logo=partner_logo,  # e.g., "vystar"
            layout="bottom_corners"
        )

        # Save and get URL
        graphic_url = save_to_storage(final_graphic, "graphic.png")
        package["graphic_url"] = graphic_url

    # Generate avatar video
    if include_video:
        heygen = HeyGenIntegration()

        video_result = heygen.create_video(
            script=text_content,
            avatar_id=os.getenv("MILTON_AVATAR_ID")
        )

        # Wait for video generation (async)
        video_url = await wait_for_video(video_result["video_id"])
        package["video_url"] = video_url

    return package


def save_to_storage(image_bytes, filename):
    """Save image to cloud storage and return URL"""
    # Could use AWS S3, Google Cloud Storage, etc.
    # For now, save locally

    path = f"generated_media/{filename}"
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, 'wb') as f:
        f.write(image_bytes)

    return f"http://localhost:8081/media/{filename}"


async def wait_for_video(video_id):
    """Wait for HeyGen video to finish rendering"""
    heygen = HeyGenIntegration()

    while True:
        status = heygen.check_video_status(video_id)

        if status["status"] == "completed":
            return status["video_url"]

        if status["status"] == "failed":
            raise Exception("Video generation failed")

        await asyncio.sleep(10)  # Check every 10 seconds
```

---

## 5. Dashboard Integration

### Add Media Generation to UI

Update `dashboard/templates/index.html`:

```html
<!-- Add after "Generate Content" button -->
<div class="media-options">
    <label>
        <input type="checkbox" id="includeGraphic" checked>
        Generate Branded Graphic
    </label>

    <label>
        <input type="checkbox" id="includeVideo">
        Generate Avatar Video ($)
    </label>

    <select id="partnerLogo">
        <option value="">No Partner Logo</option>
        <option value="vystar">VyStar Credit Union</option>
        <option value="gamechanger">GameChanger Analytics</option>
    </select>
</div>
```

Update `dashboard/app.py` generate endpoint:

```python
@app.post("/api/generate")
async def generate_content(request: Request):
    data = await request.json()

    voice_type = data.get("voice_type", "personal")
    context = data.get("context", "")
    include_graphic = data.get("include_graphic", False)
    include_video = data.get("include_video", False)
    partner_logo = data.get("partner_logo")

    # Generate text content (existing code)
    # ...

    # NEW: Generate media package
    if include_graphic or include_video:
        from workflows.complete_media_workflow import create_complete_post_package

        package = await create_complete_post_package(
            text_content=content,
            voice_type=voice_type,
            include_graphic=include_graphic,
            include_video=include_video,
            partner_logo=partner_logo
        )

        post["graphic_url"] = package["graphic_url"]
        post["video_url"] = package["video_url"]

    return {"success": True, "post": post}
```

---

## 6. Asset Management

### Store Your Logos

Create folder structure:

```
milton-publicist/
├── assets/
│   ├── logos/
│   │   ├── ksu_logo.png          ← Add KSU logo here
│   │   ├── vystar_logo.png       ← Add VyStar logo
│   │   └── gamechanger_logo.png
│   ├── templates/
│   │   └── quote_template.psd    ← Photoshop templates
│   └── fonts/
│       └── ksu_brand_font.ttf
└── generated_media/               ← Generated graphics/videos
    ├── graphics/
    └── videos/
```

---

## 7. Pricing Summary

| Service | Use Case | Cost |
|---------|----------|------|
| **Google Imagen 3** | AI graphics | $0.02 per image |
| **HeyGen** | Avatar videos | $24/mo (15 min) |
| **D-ID** | Avatar videos (alt) | $5.90/mo (20 min) |
| **DALL-E 3** | AI graphics (alt) | $0.04 per image |
| **Midjourney** | Artistic graphics | $10/mo |

**Recommended Stack**: Imagen 3 + HeyGen = ~$25-30/month

---

## Next Steps

**Want me to implement any of these?**

1. ✅ Google Imagen 3 integration for quote graphics
2. ✅ Logo overlay system
3. ✅ HeyGen avatar video integration
4. ✅ Complete workflow with media generation

Let me know which features to build first!
