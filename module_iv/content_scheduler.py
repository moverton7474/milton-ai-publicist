"""
Content Scheduler - Schedule posts for future publishing
Optimizes posting times based on platform best practices
"""

import os
import sys
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from module_iii import ClerkSocialAuth, SocialMediaPublisher

class ContentScheduler:
    """
    Manages scheduled posts and automatic publishing
    """

    def __init__(self, auth: Optional[ClerkSocialAuth] = None):
        """
        Initialize content scheduler

        Args:
            auth: Optional ClerkSocialAuth instance (creates new if None)
        """
        self.auth = auth or ClerkSocialAuth()
        self.publisher = SocialMediaPublisher(auth=self.auth)
        self.scheduled_posts: List[Dict] = []
        self.running = False

    def get_optimal_posting_times(self, platform: str) -> List[int]:
        """
        Get optimal posting hours for a platform (in 24-hour format)

        Args:
            platform: Platform name (linkedin, twitter, instagram)

        Returns:
            List of optimal hours (0-23)
        """
        optimal_times = {
            "linkedin": [7, 8, 12, 17, 18],  # Morning commute, lunch, evening
            "twitter": [8, 12, 17, 20],       # Morning, lunch, evening, night
            "instagram": [11, 13, 19, 21]     # Late morning, lunch, evening, night
        }

        return optimal_times.get(platform.lower(), [9, 12, 15])

    def calculate_next_optimal_time(
        self,
        platform: str,
        from_time: Optional[datetime] = None
    ) -> datetime:
        """
        Calculate the next optimal posting time for a platform

        Args:
            platform: Platform name
            from_time: Start time (defaults to now)

        Returns:
            Next optimal posting datetime
        """
        if from_time is None:
            from_time = datetime.now()

        optimal_hours = self.get_optimal_posting_times(platform)

        # Check today's remaining optimal times
        current_hour = from_time.hour

        for hour in optimal_hours:
            if hour > current_hour:
                # Found an optimal time today
                next_time = from_time.replace(
                    hour=hour,
                    minute=0,
                    second=0,
                    microsecond=0
                )
                return next_time

        # No optimal times left today, use first optimal time tomorrow
        tomorrow = from_time + timedelta(days=1)
        next_time = tomorrow.replace(
            hour=optimal_hours[0],
            minute=0,
            second=0,
            microsecond=0
        )

        return next_time

    def schedule_post(
        self,
        content: str,
        platforms: List[str],
        scheduled_time: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Schedule a post for future publishing

        Args:
            content: Post content
            platforms: List of platforms to post to
            scheduled_time: When to post (None = next optimal time for first platform)
            metadata: Additional metadata (media_url, etc.)

        Returns:
            Scheduled post object
        """
        if scheduled_time is None:
            # Use next optimal time for first platform
            scheduled_time = self.calculate_next_optimal_time(platforms[0])

        post = {
            "id": len(self.scheduled_posts) + 1,
            "content": content,
            "platforms": platforms,
            "scheduled_time": scheduled_time.isoformat(),
            "metadata": metadata or {},
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }

        self.scheduled_posts.append(post)

        return post

    def get_scheduled_posts(
        self,
        platform: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """
        Get scheduled posts, optionally filtered

        Args:
            platform: Filter by platform (None = all)
            status: Filter by status (None = all)

        Returns:
            List of scheduled posts
        """
        posts = self.scheduled_posts

        if platform:
            posts = [p for p in posts if platform in p.get("platforms", [])]

        if status:
            posts = [p for p in posts if p.get("status") == status]

        # Sort by scheduled time
        posts.sort(key=lambda p: p.get("scheduled_time", ""))

        return posts

    def cancel_scheduled_post(self, post_id: int) -> bool:
        """
        Cancel a scheduled post

        Args:
            post_id: Post ID to cancel

        Returns:
            True if cancelled, False if not found
        """
        for post in self.scheduled_posts:
            if post.get("id") == post_id:
                post["status"] = "cancelled"
                return True

        return False

    def reschedule_post(self, post_id: int, new_time: datetime) -> bool:
        """
        Reschedule a post to a new time

        Args:
            post_id: Post ID to reschedule
            new_time: New scheduled time

        Returns:
            True if rescheduled, False if not found
        """
        for post in self.scheduled_posts:
            if post.get("id") == post_id:
                post["scheduled_time"] = new_time.isoformat()
                return True

        return False

    async def publish_scheduled_post(self, post: Dict) -> Dict:
        """
        Publish a scheduled post to all platforms

        Args:
            post: Scheduled post object

        Returns:
            Publishing results
        """
        content = post.get("content", "")
        platforms = post.get("platforms", [])
        metadata = post.get("metadata", {})
        media_url = metadata.get("media_url")

        results = {
            "post_id": post.get("id"),
            "platforms": {},
            "published_at": datetime.now().isoformat()
        }

        # Publish to each platform
        for platform in platforms:
            try:
                if platform.lower() == "linkedin":
                    result = await self.publisher.publish_to_linkedin(content, media_url)
                elif platform.lower() == "twitter":
                    result = await self.publisher.publish_to_twitter(content, media_url)
                elif platform.lower() == "instagram":
                    if not media_url:
                        result = {"success": False, "error": "Instagram requires media_url"}
                    else:
                        result = await self.publisher.publish_to_instagram(content, media_url)
                else:
                    result = {"success": False, "error": f"Unknown platform: {platform}"}

                results["platforms"][platform] = result

            except Exception as e:
                results["platforms"][platform] = {
                    "success": False,
                    "error": str(e)
                }

        # Update post status
        all_success = all(r.get("success") for r in results["platforms"].values())
        post["status"] = "published" if all_success else "failed"
        post["published_at"] = results["published_at"]
        post["results"] = results

        return results

    async def check_and_publish_due_posts(self) -> List[Dict]:
        """
        Check for posts that are due and publish them

        Returns:
            List of publishing results
        """
        now = datetime.now()
        due_posts = []

        for post in self.scheduled_posts:
            if post.get("status") != "scheduled":
                continue

            scheduled_time = datetime.fromisoformat(post.get("scheduled_time"))

            if scheduled_time <= now:
                due_posts.append(post)

        results = []

        for post in due_posts:
            result = await self.publish_scheduled_post(post)
            results.append(result)

        return results

    async def run_scheduler(self, check_interval: int = 60):
        """
        Run the scheduler in a loop, checking for due posts

        Args:
            check_interval: Seconds between checks (default: 60)
        """
        self.running = True

        print(f"[INFO] Content scheduler started (checking every {check_interval}s)")

        while self.running:
            try:
                # Check for due posts
                results = await self.check_and_publish_due_posts()

                if results:
                    print(f"[INFO] Published {len(results)} scheduled post(s)")

                    for result in results:
                        post_id = result.get("post_id")
                        platforms = result.get("platforms", {})

                        for platform, platform_result in platforms.items():
                            if platform_result.get("success"):
                                print(f"       Post {post_id} → {platform}: SUCCESS")
                            else:
                                error = platform_result.get("error", "Unknown error")
                                print(f"       Post {post_id} → {platform}: FAILED ({error})")

                # Wait before next check
                await asyncio.sleep(check_interval)

            except Exception as e:
                print(f"[ERROR] Scheduler error: {e}")
                await asyncio.sleep(check_interval)

    def stop_scheduler(self):
        """Stop the scheduler loop"""
        self.running = False
        print("[INFO] Content scheduler stopped")

    def get_schedule_summary(self, days: int = 7) -> Dict:
        """
        Get a summary of scheduled posts for the next N days

        Args:
            days: Number of days to include

        Returns:
            Summary dict with posts by day
        """
        now = datetime.now()
        end_date = now + timedelta(days=days)

        summary = {
            "start_date": now.isoformat(),
            "end_date": end_date.isoformat(),
            "total_scheduled": 0,
            "by_day": {},
            "by_platform": {}
        }

        for post in self.scheduled_posts:
            if post.get("status") != "scheduled":
                continue

            scheduled_time = datetime.fromisoformat(post.get("scheduled_time"))

            if now <= scheduled_time <= end_date:
                summary["total_scheduled"] += 1

                # Group by day
                day_key = scheduled_time.strftime("%Y-%m-%d")
                if day_key not in summary["by_day"]:
                    summary["by_day"][day_key] = []
                summary["by_day"][day_key].append(post)

                # Count by platform
                for platform in post.get("platforms", []):
                    if platform not in summary["by_platform"]:
                        summary["by_platform"][platform] = 0
                    summary["by_platform"][platform] += 1

        return summary


# Example usage and testing
async def main():
    """Example usage of ContentScheduler"""
    print("="*70)
    print("CONTENT SCHEDULER - DEMO")
    print("="*70)
    print()

    scheduler = ContentScheduler()

    # Example 1: Schedule a LinkedIn post for next optimal time
    print("[INFO] Scheduling LinkedIn post for next optimal time...")

    post1 = scheduler.schedule_post(
        content="Excited to share our latest innovation in college athletics! Let's Go Owls!",
        platforms=["linkedin"]
    )

    print(f"       Post {post1['id']} scheduled for {post1['scheduled_time']}")
    print()

    # Example 2: Schedule a multi-platform post for specific time
    print("[INFO] Scheduling multi-platform post for tomorrow at 9 AM...")

    tomorrow_9am = datetime.now() + timedelta(days=1)
    tomorrow_9am = tomorrow_9am.replace(hour=9, minute=0, second=0, microsecond=0)

    post2 = scheduler.schedule_post(
        content="Big announcement coming soon! Stay tuned. Let's Go Owls!",
        platforms=["linkedin", "twitter"],
        scheduled_time=tomorrow_9am
    )

    print(f"       Post {post2['id']} scheduled for {post2['scheduled_time']}")
    print()

    # Example 3: Get optimal posting times
    print("[INFO] Optimal posting times:")
    for platform in ["linkedin", "twitter", "instagram"]:
        times = scheduler.get_optimal_posting_times(platform)
        print(f"       {platform.capitalize()}: {', '.join(f'{t}:00' for t in times)}")
    print()

    # Example 4: Get schedule summary
    print("[INFO] Schedule summary (next 7 days):")
    summary = scheduler.get_schedule_summary(days=7)
    print(f"       Total scheduled: {summary['total_scheduled']}")
    print(f"       By platform: {summary['by_platform']}")
    print()

    # Example 5: Show all scheduled posts
    print("[INFO] All scheduled posts:")
    posts = scheduler.get_scheduled_posts(status="scheduled")
    for post in posts:
        print(f"       Post {post['id']}: {post['scheduled_time']} → {', '.join(post['platforms'])}")
    print()

    print("="*70)
    print("To start the scheduler daemon:")
    print("  await scheduler.run_scheduler(check_interval=60)")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
