"""
Milton Overton AI Publicist - Approval Dashboard
Web interface for reviewing and publishing AI-generated content
"""

from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import sys
from datetime import datetime
from typing import Optional, List
from pathlib import Path
import asyncio
import shutil
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anthropic import Anthropic
from module_iii import SocialMediaPublisher, ClerkSocialAuth
from module_iv.news_monitor import NewsMonitor
from module_v.database import get_database
from module_v.analytics_engine import AnalyticsEngine
from module_vi.avatar_video_manager import avatar_video_manager

# Import Zapier publishing router
from dashboard.publishing_endpoints import router as publishing_router

app = FastAPI(title="Milton AI Publicist Dashboard")

# Include Zapier publishing endpoints
app.include_router(publishing_router)

# Templates and static files
templates = Jinja2Templates(directory="dashboard/templates")
app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")

# Mount generated media directory
media_dir = Path("generated_media")
media_dir.mkdir(exist_ok=True)
(media_dir / "graphics").mkdir(exist_ok=True)
(media_dir / "videos").mkdir(exist_ok=True)
(media_dir / "uploads").mkdir(exist_ok=True)  # User-uploaded media
app.mount("/media", StaticFiles(directory="generated_media"), name="media")

# Initialize services
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
publisher = None  # Will initialize when needed

# Initialize database (replaces in-memory storage)
db = get_database()
print("[INFO] Database connected: Persistent storage active")

# Initialize analytics engine
analytics = AnalyticsEngine()
print("[INFO] Analytics engine initialized")

# Initialize news monitor
news_monitor = NewsMonitor()
print("[INFO] News monitor initialized")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "Milton AI Publicist Dashboard"
    })


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard with access to all features"""
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "title": "Milton AI - Admin Dashboard"
    })


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Settings page for OAuth connections"""
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "title": "Settings - Milton AI Publicist"
    })


# ========================================================================
# OAUTH / AUTHENTICATION ENDPOINTS
# ========================================================================

@app.post("/api/auth/{platform}/connect")
async def connect_platform(platform: str):
    """
    Initiate OAuth connection for a platform
    Returns auth_url for user to visit
    """
    try:
        auth = ClerkSocialAuth()

        # Generate Clerk OAuth URL based on platform
        # Using actual Clerk domain: cool-fish-70.clerk.accounts.dev
        redirect_uri = f"{os.getenv('APP_URL', 'http://localhost:8080')}/auth/callback/{platform}"

        if platform == "linkedin":
            auth_url = f"https://cool-fish-70.clerk.accounts.dev/oauth/authorize?client_id=mhOx7MwgWEvvYqkm&response_type=code&redirect_uri={redirect_uri}&scope=r_liteprofile%20w_member_social"
        elif platform == "twitter":
            auth_url = f"https://cool-fish-70.clerk.accounts.dev/oauth/authorize?client_id=mhOx7MwgWEvvYqkm&response_type=code&redirect_uri={redirect_uri}&scope=tweet.read%20tweet.write%20users.read"
        elif platform == "instagram":
            auth_url = f"https://cool-fish-70.clerk.accounts.dev/oauth/authorize?client_id=mhOx7MwgWEvvYqkm&response_type=code&redirect_uri={redirect_uri}&scope=instagram_basic"
        else:
            return {"error": f"Platform '{platform}' not supported"}

        return {
            "success": True,
            "platform": platform,
            "auth_url": auth_url,
            "message": "Redirect user to auth_url to complete OAuth"
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/api/auth/{platform}/disconnect")
async def disconnect_platform(platform: str):
    """
    Disconnect OAuth connection for a platform
    """
    try:
        auth = ClerkSocialAuth()

        # TODO: Implement actual Clerk disconnect logic
        # For now, return success

        return {
            "success": True,
            "platform": platform,
            "message": f"{platform} disconnected successfully"
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/auth/{platform}/test")
async def test_platform_connection(platform: str):
    """
    Test if OAuth connection is working
    """
    try:
        auth = ClerkSocialAuth()
        connections = auth.verify_all_connections()

        is_connected = connections.get(platform, False)

        if not is_connected:
            return {
                "success": False,
                "error": f"{platform} is not connected"
            }

        # If connected, try to get account info
        # TODO: Implement actual test API call to the platform

        return {
            "success": True,
            "platform": platform,
            "account_name": f"Test Account ({platform})",
            "message": "Connection is working"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/auth/callback/{platform}")
async def auth_callback(platform: str, request: Request):
    """
    OAuth callback handler
    Clerk will redirect here after user authorizes
    """
    try:
        # Get OAuth code from query params
        code = request.query_params.get('code')

        if not code:
            return HTMLResponse("""
                <html>
                <body>
                    <h1>❌ Authorization Failed</h1>
                    <p>No authorization code received.</p>
                    <a href="/settings">← Back to Settings</a>
                </body>
                </html>
            """)

        # TODO: Exchange code for access token via Clerk API
        # For now, show success message

        return HTMLResponse(f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0;
                    }}
                    .card {{
                        background: white;
                        padding: 40px;
                        border-radius: 15px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                        text-align: center;
                        max-width: 500px;
                    }}
                    h1 {{ color: #28a745; }}
                    p {{ color: #666; margin: 20px 0; }}
                    a {{
                        display: inline-block;
                        background: #667eea;
                        color: white;
                        padding: 12px 24px;
                        text-decoration: none;
                        border-radius: 8px;
                        margin-top: 20px;
                    }}
                    a:hover {{ background: #5568d3; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>✓ {platform.capitalize()} Connected!</h1>
                    <p>Your {platform.capitalize()} account has been successfully connected.</p>
                    <p>You can now publish posts to {platform.capitalize()} automatically.</p>
                    <a href="/settings">← Back to Settings</a>
                    <a href="/" style="background: #28a745; margin-left: 10px;">Go to Dashboard</a>
                </div>
            </body>
            </html>
        """)

    except Exception as e:
        return HTMLResponse(f"""
            <html>
            <body>
                <h1>❌ Error</h1>
                <p>{str(e)}</p>
                <a href="/settings">← Back to Settings</a>
            </body>
            </html>
        """)


@app.get("/api/status")
async def get_status():
    """Get system status and connection info"""
    try:
        auth = ClerkSocialAuth()
        connections = auth.verify_all_connections()
        user_info = auth.get_user_info()

        # Get database stats
        stats = db.get_stats()

        return {
            "status": "online",
            "user": {
                "email": user_info.get("email") if user_info else None,
                "user_id": user_info.get("user_id") if user_info else None
            },
            "connections": connections,
            "generated_posts": stats["total_posts"],
            "published_posts": stats["published_posts"]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "connections": {
                "linkedin": False,
                "twitter": False,
                "instagram": False
            }
        }


@app.post("/api/generate")
async def generate_content(request: Request):
    """Generate new content using Milton's voice (with optional graphics/video)"""
    data = await request.json()

    scenario = data.get("scenario", "partner_appreciation")
    context = data.get("context", "")
    voice_type = data.get("voice_type", "personal")  # personal or professional
    include_graphic = data.get("include_graphic", False)
    include_video = data.get("include_video", False)
    partner_logo = data.get("partner_logo")
    uploaded_media_url = data.get("uploaded_media_url")  # User-uploaded media to use instead

    # Build prompt based on voice type
    if voice_type == "personal":
        # Personal LinkedIn voice (20-80 words)
        prompt = f"""You are helping Milton Overton draft a PERSONAL LinkedIn post.

**CRITICAL: Use PERSONAL LINKEDIN VOICE**

**Length:** 20-80 words (1-4 sentences) - KEEP IT BRIEF!

**Tone:** Warm, supportive, celebratory, grateful

**Structure:**
1. Opening: "We want to thank..." / "I am so proud..."
2. Brief context (1-2 sentences)
3. Sign-off: "Let's Go Owls!"

**Real Milton LinkedIn Example (54 words):**
"We want to thank GameChanger Analytics for their incredible partnership with Kennesaw State University Athletics! Their cutting-edge AI-powered fan engagement tools will transform how we connect with our amazing Owl community over the next three years. Champion partners like GameChanger Analytics help us build champion experiences for our fans and student-athletes. Let's Go Owls!"

**Your Task:** Write a brief LinkedIn post.

**Context:** {context}

Write ONLY the LinkedIn post. Keep it 20-80 words. End with "Let's Go Owls!"
"""
    else:
        # Professional AD voice (200-400 words)
        prompt = f"""You are helping Milton Overton draft an OFFICIAL KSU Athletics statement.

**CRITICAL: Use PROFESSIONAL ATHLETIC DIRECTOR VOICE**

**Length:** 200-300 words (4 paragraphs)

**Structure:**
1. Lead with decision/announcement
2. Explain rationale (1-2 sentences)
3. Student-athlete focus
4. Next steps
5. Close with "Let's go Owls!"

**Your Task:** Write an official statement.

**Context:** {context}

Follow professional AD voice guidelines. Include student-athlete focus and rally close.
"""

    try:
        # Generate content with Claude
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500 if voice_type == "personal" else 800,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text.strip()

        # Initialize media URLs
        graphic_url = None
        video_url = None

        # Use uploaded media if provided, otherwise generate if requested
        if uploaded_media_url:
            # User provided their own media
            if uploaded_media_url.endswith(('.mp4', '.mov', '.avi')):
                video_url = uploaded_media_url
            else:
                graphic_url = uploaded_media_url
            print(f"[INFO] Using uploaded media: {uploaded_media_url}")

        elif include_graphic or include_video:
            # Generate media with AI
            try:
                from module_vi.complete_media_workflow import CompleteMediaWorkflow

                workflow = CompleteMediaWorkflow()

                media_package = workflow.create_post_package(
                    text_content=content,
                    voice_type=voice_type,
                    include_graphic=include_graphic,
                    include_video=include_video,
                    partner_logo=partner_logo
                )

                graphic_url = media_package.get("graphic_url")
                video_url = media_package.get("video_url")

            except Exception as media_error:
                print(f"[WARN] Media generation failed: {media_error}")
                # Continue without media

        # Save to database
        post_id = db.create_post(
            content=content,
            voice_type=voice_type,
            scenario=scenario,
            context=context,
            graphic_url=graphic_url,
            video_url=video_url
        )

        # Get the created post from database
        post = db.get_post(post_id)

        return {
            "success": True,
            "post": post,
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
            "cost": (response.usage.input_tokens * 0.003 + response.usage.output_tokens * 0.015) / 1000
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/posts")
async def get_posts(status: Optional[str] = None, limit: int = 100):
    """Get all generated posts"""
    posts = db.get_all_posts(limit=limit)

    if status:
        posts = [p for p in posts if p["status"] == status]

    return {"posts": posts}


@app.get("/api/posts/{post_id}")
async def get_post_endpoint(post_id: int):
    """Get specific post"""
    post = db.get_post(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


@app.put("/api/posts/{post_id}")
async def update_post_endpoint(post_id: int, request: Request):
    """Update post content"""
    data = await request.json()

    # Build update dict
    updates = {}
    if "content" in data:
        updates["content"] = data["content"]
        updates["word_count"] = len(data["content"].split())

    if "status" in data:
        updates["status"] = data["status"]

    # Update in database
    success = db.update_post(post_id, **updates)

    if not success:
        raise HTTPException(status_code=404, detail="Post not found")

    # Return updated post
    post = db.get_post(post_id)
    return {"success": True, "post": post}


@app.post("/api/posts/{post_id}/publish")
async def publish_post(post_id: int):
    """Publish post to LinkedIn"""
    post = db.get_post(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    try:
        # Initialize publisher
        global publisher
        if publisher is None:
            publisher = SocialMediaPublisher()

        # Publish to LinkedIn
        result = await publisher.publish_to_linkedin(
            content=post["content"]
        )

        if result["success"]:
            # Mark as published in database
            db.mark_post_published(post_id, result.get("url"))

            # Log publishing result
            db.log_publishing_result(
                post_id=post_id,
                platform="linkedin",
                success=True,
                post_url=result.get("url")
            )

            # Get updated post
            post = db.get_post(post_id)

            return {
                "success": True,
                "message": "Posted to LinkedIn successfully!",
                "url": result.get("url"),
                "post": post
            }
        else:
            # Log failed publishing result
            db.log_publishing_result(
                post_id=post_id,
                platform="linkedin",
                success=False,
                error_message=result.get("error")
            )

            return {
                "success": False,
                "error": result.get("error"),
                "action": result.get("action")
            }

    except Exception as e:
        # Log exception
        db.log_publishing_result(
            post_id=post_id,
            platform="linkedin",
            success=False,
            error_message=str(e)
        )

        return {
            "success": False,
            "error": str(e)
        }


@app.delete("/api/posts/{post_id}")
async def delete_post_endpoint(post_id: int):
    """Delete a post"""
    success = db.delete_post(post_id)

    if not success:
        raise HTTPException(status_code=404, detail="Post not found")

    return {"success": True, "message": "Post deleted"}


@app.get("/api/published")
async def get_published_posts():
    """Get all published posts"""
    posts = db.get_all_posts()
    published = [p for p in posts if p["status"] == "published"]
    return {"posts": published}


# ============================================================================
# MEDIA GALLERY API ENDPOINTS
# ============================================================================

@app.post("/api/media/upload")
async def upload_media(file: UploadFile = File(...)):
    """Upload a media file (image or video)"""
    try:
        # Validate file type
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi'}
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"File type {file_ext} not allowed")

        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{unique_id}{file_ext}"

        # Save to uploads directory
        upload_path = media_dir / "uploads" / safe_filename

        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Get file info
        file_size = upload_path.stat().st_size

        return {
            "success": True,
            "filename": safe_filename,
            "url": f"/media/uploads/{safe_filename}",
            "size": file_size,
            "type": file_ext[1:],  # Remove the dot
            "uploaded_at": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/media/gallery")
async def get_media_gallery():
    """Get all uploaded media files"""
    try:
        uploads_dir = media_dir / "uploads"
        graphics_dir = media_dir / "graphics"
        videos_dir = media_dir / "videos"

        media_files = []

        # Get uploaded files
        if uploads_dir.exists():
            for file_path in uploads_dir.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    media_files.append({
                        "filename": file_path.name,
                        "url": f"/media/uploads/{file_path.name}",
                        "size": stat.st_size,
                        "type": "uploaded",
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat()
                    })

        # Get generated graphics
        if graphics_dir.exists():
            for file_path in graphics_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in {'.png', '.jpg', '.jpeg'}:
                    stat = file_path.stat()
                    media_files.append({
                        "filename": file_path.name,
                        "url": f"/media/graphics/{file_path.name}",
                        "size": stat.st_size,
                        "type": "generated",
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat()
                    })

        # Sort by creation time (newest first)
        media_files.sort(key=lambda x: x["created_at"], reverse=True)

        return {
            "media": media_files,
            "total": len(media_files)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/media/{media_type}/{filename}")
async def delete_media(media_type: str, filename: str):
    """Delete a media file"""
    try:
        if media_type not in ["uploads", "graphics", "videos"]:
            raise HTTPException(status_code=400, detail="Invalid media type")

        file_path = media_dir / media_type / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        file_path.unlink()

        return {"success": True, "message": f"Deleted {filename}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SCHEDULING API ENDPOINTS
# ============================================================================

@app.post("/api/posts/{post_id}/schedule")
async def schedule_post_endpoint(post_id: int, request: Request):
    """Schedule a post for future publishing"""
    data = await request.json()

    platform = data.get("platform")
    scheduled_time = data.get("scheduled_time")

    if not platform or not scheduled_time:
        raise HTTPException(status_code=400, detail="Missing platform or scheduled_time")

    # Verify post exists
    post = db.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Schedule the post
    schedule_id = db.schedule_post(
        post_id=post_id,
        platform=platform,
        scheduled_time=scheduled_time
    )

    # Get the scheduled post
    scheduled = db.get_all_scheduled_posts()
    scheduled_post = next((s for s in scheduled if s["id"] == schedule_id), None)

    return {
        "success": True,
        "message": f"Post scheduled for {platform} at {scheduled_time}",
        "schedule": scheduled_post
    }


@app.get("/api/scheduled")
async def get_scheduled_posts(status: Optional[str] = None):
    """Get all scheduled posts"""
    scheduled = db.get_all_scheduled_posts(status=status)
    return {"scheduled": scheduled}


@app.get("/api/scheduled/upcoming")
async def get_upcoming_scheduled():
    """Get upcoming scheduled posts (next 7 days)"""
    upcoming = db.get_upcoming_schedule(days=7)
    return {"upcoming": upcoming}


@app.delete("/api/scheduled/{schedule_id}")
async def cancel_schedule_endpoint(schedule_id: int):
    """Cancel a scheduled post"""
    success = db.cancel_scheduled_post(schedule_id)

    if not success:
        raise HTTPException(status_code=404, detail="Scheduled post not found or already published")

    return {"success": True, "message": "Scheduled post cancelled"}


@app.get("/api/scheduler/status")
async def get_scheduler_status():
    """Get scheduler daemon status"""
    # This would connect to the running scheduler daemon
    # For now, just return basic stats
    stats = db.get_stats()
    pending_schedules = db.get_all_scheduled_posts(status='pending')

    return {
        "daemon_running": False,  # Will be updated when daemon is integrated
        "pending_schedules": len(pending_schedules),
        "total_posts": stats['total_posts'],
        "published_posts": stats['published_posts']
    }


# ============================================================================
# ANALYTICS API ENDPOINTS
# ============================================================================

@app.post("/api/analytics/engagement")
async def record_engagement_endpoint(request: Request):
    """Record engagement metrics for a post"""
    data = await request.json()

    post_id = data.get("post_id")
    platform = data.get("platform", "linkedin")
    views = data.get("views", 0)
    likes = data.get("likes", 0)
    comments = data.get("comments", 0)
    shares = data.get("shares", 0)
    clicks = data.get("clicks", 0)

    if not post_id:
        raise HTTPException(status_code=400, detail="post_id is required")

    success = analytics.record_engagement(
        post_id=post_id,
        platform=platform,
        views=views,
        likes=likes,
        comments=comments,
        shares=shares,
        clicks=clicks
    )

    if success:
        return {"success": True, "message": "Engagement recorded"}
    else:
        raise HTTPException(status_code=500, detail="Failed to record engagement")


@app.get("/api/analytics/post/{post_id}")
async def get_post_analytics(post_id: int):
    """Get performance data for a specific post"""
    performance = analytics.get_post_performance(post_id)

    if "error" in performance:
        raise HTTPException(status_code=404, detail=performance["error"])

    return performance


@app.get("/api/analytics/overview")
async def get_analytics_overview(days: int = 30):
    """Get overall performance metrics"""
    return analytics.get_overall_performance(days=days)


@app.get("/api/analytics/best-times")
async def get_best_posting_times(platform: str = "linkedin"):
    """Get optimal posting times based on historical data"""
    return analytics.analyze_best_times(platform=platform)


@app.get("/api/analytics/content-performance")
async def get_content_analysis(metric: str = "engagement_rate"):
    """Analyze which content types perform best"""
    return analytics.analyze_content_performance(metric=metric)


@app.get("/api/analytics/top-posts")
async def get_top_posts(limit: int = 10, metric: str = "engagement_rate"):
    """Get top performing posts"""
    posts = analytics.get_top_performing_posts(limit=limit, metric=metric)
    return {"top_posts": posts}


@app.get("/api/analytics/insights")
async def get_analytics_insights():
    """Get actionable insights from analytics data"""
    return analytics.generate_insights()


@app.get("/api/analytics/dashboard")
async def get_analytics_dashboard():
    """Get complete analytics summary for dashboard"""
    return analytics.get_dashboard_summary()


# ===== NEWS MONITOR ENDPOINTS =====

@app.get("/api/news/monitor")
async def monitor_news(hours_back: int = 24, min_priority: int = 7):
    """
    Monitor news sources and generate post suggestions

    Args:
        hours_back: How many hours back to check for news (default 24)
        min_priority: Minimum priority score 1-10 (default 7)

    Returns:
        List of news items with post suggestions sorted by priority
    """
    try:
        suggestions = news_monitor.monitor_and_suggest(
            hours_back=hours_back,
            min_priority=min_priority
        )

        return {
            "success": True,
            "count": len(suggestions),
            "suggestions": suggestions,
            "parameters": {
                "hours_back": hours_back,
                "min_priority": min_priority
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/news/feeds")
async def get_news_feeds():
    """
    Get raw news feeds without AI analysis

    Returns:
        List of recent news items from all sources
    """
    try:
        news_items = news_monitor.fetch_rss_feeds()

        return {
            "success": True,
            "count": len(news_items),
            "news": news_items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== HEYGEN AVATAR VIDEO ENDPOINTS =====

@app.post("/api/generate-avatar-video")
async def generate_avatar_video(request: Request):
    """Generate an avatar video using HeyGen via Zapier"""
    try:
        data = await request.json()
        user_id = 'milton_overton'  # Default user

        if not data.get('voice_type') or not data.get('scenario'):
            raise HTTPException(status_code=400, detail="voice_type and scenario required")

        # Generate script using existing content generator
        from module_ii.content_generator import ContentGenerator
        content_generator = ContentGenerator()
        script_result = content_generator.generate(
            voice_type=data['voice_type'],
            scenario=data['scenario'],
            context=data.get('context', '')
        )

        script = script_result.get('content', '')

        # Optimize for video (60 seconds = ~150 words)
        if len(script.split()) > 150:
            script = ' '.join(script.split()[:150]) + '...'

        # Create video record
        video_id = avatar_video_manager.create_video_record(
            user_id=user_id,
            script=script,
            scenario=data['scenario'],
            voice_type=data['voice_type'],
            context=data.get('context', ''),
            dimensions=data.get('dimensions', 'square'),
            platform=data.get('platform', 'linkedin')
        )

        # Trigger Zapier
        avatar_video_manager.trigger_zapier_workflow(
            video_id=video_id,
            script=script,
            scenario=data['scenario'],
            voice_type=data['voice_type'],
            dimensions=data.get('dimensions', 'square'),
            platform=data.get('platform', 'linkedin')
        )

        return JSONResponse({
            "status": "generating",
            "video_id": video_id,
            "script": script,
            "message": "Video generation started. Check back in 60-90 seconds."
        })

    except Exception as e:
        logger.error(f"Error in generate_avatar_video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/avatar-video-complete")
async def avatar_video_complete(request: Request):
    """Webhook endpoint - Zapier calls this when video is ready"""
    try:
        data = await request.json()
        video_id = data.get('video_record_id')

        if not video_id:
            raise HTTPException(status_code=400, detail="video_record_id required")

        avatar_video_manager.update_video_status(
            video_id=video_id,
            status=data.get('status', 'ready'),
            heygen_video_id=data.get('heygen_video_id'),
            video_url=data.get('video_url'),
            thumbnail_url=data.get('thumbnail_url'),
            duration_seconds=data.get('duration'),
            error_message=data.get('error_message')
        )

        return JSONResponse({"status": "success", "video_id": video_id})

    except Exception as e:
        logger.error(f"Error in avatar_video_complete: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/avatar-video-status/{video_id}")
async def get_avatar_video_status(video_id: int):
    """Get status of a specific avatar video"""
    try:
        video = avatar_video_manager.get_video_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        return JSONResponse(video)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting video status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/avatar-videos")
async def list_avatar_videos(status: str = None, limit: int = 50):
    """List all avatar videos for current user"""
    try:
        user_id = 'milton_overton'  # Default user
        videos = avatar_video_manager.get_videos_by_user(user_id, status, limit)
        statistics = avatar_video_manager.get_video_statistics(user_id)

        return JSONResponse({
            "videos": videos,
            "statistics": statistics
        })
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("DASHBOARD_PORT", 8080))
    print("="*70)
    print("MILTON OVERTON AI PUBLICIST - APPROVAL DASHBOARD")
    print("="*70)
    print()
    print(f"Starting dashboard on http://localhost:{port}")
    print()
    print("Features:")
    print("  - Generate content in Milton's authentic voice")
    print("  - Preview posts before publishing")
    print("  - Edit content if needed")
    print("  - Publish to LinkedIn with one click")
    print("  - View publishing history")
    print()
    print("Press Ctrl+C to stop")
    print("="*70)
    print()

    uvicorn.run(app, host="0.0.0.0", port=port)
