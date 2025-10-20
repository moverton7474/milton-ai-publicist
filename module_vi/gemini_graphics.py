"""
AI Graphics Generation using Google Gemini 2.0 Flash + Pollinations.ai
FREE image generation for social media posts
"""

import os
import io
import json
import requests
from typing import Optional, Dict, Literal
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote

# Load environment variables
load_dotenv()


class GeminiGraphicsGenerator:
    """
    Generate AI graphics using Google Gemini 2.0 Flash (prompt generation)
    + Pollinations.ai (free image generation)

    Benefits:
    - FREE unlimited image generation
    - No billing setup required
    - High-quality images
    - Intelligent prompt generation with Gemini
    """

    def __init__(self, google_ai_api_key: Optional[str] = None):
        """
        Initialize graphics generator

        Args:
            google_ai_api_key: Google AI Studio API key (free)
        """
        self.google_ai_api_key = google_ai_api_key or os.getenv("GOOGLE_AI_API_KEY")

        if not self.google_ai_api_key:
            raise ValueError(
                "Google AI API key required. Get free key at: https://aistudio.google.com/apikey\n"
                "Set GOOGLE_AI_API_KEY in .env file"
            )

        self.gemini_endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        print("[INFO] Initialized Google Gemini 2.0 Flash + Pollinations.ai (FREE)")

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

        # Step 1: Use Gemini to generate intelligent image prompt
        print(f"[INFO] Generating optimized prompt with Gemini for theme: {theme}")
        image_prompt = self._generate_prompt_with_gemini(quote, theme)

        # Step 2: Generate image with Pollinations.ai (FREE!)
        print(f"[INFO] Generating {size} image with Pollinations.ai...")
        image_bytes = self._generate_with_pollinations(image_prompt, size, quality)

        return image_bytes

    def _generate_prompt_with_gemini(self, quote: str, theme: str) -> str:
        """Use Gemini 2.0 Flash to generate optimized image prompt"""

        # Build theme-specific instructions
        theme_instructions = self._get_theme_instructions(theme, quote)

        gemini_prompt = f"""You are a professional social media graphics designer specializing in athletic department branding.

Generate a detailed, specific image generation prompt for creating a LinkedIn/Twitter social media graphic.

REQUIREMENTS:
{theme_instructions}

The graphic should display this quote/message:
"{quote}"

Generate a single, detailed prompt that describes the visual design in specific detail. Include:
- Exact colors (hex codes)
- Layout and composition
- Typography style
- Background elements
- Brand elements (KSU)
- Overall mood and aesthetic

Return ONLY the image generation prompt text, no JSON, no explanation, just the prompt."""

        # Call Gemini API
        try:
            response = requests.post(
                f"{self.gemini_endpoint}?key={self.google_ai_api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{
                        "parts": [{"text": gemini_prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.9,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 512,
                    }
                },
                timeout=30
            )

            if not response.ok:
                print(f"[WARN] Gemini API error: {response.status_code}")
                return self._get_fallback_prompt(quote, theme)

            data = response.json()
            generated_prompt = data["candidates"][0]["content"]["parts"][0]["text"].strip()

            print(f"[OK] Gemini generated optimized prompt ({len(generated_prompt)} chars)")
            return generated_prompt

        except Exception as e:
            print(f"[WARN] Gemini error: {e}, using fallback prompt")
            return self._get_fallback_prompt(quote, theme)

    def _get_theme_instructions(self, theme: str, quote: str) -> str:
        """Get theme-specific branding instructions"""

        if theme == "ksu_athletics":
            return """KENNESAW STATE UNIVERSITY ATHLETICS BRANDING:
- Primary Color: Rich Gold (#FFB81C, #FDB913)
- Secondary Color: Black (#000000)
- Team: Kennesaw State Owls or KSU
- Include "KSU" text prominently
- Athletic, bold, energetic aesthetic
- Modern sports design
- Professional yet dynamic
- Horizontal 16:9 ratio for social media"""

        elif theme == "professional":
            return """PROFESSIONAL STATEMENT BRANDING:
- KSU Colors: Gold (#FFB81C) and Black (#000000)
- Clean, authoritative design
- Professional business aesthetic
- Modern corporate style
- Bold typography for readability
- Gradient backgrounds (gold to black)
- Executive presence
- Horizontal 16:9 ratio for social media"""

        elif theme == "celebration":
            return """CELEBRATION/ACHIEVEMENT BRANDING:
- KSU Colors: Vibrant Gold (#FFB81C) and Black (#000000)
- Energetic, exciting design
- Victory and achievement theme
- Bold, dynamic composition
- Celebratory atmosphere
- High-energy sports aesthetics
- Motivational and inspiring
- Horizontal 16:9 ratio for social media"""

        else:
            return """KSU ATHLETICS BRANDING:
- Colors: Gold (#FFB81C) and Black (#000000)
- Bold, professional design
- Modern athletic aesthetic
- Horizontal 16:9 ratio"""

    def _get_fallback_prompt(self, quote: str, theme: str) -> str:
        """Fallback prompt if Gemini fails"""

        if theme == "ksu_athletics":
            return f"""Modern athletic social media graphic for Kennesaw State University Athletics. Bold design with rich gold (#FFB81C) and black (#000000) colors. Large, readable typography displaying: "{quote}". Include "KSU" branding prominently. Dynamic sports energy, professional composition, horizontal 16:9 format, high quality, photorealistic rendering."""

        elif theme == "professional":
            return f"""Professional LinkedIn post graphic for Kennesaw State University. Clean, authoritative design with gold (#FFB81C) to black (#000000) gradient background. Bold sans-serif typography displaying: "{quote}". KSU branding subtle but present. Executive aesthetic, modern corporate style, horizontal 16:9 format, 4K quality."""

        else:
            return f"""Celebratory sports graphic for KSU Athletics. Vibrant gold (#FFB81C) and black (#000000) colors. Energetic design with bold typography: "{quote}". Achievement and victory theme, dynamic composition, horizontal 16:9 format, professional quality."""

    def _generate_with_pollinations(
        self,
        prompt: str,
        size: Literal["square", "wide", "story"],
        quality: Literal["standard", "hd"]
    ) -> bytes:
        """Generate image using Pollinations.ai (FREE!)"""

        # Determine dimensions
        if size == "square":
            width, height = 1024, 1024
        elif size == "wide":
            width, height = 1792, 1024
        elif size == "story":
            width, height = 1024, 1792
        else:
            width, height = 1792, 1024

        # Simplify prompt to avoid URL length issues (Pollinations.ai has limits)
        # Keep it under 500 chars
        if len(prompt) > 400:
            prompt = prompt[:400] + "..."

        # Enhance prompt for better quality
        enhanced_prompt = f"{prompt}. Professional social media graphic, high quality, modern design"

        # Pollinations.ai URL format (simpler encoding)
        # https://image.pollinations.ai/prompt/{prompt}?width=X&height=Y&nologo=true
        import time
        seed = int(time.time())  # Dynamic seed for variety

        image_url = f"https://image.pollinations.ai/prompt/{quote(enhanced_prompt)}?width={width}&height={height}&nologo=true&seed={seed}"

        print(f"[INFO] Pollinations.ai URL generated (FREE)")
        print(f"[DEBUG] URL length: {len(image_url)} chars")

        # Download the generated image
        try:
            response = requests.get(image_url, timeout=90)

            if response.ok:
                print(f"[OK] Image generated successfully ({len(response.content)} bytes)")
                return response.content
            else:
                print(f"[ERROR] Pollinations.ai returned status {response.status_code}")
                print(f"[DEBUG] Response: {response.text[:200]}")
                raise Exception(f"Pollinations.ai returned status {response.status_code}")

        except Exception as e:
            print(f"[ERROR] Failed to generate image: {e}")
            raise


    def save_image(self, image_bytes: bytes, filename: str, output_dir: str = "generated_media/graphics") -> str:
        """Save image to file"""

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        filepath = output_path / filename
        filepath.write_bytes(image_bytes)

        print(f"[OK] Saved to: {filepath}")
        return str(filepath)


# Demo/Test
if __name__ == "__main__":
    print("="*70)
    print("GOOGLE GEMINI + POLLINATIONS.AI GRAPHICS - DEMO")
    print("="*70)
    print()

    try:
        # Initialize generator
        generator = GeminiGraphicsGenerator()

        # Test 1: KSU Athletics quote
        print("[INFO] Generating KSU Athletics quote graphic...")
        quote1 = "We want to thank our incredible partners who make it all possible for our student-athletes. Let's Go Owls!"
        graphic1 = generator.generate_quote_graphic(
            quote=quote1,
            theme="ksu_athletics",
            size="wide",
            quality="hd"
        )
        filename1 = generator.save_image(graphic1, "ksu_gemini_example.png")
        print(f"[OK] Graphic saved to: {filename1}")
        print()

        # Test 2: Professional statement
        print("[INFO] Generating professional leadership graphic...")
        quote2 = "Leadership in college athletics means putting student-athletes first and building champions both on the field and in the classroom."
        graphic2 = generator.generate_quote_graphic(
            quote=quote2,
            theme="professional",
            size="wide",
            quality="hd"
        )
        filename2 = generator.save_image(graphic2, "professional_gemini_example.png")
        print(f"[OK] Graphic saved to: {filename2}")
        print()

        print("="*70)
        print("Graphics generated successfully!")
        print("Next: Add KSU/partner logos with LogoOverlaySystem")
        print("="*70)

    except ValueError as e:
        print(f"[ERROR] {e}")
        print()
        print("Quick Setup:")
        print("1. Get free API key: https://aistudio.google.com/apikey")
        print("2. Add to .env: GOOGLE_AI_API_KEY=your_key_here")
        print("3. Run again!")
    except Exception as e:
        print(f"[ERROR] {e}")
