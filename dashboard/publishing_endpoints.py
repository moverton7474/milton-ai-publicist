"""
Publishing API Endpoints - FastAPI Router for Zapier Integration
Provides RESTful API endpoints for publishing posts to social media via Zapier
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Optional, List
import logging
from datetime import datetime

from dashboard.zapier_publisher import ZapierPublisher
from module_v.database import get_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/publish", tags=["publishing"])

# Initialize services
zapier_publisher = ZapierPublisher()
db = get_database()


@router.get("/platforms")
async def get_platform_status():
    """
    Get configuration status for all publishing platforms

    Returns:
        Dict with platform names and whether they're configured

    Example Response:
        {
            "platforms": {
                "linkedin": true,
                "instagram": false,
                "twitter": true,
                "facebook": false
            },
            "configured_count": 2,
            "total_platforms": 4
        }
    """
    platforms = zapier_publisher.get_configured_platforms()
    configured_count = sum(1 for v in platforms.values() if v)

    return {
        "platforms": platforms,
        "configured_count": configured_count,
        "total_platforms": len(platforms)
    }


@router.get("/platforms/{platform}/setup")
async def get_platform_setup(platform: str):
    """
    Get setup instructions for configuring a specific platform

    Args:
        platform: Platform name (linkedin, instagram, twitter, facebook)

    Returns:
        Setup instructions with step-by-step guide

    Example Response:
        {
            "platform": "linkedin",
            "steps": [...],
            "example_webhook": "https://hooks.zapier.com/...",
            "env_var": "ZAPIER_LINKEDIN_WEBHOOK",
            "zapier_url": "https://zapier.com/app/editor"
        }
    """
    return zapier_publisher.get_webhook_setup_instructions(platform)


@router.post("/posts/{post_id}/{platform}")
async def publish_to_platform(post_id: int, platform: str):
    """
    Publish a specific post to a specific platform via Zapier

    Args:
        post_id: Database ID of post to publish
        platform: Target platform (linkedin, instagram, twitter, facebook)

    Returns:
        Publish result with success status

    Example:
        POST /api/publish/posts/123/linkedin
        Returns: {"success": true, "platform": "linkedin", ...}
    """
    # Validate platform
    platform = platform.lower()
    valid_platforms = ["linkedin", "instagram", "twitter", "facebook"]

    if platform not in valid_platforms:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform '{platform}'. Must be one of: {', '.join(valid_platforms)}"
        )

    # Get post from database
    post = db.get_post(post_id)

    if not post:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")

    # Check if platform is configured
    if not zapier_publisher.is_platform_configured(platform):
        return {
            "success": False,
            "error": f"{platform} webhook not configured",
            "action": "configure_webhook",
            "setup_url": f"/api/publish/platforms/{platform}/setup"
        }

    # Publish via Zapier
    result = await zapier_publisher.publish_to_platform(
        platform=platform,
        content=post["content"],
        post_id=post_id,
        image_url=post.get("graphic_url"),
        video_url=post.get("video_url"),
        metadata={
            "voice_type": post.get("voice_type"),
            "scenario": post.get("scenario"),
            "word_count": post.get("word_count")
        }
    )

    # If successful, update database
    if result.get("success"):
        # Mark post as published (update status to 'published')
        try:
            db.update_post(post_id, status='published')
        except Exception as e:
            logger.warning(f"Could not update post status: {e}")

        logger.info(f"Successfully published post {post_id} to {platform}")

    else:
        logger.error(f"Failed to publish post {post_id} to {platform}: {result.get('error')}")

        logger.warning(f"Failed to publish post {post_id} to {platform}: {result.get('error')}")

    return result


@router.post("/posts/{post_id}/multi")
async def publish_to_multiple_platforms(post_id: int, request: Request):
    """
    Publish a post to multiple platforms simultaneously

    Request Body:
        {
            "platforms": ["linkedin", "twitter", "instagram"]
        }

    Returns:
        Results for each platform

    Example Response:
        {
            "post_id": 123,
            "results": {
                "linkedin": {"success": true, ...},
                "twitter": {"success": true, ...},
                "instagram": {"success": false, "error": "..."}
            },
            "success_count": 2,
            "failure_count": 1
        }
    """
    data = await request.json()
    platforms = data.get("platforms", [])

    if not platforms:
        raise HTTPException(status_code=400, detail="No platforms specified")

    # Get post from database
    post = db.get_post(post_id)

    if not post:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")

    # Publish to all platforms
    results = await zapier_publisher.publish_to_multiple(
        platforms=platforms,
        content=post["content"],
        post_id=post_id,
        image_url=post.get("graphic_url"),
        video_url=post.get("video_url"),
        metadata={
            "voice_type": post.get("voice_type"),
            "scenario": post.get("scenario"),
            "word_count": post.get("word_count")
        }
    )

    # Count successes and failures
    success_count = sum(1 for r in results.values() if r.get("success"))
    failure_count = len(results) - success_count

    # Log each result
    for platform, result in results.items():
        if result.get("success"):
            db.mark_post_published(post_id, post_url=None)
            db.log_publishing_result(
                post_id=post_id,
                platform=platform,
                success=True,
                response_data=result
            )
        else:
            db.log_publishing_result(
                post_id=post_id,
                platform=platform,
                success=False,
                error_message=result.get("error"),
                response_data=result
            )

    return {
        "post_id": post_id,
        "results": results,
        "success_count": success_count,
        "failure_count": failure_count,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/history")
async def get_publishing_history(
    limit: int = 50,
    platform: Optional[str] = None,
    success_only: bool = False
):
    """
    Get publishing history from database

    Query Parameters:
        limit: Max number of results (default 50)
        platform: Filter by platform (optional)
        success_only: Only show successful publishes (default false)

    Returns:
        List of publishing records

    Example:
        GET /api/publish/history?platform=linkedin&limit=10
    """
    try:
        # Get publishing results from database
        results = db.get_publishing_results(limit=limit)

        # Filter by platform if specified
        if platform:
            results = [r for r in results if r.get("platform") == platform.lower()]

        # Filter by success if specified
        if success_only:
            results = [r for r in results if r.get("success")]

        return {
            "history": results,
            "count": len(results),
            "filters": {
                "platform": platform,
                "success_only": success_only,
                "limit": limit
            }
        }

    except Exception as e:
        logger.error(f"Error fetching publishing history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_publishing_stats():
    """
    Get publishing statistics

    Returns:
        Summary statistics about publishing activity

    Example Response:
        {
            "total_published": 150,
            "by_platform": {
                "linkedin": 80,
                "twitter": 45,
                "instagram": 25
            },
            "success_rate": 0.95,
            "last_published": "2025-10-20T12:00:00"
        }
    """
    try:
        # Get all publishing results
        results = db.get_publishing_results(limit=1000)

        # Calculate stats
        total = len(results)
        successes = sum(1 for r in results if r.get("success"))
        success_rate = successes / total if total > 0 else 0

        # Count by platform
        by_platform = {}
        for result in results:
            platform = result.get("platform", "unknown")
            by_platform[platform] = by_platform.get(platform, 0) + 1

        # Get last published timestamp
        last_published = None
        if results:
            last_published = results[0].get("published_at")  # Assuming sorted by most recent

        return {
            "total_published": total,
            "successful_publishes": successes,
            "failed_publishes": total - successes,
            "success_rate": round(success_rate, 3),
            "by_platform": by_platform,
            "last_published": last_published
        }

    except Exception as e:
        logger.error(f"Error calculating publishing stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/{platform}")
async def test_platform_webhook(platform: str):
    """
    Test a platform's webhook configuration with a dummy payload

    Args:
        platform: Platform to test

    Returns:
        Test result indicating if webhook is reachable

    Example:
        POST /api/publish/test/linkedin
    """
    platform = platform.lower()

    if not zapier_publisher.is_platform_configured(platform):
        return {
            "success": False,
            "error": f"{platform} webhook not configured",
            "action": "configure_webhook"
        }

    # Send test payload
    result = await zapier_publisher.publish_to_platform(
        platform=platform,
        content="🧪 Test message from Milton AI Publicist (this is a test, not a real post)",
        post_id=None,
        metadata={"test": True}
    )

    return {
        "platform": platform,
        "test_result": result,
        "message": "Check your Zap history in Zapier to see if test was received"
    }


# Export router for inclusion in main app
__all__ = ["router"]
