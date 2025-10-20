"""
Zapier Publishing Module - Webhook-based Social Media Publishing
Sends posts to Zapier webhooks which handle OAuth and platform publishing
"""

import httpx
import os
import logging
from typing import Dict, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZapierPublisher:
    """
    Handles publishing posts to social media via Zapier webhooks

    Workflow:
    1. Dashboard calls publish_to_platform()
    2. ZapierPublisher sends HTTP POST to Zapier webhook
    3. Zapier receives webhook and posts to LinkedIn/Instagram/Twitter
    4. Returns success/failure status

    Benefits:
    - No OAuth token management required
    - No platform API changes to track
    - Enterprise-grade reliability via Zapier
    - Multi-platform support with simple webhook URLs
    """

    def __init__(self):
        """Initialize Zapier publisher with webhook URLs from environment"""
        self.webhooks = {
            "linkedin": os.getenv("ZAPIER_LINKEDIN_WEBHOOK"),
            "instagram": os.getenv("ZAPIER_INSTAGRAM_WEBHOOK"),
            "twitter": os.getenv("ZAPIER_TWITTER_WEBHOOK"),
            "facebook": os.getenv("ZAPIER_FACEBOOK_WEBHOOK")
        }

        # HTTP client configuration
        self.timeout = httpx.Timeout(30.0, connect=10.0)  # 30s total, 10s connect
        self.max_retries = 2

        logger.info("ZapierPublisher initialized")
        logger.info(f"Configured platforms: {[k for k, v in self.webhooks.items() if v]}")


    def is_platform_configured(self, platform: str) -> bool:
        """
        Check if a platform has a webhook URL configured

        Args:
            platform: Platform name (linkedin, instagram, twitter, facebook)

        Returns:
            True if webhook URL exists, False otherwise
        """
        webhook_url = self.webhooks.get(platform.lower())
        return webhook_url is not None and webhook_url.strip() != ""


    def get_configured_platforms(self) -> Dict[str, bool]:
        """
        Get status of all platform configurations

        Returns:
            Dict with platform names and configuration status
        """
        return {
            platform: self.is_platform_configured(platform)
            for platform in ["linkedin", "instagram", "twitter", "facebook"]
        }


    async def publish_to_platform(
        self,
        platform: str,
        content: str,
        post_id: Optional[int] = None,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Publish content to a social media platform via Zapier webhook

        Args:
            platform: Target platform (linkedin, instagram, twitter, facebook)
            content: Post content/caption
            post_id: Internal post ID for tracking
            image_url: Optional image URL to include
            video_url: Optional video URL to include
            metadata: Additional data to send to Zapier (tags, mentions, etc.)

        Returns:
            Dict with success status, message, and optional error details

        Example:
            result = await publisher.publish_to_platform(
                platform="linkedin",
                content="Exciting news! Let's Go Owls!",
                post_id=123,
                image_url="https://example.com/image.jpg"
            )
        """
        platform = platform.lower()

        # Validate platform is configured
        if not self.is_platform_configured(platform):
            logger.warning(f"Platform {platform} not configured - no webhook URL")
            return {
                "success": False,
                "error": f"{platform} webhook not configured",
                "platform": platform,
                "action": "configure_webhook",
                "message": f"Please add ZAPIER_{platform.upper()}_WEBHOOK to your .env file"
            }

        webhook_url = self.webhooks[platform]

        # Build webhook payload
        payload = {
            "content": content,
            "platform": platform,
            "post_id": post_id,
            "timestamp": datetime.now().isoformat(),
            "source": "milton_ai_publicist"
        }

        # Add media URLs if provided
        if image_url:
            payload["image_url"] = image_url

        if video_url:
            payload["video_url"] = video_url

        # Add metadata if provided
        if metadata:
            payload["metadata"] = metadata

        # Send webhook request with retries
        attempt = 0
        last_error = None

        while attempt <= self.max_retries:
            try:
                logger.info(f"Publishing to {platform} via Zapier (attempt {attempt + 1}/{self.max_retries + 1})")
                logger.debug(f"Webhook URL: {webhook_url[:50]}...")
                logger.debug(f"Payload: {payload}")

                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        webhook_url,
                        json=payload,
                        headers={
                            "Content-Type": "application/json",
                            "User-Agent": "Milton-AI-Publicist/1.0"
                        }
                    )

                    # Check response status
                    if response.status_code in [200, 201, 202]:
                        logger.info(f"Successfully published post {post_id} to {platform}")

                        return {
                            "success": True,
                            "platform": platform,
                            "post_id": post_id,
                            "method": "zapier",
                            "message": f"Published to {platform} via Zapier",
                            "zapier_status": response.status_code,
                            "timestamp": datetime.now().isoformat()
                        }

                    else:
                        # Non-success status code
                        error_text = response.text[:200] if response.text else "No error details"
                        logger.warning(f"Zapier webhook returned {response.status_code}: {error_text}")
                        last_error = f"HTTP {response.status_code}: {error_text}"

                        # Don't retry on 4xx errors (client errors)
                        if 400 <= response.status_code < 500:
                            break

            except httpx.TimeoutException as e:
                last_error = f"Request timeout: {str(e)}"
                logger.warning(f"Timeout publishing to {platform}: {e}")

            except httpx.NetworkError as e:
                last_error = f"Network error: {str(e)}"
                logger.warning(f"Network error publishing to {platform}: {e}")

            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                logger.error(f"Unexpected error publishing to {platform}: {e}", exc_info=True)

            attempt += 1

        # All attempts failed
        logger.error(f"Failed to publish post {post_id} to {platform} after {self.max_retries + 1} attempts")

        return {
            "success": False,
            "platform": platform,
            "post_id": post_id,
            "error": last_error or "Unknown error",
            "action": "check_zapier_zap",
            "message": f"Failed to publish to {platform}. Check that your Zap is turned ON.",
            "timestamp": datetime.now().isoformat()
        }


    async def publish_to_multiple(
        self,
        platforms: list[str],
        content: str,
        post_id: Optional[int] = None,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Publish content to multiple platforms simultaneously

        Args:
            platforms: List of platform names to publish to
            content: Post content/caption
            post_id: Internal post ID for tracking
            image_url: Optional image URL
            video_url: Optional video URL
            metadata: Additional metadata

        Returns:
            Dict with platform names as keys and publish results as values

        Example:
            results = await publisher.publish_to_multiple(
                platforms=["linkedin", "twitter"],
                content="Go Owls!",
                post_id=123
            )
            # Returns: {
            #   "linkedin": {"success": True, ...},
            #   "twitter": {"success": True, ...}
            # }
        """
        results = {}

        for platform in platforms:
            result = await self.publish_to_platform(
                platform=platform,
                content=content,
                post_id=post_id,
                image_url=image_url,
                video_url=video_url,
                metadata=metadata
            )
            results[platform] = result

        return results


    def get_webhook_setup_instructions(self, platform: str) -> Dict[str, Any]:
        """
        Get setup instructions for configuring a Zapier webhook

        Args:
            platform: Platform name

        Returns:
            Dict with setup instructions and example webhook URL
        """
        platform = platform.lower()

        return {
            "platform": platform,
            "steps": [
                f"1. Go to https://zapier.com/app/editor",
                f"2. Create new Zap",
                f"3. Trigger: Webhooks by Zapier → Catch Hook",
                f"4. Action: {platform.capitalize()} → Create Post/Update",
                f"5. Map fields: content → {{{{1__content}}}}, image_url → {{{{1__image_url}}}}",
                f"6. Test and turn ON",
                f"7. Copy webhook URL",
                f"8. Add to .env: ZAPIER_{platform.upper()}_WEBHOOK=<your_webhook_url>"
            ],
            "example_webhook": f"https://hooks.zapier.com/hooks/catch/XXXXX/YYYYY/",
            "env_var": f"ZAPIER_{platform.upper()}_WEBHOOK",
            "zapier_url": "https://zapier.com/app/editor"
        }


# Convenience function for quick publishing
async def publish_post_via_zapier(
    platform: str,
    content: str,
    post_id: Optional[int] = None,
    image_url: Optional[str] = None,
    video_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quick convenience function for publishing via Zapier

    Example:
        result = await publish_post_via_zapier(
            platform="linkedin",
            content="Go Owls!",
            post_id=123
        )
    """
    publisher = ZapierPublisher()
    return await publisher.publish_to_platform(
        platform=platform,
        content=content,
        post_id=post_id,
        image_url=image_url,
        video_url=video_url
    )
