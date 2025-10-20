"""
HeyGen Avatar Video Generation
Create photorealistic avatar videos from text scripts
"""

import os
import time
import requests
from typing import Optional, Dict, Literal
from datetime import datetime


class HeyGenVideoGenerator:
    """
    Generate avatar videos using HeyGen API
    Supports custom avatars and voice cloning
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize HeyGen video generator

        Args:
            api_key: HeyGen API key (or set HEYGEN_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("HEYGEN_API_KEY")

        if not self.api_key:
            raise ValueError("HeyGen API key required. Set HEYGEN_API_KEY environment variable or pass api_key parameter.")

        self.base_url = "https://api.heygen.com/v2"
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def create_video(
        self,
        script: str,
        avatar_id: Optional[str] = None,
        voice_id: Optional[str] = None,
        background_color: str = "#0066CC",
        video_title: Optional[str] = None
    ) -> Dict:
        """
        Create an avatar video

        Args:
            script: Text script for avatar to speak
            avatar_id: Custom avatar ID (or use default)
            voice_id: Custom voice ID (or use default)
            background_color: Background color (hex code)
            video_title: Optional video title

        Returns:
            Dict with video_id and status
        """

        # Use default avatar and voice if not specified
        if not avatar_id:
            avatar_id = os.getenv("MILTON_AVATAR_ID", "default_avatar")

        if not voice_id:
            voice_id = os.getenv("MILTON_VOICE_ID", "default_voice")

        # Build request payload
        payload = {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": script,
                    "voice_id": voice_id
                },
                "background": {
                    "type": "color",
                    "value": background_color
                }
            }],
            "dimension": {
                "width": 1920,
                "height": 1080
            },
            "title": video_title or f"Milton Video - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }

        # Make API request
        response = requests.post(
            f"{self.base_url}/video/generate",
            headers=self.headers,
            json=payload
        )

        response.raise_for_status()
        result = response.json()

        return {
            "video_id": result.get("video_id"),
            "status": "generating",
            "message": "Video generation started"
        }

    def check_video_status(self, video_id: str) -> Dict:
        """
        Check video generation status

        Args:
            video_id: Video ID from create_video()

        Returns:
            Dict with status and video_url (if completed)
        """

        response = requests.get(
            f"{self.base_url}/video/{video_id}",
            headers=self.headers
        )

        response.raise_for_status()
        result = response.json()

        status = result.get("status")  # "pending", "processing", "completed", "failed"

        return {
            "video_id": video_id,
            "status": status,
            "video_url": result.get("video_url") if status == "completed" else None,
            "thumbnail_url": result.get("thumbnail_url"),
            "duration": result.get("duration"),
            "error": result.get("error") if status == "failed" else None
        }

    def wait_for_video(
        self,
        video_id: str,
        max_wait_seconds: int = 300,
        check_interval: int = 10
    ) -> Dict:
        """
        Wait for video to finish generating

        Args:
            video_id: Video ID from create_video()
            max_wait_seconds: Maximum time to wait (default: 5 minutes)
            check_interval: Seconds between status checks

        Returns:
            Dict with final status and video_url

        Raises:
            TimeoutError: If video doesn't complete within max_wait_seconds
            Exception: If video generation fails
        """

        start_time = time.time()

        while True:
            # Check status
            status_info = self.check_video_status(video_id)

            if status_info["status"] == "completed":
                return status_info

            if status_info["status"] == "failed":
                error = status_info.get("error", "Unknown error")
                raise Exception(f"Video generation failed: {error}")

            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > max_wait_seconds:
                raise TimeoutError(f"Video generation timed out after {max_wait_seconds} seconds")

            # Wait before next check
            print(f"[INFO] Video status: {status_info['status']}... (waited {int(elapsed)}s)")
            time.sleep(check_interval)

    def list_avatars(self) -> Dict:
        """
        List available avatars

        Returns:
            Dict with avatar list
        """

        response = requests.get(
            f"{self.base_url}/avatars",
            headers=self.headers
        )

        response.raise_for_status()
        return response.json()

    def list_voices(self) -> Dict:
        """
        List available voices

        Returns:
            Dict with voice list
        """

        response = requests.get(
            f"{self.base_url}/voices",
            headers=self.headers
        )

        response.raise_for_status()
        return response.json()

    def download_video(self, video_url: str, output_path: str):
        """
        Download completed video

        Args:
            video_url: URL from check_video_status()
            output_path: Path to save video file
        """

        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"[OK] Video downloaded to: {output_path}")


# Example usage
def main():
    """Example usage of HeyGenVideoGenerator"""
    print("="*70)
    print("HEYGEN AVATAR VIDEO GENERATION - DEMO")
    print("="*70)
    print()

    # Check if API key is set
    if not os.getenv("HEYGEN_API_KEY"):
        print("[INFO] HeyGen API key not set")
        print()
        print("To use HeyGen avatar videos:")
        print("1. Sign up at https://www.heygen.com")
        print("2. Get your API key from dashboard")
        print("3. Set environment variable:")
        print("   export HEYGEN_API_KEY='your_api_key_here'")
        print()
        print("Pricing:")
        print("  - Free tier: 1 minute/month")
        print("  - Creator: $24/month for 15 minutes")
        print("  - Business: $72/month for 60 minutes")
        print()
        print("="*70)
        return

    try:
        generator = HeyGenVideoGenerator()

        # Example script
        script = """
        We want to thank VyStar Credit Union for their incredible partnership
        with Kennesaw State University Athletics!

        Their support will help us create even more memorable experiences for
        our Owl community, student-athletes, and fans.

        Let's Go Owls!
        """

        print("[INFO] Creating avatar video...")
        print(f"Script: {script[:100]}...")
        print()

        # Create video
        result = generator.create_video(
            script=script,
            background_color="#000000",  # Black background
            video_title="VyStar Partnership Announcement"
        )

        video_id = result["video_id"]
        print(f"[OK] Video generation started")
        print(f"Video ID: {video_id}")
        print()

        # Wait for completion
        print("[INFO] Waiting for video to complete...")
        print("(This usually takes 1-3 minutes)")
        print()

        final_status = generator.wait_for_video(video_id, max_wait_seconds=300)

        print("[OK] Video completed!")
        print(f"URL: {final_status['video_url']}")
        print(f"Duration: {final_status['duration']} seconds")
        print()

        # Download video
        print("[INFO] Downloading video...")
        generator.download_video(
            final_status['video_url'],
            "generated_media/videos/vystar_partnership.mp4"
        )

        print()
        print("="*70)
        print("Avatar video generated successfully!")
        print("="*70)

    except ValueError as e:
        print(f"[ERROR] {e}")
    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()
