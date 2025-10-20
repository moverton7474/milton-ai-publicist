"""
Automated Scheduler Daemon for Milton AI Publicist
Runs continuously in background, publishing posts at scheduled times
"""

import time
import signal
import sys
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from module_v.database import get_database
from module_iii import SocialMediaPublisher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler_daemon.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SchedulerDaemon')


class SchedulerDaemon:
    """
    Background daemon that automatically publishes scheduled posts

    Features:
    - Checks for due posts every minute
    - Publishes to LinkedIn, Twitter, Instagram
    - Updates database with results
    - Error handling and retry logic
    - Graceful shutdown
    """

    def __init__(self, check_interval: int = 60):
        """
        Initialize scheduler daemon

        Args:
            check_interval: Seconds between checks (default 60 = 1 minute)
        """
        self.check_interval = check_interval
        self.db = get_database()
        self.publisher = SocialMediaPublisher()
        self.running = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._shutdown_handler)
        signal.signal(signal.SIGTERM, self._shutdown_handler)

        logger.info("Scheduler Daemon initialized")
        logger.info(f"Check interval: {check_interval} seconds")

    def _shutdown_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received shutdown signal ({signum})")
        self.stop()

    def start(self):
        """Start the scheduler daemon"""
        logger.info("="*70)
        logger.info("MILTON AI PUBLICIST - SCHEDULER DAEMON STARTING")
        logger.info("="*70)
        logger.info(f"Current time: {datetime.now(timezone.utc).isoformat()}")
        logger.info(f"Check interval: {self.check_interval} seconds")
        logger.info("Press Ctrl+C to stop")
        logger.info("="*70)

        self.running = True

        try:
            while self.running:
                self._check_and_publish()

                if self.running:  # Only sleep if still running
                    logger.debug(f"Sleeping for {self.check_interval} seconds...")
                    time.sleep(self.check_interval)

        except Exception as e:
            logger.error(f"Daemon crashed: {e}", exc_info=True)
            raise
        finally:
            logger.info("Scheduler Daemon stopped")

    def stop(self):
        """Stop the scheduler daemon"""
        logger.info("Stopping scheduler daemon...")
        self.running = False

    def _check_and_publish(self):
        """Check for due posts and publish them"""
        try:
            # Get all posts that are due to be published
            due_posts = self.db.get_due_scheduled_posts()

            if not due_posts:
                logger.debug("No posts due for publishing")
                return

            logger.info(f"Found {len(due_posts)} post(s) due for publishing")

            # Process each due post
            for scheduled_post in due_posts:
                self._publish_scheduled_post(scheduled_post)

        except Exception as e:
            logger.error(f"Error checking for due posts: {e}", exc_info=True)

    def _publish_scheduled_post(self, scheduled_post: dict):
        """
        Publish a single scheduled post

        Args:
            scheduled_post: Dict containing scheduled_post data and post content
        """
        schedule_id = scheduled_post['id']
        post_id = scheduled_post['post_id']
        platform = scheduled_post['platform']
        scheduled_time = scheduled_post['scheduled_time']

        logger.info("="*70)
        logger.info(f"Publishing Scheduled Post")
        logger.info(f"  Schedule ID: {schedule_id}")
        logger.info(f"  Post ID: {post_id}")
        logger.info(f"  Platform: {platform}")
        logger.info(f"  Scheduled: {scheduled_time}")
        logger.info("="*70)

        try:
            # Get post content
            content = scheduled_post['content']
            graphic_url = scheduled_post.get('graphic_url')
            video_url = scheduled_post.get('video_url')

            logger.info(f"Content: {content[:100]}...")
            if graphic_url:
                logger.info(f"Graphic: {graphic_url}")
            if video_url:
                logger.info(f"Video: {video_url}")

            # Publish to the specified platform
            result = asyncio.run(self._publish_to_platform(
                platform=platform,
                content=content,
                graphic_url=graphic_url,
                video_url=video_url
            ))

            if result['success']:
                post_url = result.get('url')
                logger.info(f"✅ SUCCESS: Published to {platform}")
                logger.info(f"   URL: {post_url}")

                # Mark scheduled post as published
                self.db.mark_scheduled_post_published(schedule_id, post_url)

                # Mark the original post as published
                self.db.mark_post_published(post_id, post_url)

                # Log the publishing result
                self.db.log_publishing_result(
                    post_id=post_id,
                    platform=platform,
                    success=True,
                    post_url=post_url
                )
            else:
                error = result.get('error', 'Unknown error')
                logger.error(f"❌ FAILED: {error}")

                # Mark scheduled post as failed
                self.db.mark_scheduled_post_failed(schedule_id, error)

                # Log the failure
                self.db.log_publishing_result(
                    post_id=post_id,
                    platform=platform,
                    success=False,
                    error_message=error
                )

        except Exception as e:
            error_msg = f"Exception during publishing: {str(e)}"
            logger.error(error_msg, exc_info=True)

            # Mark as failed
            self.db.mark_scheduled_post_failed(schedule_id, error_msg)

            # Log the failure
            self.db.log_publishing_result(
                post_id=post_id,
                platform=platform,
                success=False,
                error_message=error_msg
            )

    async def _publish_to_platform(
        self,
        platform: str,
        content: str,
        graphic_url: Optional[str] = None,
        video_url: Optional[str] = None
    ) -> dict:
        """
        Publish content to a specific platform

        Args:
            platform: 'linkedin', 'twitter', or 'instagram'
            content: Post text content
            graphic_url: Optional URL/path to graphic
            video_url: Optional URL/path to video

        Returns:
            Dict with 'success' (bool) and 'url' or 'error'
        """
        try:
            if platform == 'linkedin':
                return await self.publisher.publish_to_linkedin(
                    content=content,
                    image_url=graphic_url,
                    video_url=video_url
                )

            elif platform == 'twitter':
                return await self.publisher.publish_to_twitter(
                    content=content,
                    image_url=graphic_url,
                    video_url=video_url
                )

            elif platform == 'instagram':
                return await self.publisher.publish_to_instagram(
                    content=content,
                    image_url=graphic_url,
                    video_url=video_url
                )

            else:
                return {
                    'success': False,
                    'error': f'Unknown platform: {platform}'
                }

        except Exception as e:
            logger.error(f"Error publishing to {platform}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def get_status(self) -> dict:
        """Get daemon status"""
        stats = self.db.get_stats()

        # Get upcoming scheduled posts
        pending_schedules = self.db.get_all_scheduled_posts(status='pending')

        return {
            'running': self.running,
            'check_interval': self.check_interval,
            'total_posts': stats['total_posts'],
            'published_posts': stats['published_posts'],
            'pending_schedules': len(pending_schedules),
            'next_check': datetime.now(timezone.utc).isoformat()
        }


def main():
    """Main entry point for scheduler daemon"""
    import argparse

    parser = argparse.ArgumentParser(description='Milton AI Publicist Scheduler Daemon')
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (faster checks, verbose logging)'
    )

    args = parser.parse_args()

    # Test mode: faster checks, debug logging
    if args.test:
        args.interval = 10  # Check every 10 seconds
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Running in TEST MODE (10-second intervals)")

    # Create and start daemon
    daemon = SchedulerDaemon(check_interval=args.interval)

    try:
        daemon.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        daemon.stop()
    except Exception as e:
        logger.error(f"Daemon failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
