"""
AI Graphics Generation using Google Imagen 3 or DALL-E 3
Generate branded quote graphics for social media
"""

import os
import base64
import io
from typing import Optional, Dict, Literal
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from google.cloud import aiplatform
    from google.oauth2 import service_account
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class ImagenGraphicsGenerator:
    """
    Generate AI graphics using Google Imagen 3 or DALL-E 3
    Falls back to DALL-E if Google Cloud isn't configured
    """

    def __init__(
        self,
        provider: Literal["google", "openai", "auto"] = "auto",
        google_project_id: Optional[str] = None,
        google_credentials_path: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize graphics generator

        Args:
            provider: "google" (Imagen 3), "openai" (DALL-E 3), or "auto" (try Google, fall back to OpenAI)
            google_project_id: Google Cloud project ID
            google_credentials_path: Path to Google Cloud credentials JSON
            openai_api_key: OpenAI API key
        """
        self.provider = provider
        self.google_project_id = google_project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.google_credentials_path = google_credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        # Determine which provider to use
        if provider == "auto":
            if GOOGLE_AVAILABLE and self.google_project_id and self.google_credentials_path:
                self.active_provider = "google"
            elif OPENAI_AVAILABLE and self.openai_api_key:
                self.active_provider = "openai"
            else:
                raise ValueError("No AI graphics provider available. Install openai or google-cloud-aiplatform and set API keys.")
        else:
            self.active_provider = provider

        # Initialize the active provider
        if self.active_provider == "google":
            self._init_google()
        elif self.active_provider == "openai":
            self._init_openai()

    def _init_google(self):
        """Initialize Google Imagen 3"""
        if not GOOGLE_AVAILABLE:
            raise ImportError("google-cloud-aiplatform not installed. Run: pip install google-cloud-aiplatform")

        if not self.google_credentials_path or not Path(self.google_credentials_path).exists():
            raise ValueError(f"Google credentials not found at: {self.google_credentials_path}")

        credentials = service_account.Credentials.from_service_account_file(
            self.google_credentials_path
        )

        aiplatform.init(
            project=self.google_project_id,
            location="us-central1",
            credentials=credentials
        )

        print(f"[INFO] Initialized Google Imagen 3 (Project: {self.google_project_id})")

    def _init_openai(self):
        """Initialize OpenAI DALL-E 3"""
        if not OPENAI_AVAILABLE:
            raise ImportError("openai not installed. Run: pip install openai")

        if not self.openai_api_key:
            raise ValueError("OpenAI API key not set. Set OPENAI_API_KEY environment variable.")

        self.openai_client = OpenAI(api_key=self.openai_api_key)
        print(f"[INFO] Initialized OpenAI DALL-E 3")

    def generate_quote_graphic(
        self,
        quote: str,
        theme: Literal["ksu_athletics", "professional", "celebration"] = "ksu_athletics",
        size: Literal["square", "wide", "story"] = "wide",
        quality: Literal["standard", "hd"] = "hd"
    ) -> bytes:
        """
        Generate a branded quote graphic

        Args:
            quote: The quote text to display
            theme: Visual theme
            size: Image size (square=1024x1024, wide=1792x1024, story=1024x1792)
            quality: Image quality

        Returns:
            Image bytes (PNG format)
        """

        # Build prompt based on theme
        prompt = self._build_prompt(quote, theme)

        # Generate image using active provider
        if self.active_provider == "google":
            return self._generate_with_google(prompt, size, quality)
        elif self.active_provider == "openai":
            return self._generate_with_openai(prompt, size, quality)

    def _build_prompt(self, quote: str, theme: str) -> str:
        """Build AI prompt for graphic generation"""

        prompts = {
            "ksu_athletics": f"""
Professional athletic department social media graphic for LinkedIn/Twitter.

Design Requirements:
- Kennesaw State University brand colors: Gold (#FDB913) and Black (#000000)
- Modern, clean, bold typography
- Athletic energy and professionalism
- Horizontal 16:9 ratio optimized for social media

Text to Display (centered, large, readable):
"{quote}"

Visual Style:
- Bold sans-serif font for maximum readability
- Gradient background from gold to black
- Subtle owl motif (KSU mascot) as watermark
- Professional collegiate athletics aesthetic
- High contrast for mobile viewing
- NO LOGOS (will be added separately)

Layout: Text should be the focal point, large enough to read on mobile devices.
""",

            "professional": f"""
Executive leadership quote graphic for LinkedIn.

Design Requirements:
- Sophisticated, minimalist design
- Navy blue (#002147), gold (#FDB913) accents, white
- Modern serif font for the quote
- Corporate/professional aesthetic

Text to Display:
"{quote}"

Visual Style:
- Clean, uncluttered layout
- White or light gray background
- Dark text for maximum readability
- Subtle gold accent line or element
- Forbes/Harvard Business Review aesthetic
- Professional business look

Layout: Quote centered, attribution space at bottom (will be added separately).
""",

            "celebration": f"""
Vibrant celebration announcement graphic for social media.

Design Requirements:
- Energetic, bold, exciting
- Gold and black with dynamic gradients
- Modern bold typography
- Celebratory feeling

Text to Display:
"{quote}"

Visual Style:
- Bright gold background with black text OR black background with gold text
- Confetti, stars, or celebratory geometric shapes
- High energy ESPN/Athletic Department social media style
- Bold, impact font
- Exciting and shareable

Layout: Text fills most of the space, maximum visual impact.
"""
        }

        return prompts.get(theme, prompts["ksu_athletics"])

    def _generate_with_google(self, prompt: str, size: str, quality: str) -> bytes:
        """Generate image using Google Imagen 3"""

        # Map size to aspect ratio
        aspect_ratios = {
            "square": "1:1",
            "wide": "16:9",
            "story": "9:16"
        }

        endpoint = aiplatform.Endpoint(
            endpoint_name=f"projects/{self.google_project_id}/locations/us-central1/publishers/google/models/imagen-3.0-generate-001"
        )

        instances = [{
            "prompt": prompt,
            "aspectRatio": aspect_ratios[size],
            "numberOfImages": 1,
            "outputOptions": {
                "mimeType": "image/png"
            }
        }]

        response = endpoint.predict(instances=instances)

        # Decode base64 image
        image_data = response.predictions[0]["bytesBase64Encoded"]
        image_bytes = base64.b64decode(image_data)

        return image_bytes

    def _generate_with_openai(self, prompt: str, size: str, quality: str) -> bytes:
        """Generate image using OpenAI DALL-E 3"""

        # Map size to DALL-E dimensions
        sizes = {
            "square": "1024x1024",
            "wide": "1792x1024",
            "story": "1024x1792"
        }

        response = self.openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=sizes[size],
            quality=quality,
            n=1
        )

        # Download the image
        image_url = response.data[0].url
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        return image_response.content

    def save_image(self, image_bytes: bytes, filename: str, output_dir: str = "generated_media/graphics") -> str:
        """
        Save generated image to file

        Args:
            image_bytes: Image data
            filename: Output filename
            output_dir: Output directory

        Returns:
            Path to saved file
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        filepath = output_path / filename
        with open(filepath, 'wb') as f:
            f.write(image_bytes)

        return str(filepath)


# Example usage
def main():
    """Example usage of ImagenGraphicsGenerator"""
    print("="*70)
    print("AI GRAPHICS GENERATION - DEMO")
    print("="*70)
    print()

    # Initialize generator (auto-detects available provider)
    try:
        generator = ImagenGraphicsGenerator(provider="auto")
    except ValueError as e:
        print(f"[ERROR] {e}")
        print()
        print("To use this feature:")
        print("  Option 1 (OpenAI DALL-E 3): pip install openai && set OPENAI_API_KEY")
        print("  Option 2 (Google Imagen 3): pip install google-cloud-aiplatform && configure Google Cloud")
        return

    # Example 1: KSU Athletics theme
    print("[INFO] Generating KSU Athletics quote graphic...")

    quote = "We want to thank VyStar Credit Union for their incredible partnership with Kennesaw State University Athletics! Let's Go Owls!"

    try:
        image_bytes = generator.generate_quote_graphic(
            quote=quote,
            theme="ksu_athletics",
            size="wide",
            quality="hd"
        )

        # Save image
        filepath = generator.save_image(image_bytes, "ksu_quote_example.png")
        print(f"[OK] Graphic saved to: {filepath}")
        print()

    except Exception as e:
        print(f"[ERROR] {e}")
        print()

    # Example 2: Professional theme
    print("[INFO] Generating professional leadership graphic...")

    quote_professional = "Innovation in college sports isn't about having the biggest budget. It's about being willing to experiment, iterate, and lead."

    try:
        image_bytes = generator.generate_quote_graphic(
            quote=quote_professional,
            theme="professional",
            size="square",
            quality="hd"
        )

        filepath = generator.save_image(image_bytes, "professional_quote_example.png")
        print(f"[OK] Graphic saved to: {filepath}")
        print()

    except Exception as e:
        print(f"[ERROR] {e}")
        print()

    print("="*70)
    print("Graphics generated successfully!")
    print("Next: Add KSU/partner logos with LogoOverlaySystem")
    print("="*70)


if __name__ == "__main__":
    main()
