"""
Logo Overlay System
Add KSU and partner logos to generated graphics
"""

from __future__ import annotations

import os
from typing import Optional, List, Literal, Tuple
from pathlib import Path
import io

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class LogoOverlaySystem:
    """
    Add logos to generated graphics with automatic positioning and sizing
    """

    def __init__(self, assets_dir: Optional[str] = None):
        """
        Initialize logo overlay system

        Args:
            assets_dir: Directory containing logo files
        """
        if not PIL_AVAILABLE:
            raise ImportError("Pillow not installed. Run: pip install Pillow")

        self.assets_dir = Path(assets_dir or "assets/logos")
        self.assets_dir.mkdir(parents=True, exist_ok=True)

        # Logo file paths
        self.logos = {
            "ksu": self.assets_dir / "ksu_logo.png",
            "vystar": self.assets_dir / "vystar_logo.png",
            "gamechanger": self.assets_dir / "gamechanger_logo.png"
        }

    def add_logos(
        self,
        base_image_bytes: bytes,
        primary_logo: str = "ksu",
        secondary_logo: Optional[str] = None,
        layout: Literal["bottom_corners", "bottom_center", "top_right", "bottom_left_only"] = "bottom_corners",
        logo_size_percent: float = 8.0,
        padding: int = 40
    ) -> bytes:
        """
        Add logos to a generated graphic

        Args:
            base_image_bytes: The base image (from AI generation)
            primary_logo: Primary logo name ("ksu", "vystar", etc.)
            secondary_logo: Optional secondary logo name
            layout: Logo placement layout
            logo_size_percent: Logo size as percentage of image width
            padding: Padding from edges in pixels

        Returns:
            Image bytes with logos added (PNG format)
        """

        # Load base image
        img = Image.open(io.BytesIO(base_image_bytes))

        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Load primary logo
        primary_logo_img = self._load_logo(primary_logo)
        if not primary_logo_img:
            print(f"[WARN] Primary logo '{primary_logo}' not found, skipping")
            return base_image_bytes

        # Load secondary logo if specified
        secondary_logo_img = None
        if secondary_logo:
            secondary_logo_img = self._load_logo(secondary_logo)
            if not secondary_logo_img:
                print(f"[WARN] Secondary logo '{secondary_logo}' not found, skipping")

        # Add logos based on layout
        if layout == "bottom_corners":
            self._add_logo_at_position(
                img, primary_logo_img,
                position="bottom_left",
                size_percent=logo_size_percent,
                padding=padding
            )

            if secondary_logo_img:
                self._add_logo_at_position(
                    img, secondary_logo_img,
                    position="bottom_right",
                    size_percent=logo_size_percent,
                    padding=padding
                )

        elif layout == "bottom_center":
            if secondary_logo_img:
                # Combine both logos horizontally
                combined = self._combine_logos_horizontal(
                    [primary_logo_img, secondary_logo_img],
                    spacing=30
                )
                self._add_logo_at_position(
                    img, combined,
                    position="bottom_center",
                    size_percent=logo_size_percent * 1.5,  # Larger for combined
                    padding=padding
                )
            else:
                self._add_logo_at_position(
                    img, primary_logo_img,
                    position="bottom_center",
                    size_percent=logo_size_percent,
                    padding=padding
                )

        elif layout == "top_right":
            self._add_logo_at_position(
                img, primary_logo_img,
                position="top_right",
                size_percent=logo_size_percent,
                padding=padding
            )

        elif layout == "bottom_left_only":
            self._add_logo_at_position(
                img, primary_logo_img,
                position="bottom_left",
                size_percent=logo_size_percent,
                padding=padding
            )

        # Convert back to bytes
        output = io.BytesIO()
        img.save(output, format='PNG')
        return output.getvalue()

    def _load_logo(self, logo_name: str) -> Optional[Image.Image]:
        """Load logo file"""
        logo_path = self.logos.get(logo_name)

        if not logo_path or not logo_path.exists():
            return None

        try:
            logo = Image.open(logo_path)
            # Ensure RGBA for transparency
            if logo.mode != 'RGBA':
                logo = logo.convert('RGBA')
            return logo
        except Exception as e:
            print(f"[ERROR] Failed to load logo {logo_name}: {e}")
            return None

    def _add_logo_at_position(
        self,
        base_img: Image.Image,
        logo: Image.Image,
        position: str,
        size_percent: float,
        padding: int
    ):
        """Add logo to base image at specified position"""

        # Calculate logo size
        logo_width = int(base_img.width * (size_percent / 100))
        logo_height = int(logo.height * (logo_width / logo.width))

        # Resize logo
        logo_resized = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

        # Calculate position
        positions = {
            "bottom_left": (padding, base_img.height - logo_height - padding),
            "bottom_right": (base_img.width - logo_width - padding, base_img.height - logo_height - padding),
            "bottom_center": ((base_img.width - logo_width) // 2, base_img.height - logo_height - padding),
            "top_right": (base_img.width - logo_width - padding, padding),
            "top_left": (padding, padding),
            "center": ((base_img.width - logo_width) // 2, (base_img.height - logo_height) // 2)
        }

        pos = positions.get(position, positions["bottom_right"])

        # Paste logo with alpha transparency
        base_img.paste(logo_resized, pos, logo_resized)

    def _combine_logos_horizontal(
        self,
        logos: List[Image.Image],
        spacing: int = 20
    ) -> Image.Image:
        """Combine multiple logos horizontally"""

        # Calculate combined dimensions
        total_width = sum(logo.width for logo in logos) + spacing * (len(logos) - 1)
        max_height = max(logo.height for logo in logos)

        # Create new image
        combined = Image.new('RGBA', (total_width, max_height), (0, 0, 0, 0))

        # Paste logos
        x_offset = 0
        for logo in logos:
            # Center vertically
            y_offset = (max_height - logo.height) // 2
            combined.paste(logo, (x_offset, y_offset), logo)
            x_offset += logo.width + spacing

        return combined

    def create_placeholder_logo(self, logo_name: str, text: str):
        """
        Create a placeholder logo if actual logo isn't available

        Args:
            logo_name: Name to save as
            text: Text to display in placeholder
        """
        # Create a simple placeholder
        img = Image.new('RGBA', (400, 200), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw background rectangle
        draw.rectangle([(10, 10), (390, 190)], fill=(253, 185, 19, 255), outline=(0, 0, 0, 255), width=3)

        # Try to add text
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()

        # Calculate text position (centered)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = (400 - text_width) // 2
        text_y = (200 - text_height) // 2

        draw.text((text_x, text_y), text, fill=(0, 0, 0, 255), font=font)

        # Save
        logo_path = self.assets_dir / f"{logo_name}_logo.png"
        img.save(logo_path)

        print(f"[INFO] Created placeholder logo: {logo_path}")

        return logo_path


# Example usage
def main():
    """Example usage of LogoOverlaySystem"""
    print("="*70)
    print("LOGO OVERLAY SYSTEM - DEMO")
    print("="*70)
    print()

    system = LogoOverlaySystem()

    # Create placeholder logos if they don't exist
    print("[INFO] Checking for logo files...")

    if not (system.assets_dir / "ksu_logo.png").exists():
        print("[INFO] Creating KSU placeholder logo...")
        system.create_placeholder_logo("ksu", "KSU")

    if not (system.assets_dir / "vystar_logo.png").exists():
        print("[INFO] Creating VyStar placeholder logo...")
        system.create_placeholder_logo("vystar", "VyStar")

    if not (system.assets_dir / "gamechanger_logo.png").exists():
        print("[INFO] Creating GameChanger placeholder logo...")
        system.create_placeholder_logo("gamechanger", "GameChanger")

    print()

    # Example: Add logos to an existing image
    print("[INFO] Example: Add logos to a graphic")
    print()
    print("Usage:")
    print("""
    # Load your generated graphic
    with open("generated_graphic.png", "rb") as f:
        base_image_bytes = f.read()

    # Add KSU logo (bottom left) and VyStar logo (bottom right)
    final_image_bytes = system.add_logos(
        base_image_bytes=base_image_bytes,
        primary_logo="ksu",
        secondary_logo="vystar",
        layout="bottom_corners"
    )

    # Save final image
    with open("graphic_with_logos.png", "wb") as f:
        f.write(final_image_bytes)
    """)

    print()
    print("="*70)
    print("Logo system ready!")
    print(f"Add your actual logo files to: {system.assets_dir}")
    print("Supported logos: KSU, VyStar, GameChanger")
    print("="*70)


if __name__ == "__main__":
    main()
