"""
Social Media Publisher with OAuth 2.0 Authentication
Publishes content to LinkedIn, Twitter/X, and Instagram using Clerk OAuth
"""

import asyncio
import aiohttp
from typing import Dict, Optional, List
from datetime import datetime
from .clerk_auth import ClerkSocialAuth


class SocialMediaPublisher:
    """
    Modern OAuth-based social media publisher using Clerk

    Replaces username/password authentication with secure OAuth tokens
    Supports: LinkedIn, Twitter/X, Instagram (via Facebook Graph API)
    """

    def __init__(self, clerk_auth: Optional[ClerkSocialAuth] = None):
        """
        Initialize publisher

        Args:
            clerk_auth: ClerkSocialAuth instance (creates new one if None)
        """
        self.auth = clerk_auth or ClerkSocialAuth()
        self.platforms_enabled = {
            "linkedin": True,
            "twitter": True,
            "instagram": True
        }

    async def publish_to_linkedin(
        self,
        content: str,
        media_url: Optional[str] = None,
        media_title: Optional[str] = None,
        media_description: Optional[str] = None
    ) -> Dict:
        """
        Publish to LinkedIn using OAuth 2.0

        Args:
            content: Post text (max 3000 characters)
            media_url: Optional media URL (image/article)
            media_title: Optional media title
            media_description: Optional media description

        Returns:
            Result dict:
            {
                "success": bool,
                "platform": "linkedin",
                "post_id": str (if successful),
                "url": str (if successful),
                "error": str (if failed),
                "timestamp": str
            }
        """
        token = self.auth.get_linkedin_access_token()

        if not token:
            return {
                "success": False,
                "platform": "linkedin",
                "error": "LinkedIn not connected",
                "action": "Connect LinkedIn account in Clerk dashboard",
                "timestamp": datetime.utcnow().isoformat()
            }

        async with aiohttp.ClientSession() as session:
            try:
                # Get LinkedIn person ID (URN)
                person_id = await self._get_linkedin_person_id(token, session)

                # Prepare post payload (UGC Post API)
                payload = {
                    "author": f"urn:li:person:{person_id}",
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {
                                "text": content
                            },
                            "shareMediaCategory": "ARTICLE" if media_url else "NONE"
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                }

                # Add media if provided
                if media_url:
                    payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                        {
                            "status": "READY",
                            "description": {
                                "text": media_description or ""
                            },
                            "originalUrl": media_url,
                            "title": {
                                "text": media_title or ""
                            }
                        }
                    ]

                # Post to LinkedIn
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "X-Restli-Protocol-Version": "2.0.0"
                }

                async with session.post(
                    "https://api.linkedin.com/v2/ugcPosts",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        post_id = result.get("id", "").split(":")[-1]  # Extract ID from URN

                        return {
                            "success": True,
                            "platform": "linkedin",
                            "post_id": post_id,
                            "url": f"https://www.linkedin.com/feed/update/urn:li:share:{post_id}",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "platform": "linkedin",
                            "error": f"HTTP {response.status}: {error_text}",
                            "timestamp": datetime.utcnow().isoformat()
                        }

            except Exception as e:
                return {
                    "success": False,
                    "platform": "linkedin",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

    async def publish_to_twitter(
        self,
        content: str,
        media_ids: Optional[List[str]] = None
    ) -> Dict:
        """
        Publish to Twitter/X using OAuth 2.0

        Args:
            content: Tweet text (max 280 characters for standard accounts)
            media_ids: Optional list of uploaded media IDs

        Returns:
            Result dict with success status, tweet ID, and URL
        """
        token = self.auth.get_twitter_access_token()

        if not token:
            return {
                "success": False,
                "platform": "twitter",
                "error": "Twitter not connected",
                "action": "Connect Twitter account in Clerk dashboard",
                "timestamp": datetime.utcnow().isoformat()
            }

        async with aiohttp.ClientSession() as session:
            try:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }

                # Twitter API v2 create tweet endpoint
                payload = {
                    "text": content
                }

                # Add media if provided
                if media_ids:
                    payload["media"] = {"media_ids": media_ids}

                async with session.post(
                    "https://api.twitter.com/2/tweets",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        tweet_id = result["data"]["id"]

                        return {
                            "success": True,
                            "platform": "twitter",
                            "post_id": tweet_id,
                            "url": f"https://twitter.com/i/web/status/{tweet_id}",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "platform": "twitter",
                            "error": f"HTTP {response.status}: {error_text}",
                            "timestamp": datetime.utcnow().isoformat()
                        }

            except Exception as e:
                return {
                    "success": False,
                    "platform": "twitter",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

    async def publish_to_instagram(
        self,
        caption: str,
        image_url: str
    ) -> Dict:
        """
        Publish to Instagram using Facebook Graph API

        Note: Instagram requires media (image/video) - cannot post text-only

        Args:
            caption: Post caption text
            image_url: Required publicly accessible image URL

        Returns:
            Result dict with success status and media ID
        """
        token = self.auth.get_instagram_access_token()

        if not token:
            return {
                "success": False,
                "platform": "instagram",
                "error": "Instagram not connected",
                "action": "Connect Instagram account in Clerk dashboard",
                "timestamp": datetime.utcnow().isoformat()
            }

        if not image_url:
            return {
                "success": False,
                "platform": "instagram",
                "error": "Instagram requires media (image or video)",
                "action": "Provide image_url parameter",
                "timestamp": datetime.utcnow().isoformat()
            }

        async with aiohttp.ClientSession() as session:
            try:
                # Get Instagram Business Account ID
                ig_account_id = await self._get_instagram_account_id(token, session)

                # Step 1: Create media container
                container_params = {
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": token
                }

                async with session.post(
                    f"https://graph.facebook.com/v18.0/{ig_account_id}/media",
                    params=container_params
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "platform": "instagram",
                            "error": f"Container creation failed: HTTP {response.status}: {error_text}",
                            "timestamp": datetime.utcnow().isoformat()
                        }

                    container_result = await response.json()
                    container_id = container_result["id"]

                # Step 2: Publish media container
                publish_params = {
                    "creation_id": container_id,
                    "access_token": token
                }

                async with session.post(
                    f"https://graph.facebook.com/v18.0/{ig_account_id}/media_publish",
                    params=publish_params
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "platform": "instagram",
                            "post_id": result["id"],
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "platform": "instagram",
                            "error": f"Publish failed: HTTP {response.status}: {error_text}",
                            "timestamp": datetime.utcnow().isoformat()
                        }

            except Exception as e:
                return {
                    "success": False,
                    "platform": "instagram",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

    async def publish_multi_platform(
        self,
        content: Dict[str, str],
        platforms: List[str] = ["linkedin", "twitter"],
        media: Optional[Dict] = None
    ) -> Dict[str, Dict]:
        """
        Publish to multiple platforms simultaneously

        Args:
            content: Dict of platform: content_text
                     Example: {"linkedin": "Full post...", "twitter": "Short version..."}
                     Or: {"default": "Same content for all"}
            platforms: List of platforms to publish to ["linkedin", "twitter", "instagram"]
            media: Optional media dict:
                   {"url": "https://...", "title": "...", "description": "..."}

        Returns:
            Dict of platform: result
            Example: {"linkedin": {...}, "twitter": {...}}
        """
        tasks = []
        default_content = content.get("default", "")

        # Prepare publishing tasks
        if "linkedin" in platforms and self.platforms_enabled["linkedin"]:
            linkedin_content = content.get("linkedin", default_content)
            tasks.append(("linkedin", self.publish_to_linkedin(
                linkedin_content,
                media_url=media.get("url") if media else None,
                media_title=media.get("title") if media else None,
                media_description=media.get("description") if media else None
            )))

        if "twitter" in platforms and self.platforms_enabled["twitter"]:
            twitter_content = content.get("twitter", default_content)
            # Twitter has 280 char limit
            if len(twitter_content) > 280:
                twitter_content = twitter_content[:277] + "..."

            tasks.append(("twitter", self.publish_to_twitter(twitter_content)))

        if "instagram" in platforms and self.platforms_enabled["instagram"] and media:
            instagram_content = content.get("instagram", default_content)
            tasks.append(("instagram", self.publish_to_instagram(
                instagram_content,
                media.get("url", "")
            )))

        # Execute all publishes in parallel
        results = {}
        for platform, task in tasks:
            result = await task
            results[platform] = result

        return results

    async def _get_linkedin_person_id(self, token: str, session: aiohttp.ClientSession) -> str:
        """Get LinkedIn person URN from access token"""
        headers = {
            "Authorization": f"Bearer {token}"
        }

        async with session.get(
            "https://api.linkedin.com/v2/userinfo",
            headers=headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("sub")  # LinkedIn person ID
            else:
                error = await response.text()
                raise Exception(f"Failed to get LinkedIn person ID: {error}")

    async def _get_instagram_account_id(self, token: str, session: aiohttp.ClientSession) -> str:
        """Get Instagram Business Account ID from Facebook token"""
        params = {
            "fields": "instagram_business_account",
            "access_token": token
        }

        async with session.get(
            "https://graph.facebook.com/v18.0/me/accounts",
            params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                # Get first page's Instagram account
                if data.get("data") and len(data["data"]) > 0:
                    page_data = data["data"][0]
                    if "instagram_business_account" in page_data:
                        return page_data["instagram_business_account"]["id"]

            error = await response.text()
            raise Exception(f"Failed to get Instagram account ID: {error}")


# Example usage / testing
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    async def test_publisher():
        print("="*70)
        print("SOCIAL MEDIA PUBLISHER TEST")
        print("="*70)
        print()

        try:
            publisher = SocialMediaPublisher()
            print("[OK] Publisher initialized")
            print()

            # Check connected platforms
            connections = publisher.auth.verify_all_connections()
            print("[INFO] Platform connections:")
            for platform, connected in connections.items():
                status = "[CONNECTED]" if connected else "[NOT CONNECTED]"
                print(f"  {status} {platform.capitalize()}")
            print()

            # Test publish (dry run - won't actually post)
            test_content = {
                "default": "Test post from Milton Overton AI Publicist system. Let's Go Owls!"
            }

            print("[INFO] Testing multi-platform publish (DRY RUN)...")
            print(f"Content: {test_content['default']}")
            print()

            # Only test platforms that are connected
            connected_platforms = [p for p, c in connections.items() if c]

            if not connected_platforms:
                print("[WARN] No platforms connected yet")
                print("Connect social accounts in Clerk dashboard to test publishing")
            else:
                print(f"[INFO] Would publish to: {', '.join(connected_platforms)}")
                print()
                print("To actually publish, uncomment the publish call below")
                # results = await publisher.publish_multi_platform(
                #     content=test_content,
                #     platforms=connected_platforms
                # )
                # for platform, result in results.items():
                #     print(f"{platform}: {result}")

        except ValueError as e:
            print(f"[ERROR] Configuration error: {e}")
            print()
            print("Please ensure:")
            print("1. CLERK_SECRET_KEY is set in .env")
            print("2. MILTON_USER_ID is set in .env")
            print("3. Social accounts are connected in Clerk")

        except Exception as e:
            print(f"[ERROR] {e}")

    # Run async test
    asyncio.run(test_publisher())
