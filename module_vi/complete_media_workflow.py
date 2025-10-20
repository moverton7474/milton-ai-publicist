"""
Complete Media Workflow
Generate text → Create graphic → Add logos → Create avatar video → Publish
"""

import asyncio
import os
import sys
from typing import Optional, Dict, List
from pathlib import Path

# Add parent directory to path for standalone execution
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from module_vi.gemini_graphics import GeminiGraphicsGenerator
    from module_vi.imagen_graphics import ImagenGraphicsGenerator
    from module_vi.logo_overlay import LogoOverlaySystem
    from module_vi.heygen_videos import HeyGenVideoGenerator
except ImportError:
    from .gemini_graphics import GeminiGraphicsGenerator
    from .imagen_graphics import ImagenGraphicsGenerator
    from .logo_overlay import LogoOverlaySystem
    from .heygen_videos import HeyGenVideoGenerator


class CompleteMediaWorkflow:
    """
    One-stop workflow for creating complete social media packages
    """

    def __init__(self, prefer_gemini: bool = True):
        """
        Initialize all media generation systems

        Args:
            prefer_gemini: Use Gemini + Pollinations.ai (FREE) instead of DALL-E (default: True)
        """

        # Initialize graphics generator (try Gemini first, fallback to DALL-E/Imagen)
        try:
            if prefer_gemini:
                # Try Gemini + Pollinations.ai (FREE!)
                self.graphics_generator = GeminiGraphicsGenerator()
                self.graphics_available = True
                print("[INFO] Using Google Gemini + Pollinations.ai (FREE)")
            else:
                # Fallback to DALL-E/Imagen (paid)
                self.graphics_generator = ImagenGraphicsGenerator(provider="auto")
                self.graphics_available = True
                print("[INFO] Using DALL-E/Imagen (paid)")
        except Exception as e:
            # If Gemini fails, try DALL-E/Imagen as fallback
            try:
                self.graphics_generator = ImagenGraphicsGenerator(provider="auto")
                self.graphics_available = True
                print("[INFO] Gemini unavailable, using DALL-E/Imagen fallback")
            except Exception as e2:
                print(f"[WARN] Graphics generation not available: {e2}")
                self.graphics_available = False

        # Initialize logo overlay system
        self.logo_system = LogoOverlaySystem()

        # Initialize video generator
        try:
            self.video_generator = HeyGenVideoGenerator()
            self.video_available = True
        except Exception as e:
            print(f"[WARN] Video generation not available: {e}")
            self.video_available = False

        # Output directory
        self.output_dir = Path("generated_media")
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "graphics").mkdir(exist_ok=True)
        (self.output_dir / "videos").mkdir(exist_ok=True)

    def create_post_package(
        self,
        text_content: str,
        voice_type: str = "personal",
        include_graphic: bool = True,
        include_video: bool = False,
        partner_logo: Optional[str] = None,
        graphic_theme: str = None,
        video_background: str = "#000000"
    ) -> Dict:
        """
        Create complete social media package

        Args:
            text_content: The post text
            voice_type: "personal" or "professional"
            include_graphic: Generate branded graphic
            include_video: Generate avatar video
            partner_logo: Optional partner logo ("vystar", "gamechanger", etc.)
            graphic_theme: Visual theme for graphic
            video_background: Background color for video

        Returns:
            Dict with text, graphic_path, video_path, and metadata
        """

        package = {
            "text": text_content,
            "graphic_path": None,
            "video_path": None,
            "graphic_url": None,
            "video_url": None,
            "metadata": {
                "voice_type": voice_type,
                "word_count": len(text_content.split()),
                "has_graphic": False,
                "has_video": False,
                "partner": partner_logo
            }
        }

        # Determine graphic theme based on voice type
        if not graphic_theme:
            graphic_theme = "professional" if voice_type == "professional" else "ksu_athletics"

        # Generate graphic
        if include_graphic and self.graphics_available:
            try:
                print("[INFO] Generating AI graphic...")

                # Extract quote (first 200 chars or first sentence)
                quote = text_content[:200] if len(text_content) > 200 else text_content

                # Generate base graphic
                graphic_bytes = self.graphics_generator.generate_quote_graphic(
                    quote=quote,
                    theme=graphic_theme,
                    size="wide",
                    quality="hd"
                )

                # Add logos
                print("[INFO] Adding logos...")
                final_graphic_bytes = self.logo_system.add_logos(
                    base_image_bytes=graphic_bytes,
                    primary_logo="ksu",
                    secondary_logo=partner_logo,
                    layout="bottom_corners" if partner_logo else "bottom_left_only"
                )

                # Save graphic
                filename = f"graphic_{voice_type}_{self._get_timestamp()}.png"
                graphic_path = self.output_dir / "graphics" / filename

                with open(graphic_path, 'wb') as f:
                    f.write(final_graphic_bytes)

                package["graphic_path"] = str(graphic_path)
                package["graphic_url"] = f"/media/graphics/{filename}"
                package["metadata"]["has_graphic"] = True

                print(f"[OK] Graphic saved: {graphic_path}")

            except Exception as e:
                print(f"[ERROR] Graphic generation failed: {e}")

        # Generate video
        if include_video and self.video_available:
            try:
                print("[INFO] Generating avatar video...")
                print("(This may take 1-3 minutes)")

                # Create video
                result = self.video_generator.create_video(
                    script=text_content,
                    background_color=video_background
                )

                # Wait for completion
                final_status = self.video_generator.wait_for_video(
                    result["video_id"],
                    max_wait_seconds=300
                )

                # Download video
                filename = f"video_{voice_type}_{self._get_timestamp()}.mp4"
                video_path = self.output_dir / "videos" / filename

                self.video_generator.download_video(
                    final_status["video_url"],
                    str(video_path)
                )

                package["video_path"] = str(video_path)
                package["video_url"] = f"/media/videos/{filename}"
                package["metadata"]["has_video"] = True
                package["metadata"]["video_duration"] = final_status.get("duration")

                print(f"[OK] Video saved: {video_path}")

            except Exception as e:
                print(f"[ERROR] Video generation failed: {e}")

        return package

    def _get_timestamp(self) -> str:
        """Get timestamp for filenames"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")


# Example usage
async def main():
    """Example complete workflow"""
    print("="*70)
    print("COMPLETE MEDIA WORKFLOW - DEMO")
    print("="*70)
    print()

    workflow = CompleteMediaWorkflow()

    # Example 1: Text + Graphic (no video)
    print("[EXAMPLE 1] Generate post with graphic")
    print()

    text1 = """We want to thank VyStar Credit Union for their incredible partnership
with Kennesaw State University Athletics! Their support helps us create
even more memorable experiences for our Owl community. Let's Go Owls!"""

    package1 = workflow.create_post_package(
        text_content=text1,
        voice_type="personal",
        include_graphic=True,
        include_video=False,
        partner_logo="vystar"
    )

    print()
    print("Package created:")
    print(f"  Text: {len(package1['text'])} chars")
    print(f"  Graphic: {package1['graphic_path'] or 'None'}")
    print(f"  Video: {package1['video_path'] or 'None'}")
    print()
    print("="*70)
    print()

    # Example 2: Complete package (text + graphic + video)
    if workflow.video_available:
        print("[EXAMPLE 2] Generate complete package (text + graphic + video)")
        print()

        text2 = """Excited to announce our partnership with GameChanger Analytics!
Their AI-powered fan engagement tools will transform how we connect
with our Owl community. Let's Go Owls!"""

        package2 = workflow.create_post_package(
            text_content=text2,
            voice_type="personal",
            include_graphic=True,
            include_video=True,
            partner_logo="gamechanger"
        )

        print()
        print("Complete package created:")
        print(f"  Text: {len(package2['text'])} chars")
        print(f"  Graphic: {package2['graphic_path']}")
        print(f"  Video: {package2['video_path']}")
        print()

    print("="*70)
    print("Workflow complete!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
