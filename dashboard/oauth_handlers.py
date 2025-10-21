"""
OAuth Callback Handlers
Handles OAuth callbacks from social media platforms via Clerk
"""

from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
import os
from typing import Optional
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from security.oauth_manager import OAuthManager
from datetime import datetime, timedelta

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.get("/status")
async def oauth_status():
    """
    Get OAuth configuration status for all platforms

    Returns:
        Dictionary with platform connection status
    """
    manager = OAuthManager()

    platform_status = manager.get_platform_status()
    configured_platforms = manager.get_configured_platforms()

    is_valid, issues = manager.validate_configuration()

    return {
        "success": True,
        "platforms": platform_status,
        "configured_platforms": configured_platforms,
        "is_valid": is_valid,
        "issues": issues,
        "clerk_configured": manager.config.get("clerk_config", {}).get("configured", False)
    }


@router.get("/callback/{platform}")
async def oauth_callback(
    platform: str,
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None)
):
    """
    Handle OAuth callback from social media platforms

    Args:
        platform: Platform name (linkedin, twitter, instagram, facebook)
        code: Authorization code
        state: State parameter for CSRF protection
        error: Error code if OAuth failed
        error_description: Human-readable error description

    Returns:
        Redirect to dashboard with status
    """
    # Handle OAuth errors
    if error:
        return RedirectResponse(
            url=f"/?oauth_error={error}&platform={platform}&message={error_description or 'OAuth failed'}",
            status_code=302
        )

    if not code:
        return RedirectResponse(
            url=f"/?oauth_error=missing_code&platform={platform}",
            status_code=302
        )

    # In production, exchange code for tokens via Clerk
    # For now, we'll simulate successful OAuth
    manager = OAuthManager()

    try:
        # This would normally exchange the code for tokens via Clerk API
        # For MVP, we'll mark the platform as connected pending full Clerk integration

        # Calculate token expiration (60 days for most platforms)
        expires_at = (datetime.now() + timedelta(days=60)).isoformat()

        manager.add_platform(
            platform=platform,
            access_token=f"mock_token_{platform}_{code[:10]}",  # Placeholder
            refresh_token=f"mock_refresh_{platform}",
            token_expires_at=expires_at,
            oauth_code=code,
            oauth_state=state,
            connected_via="clerk_pending_exchange"
        )

        return RedirectResponse(
            url=f"/?oauth_success=true&platform={platform}",
            status_code=302
        )

    except Exception as e:
        return RedirectResponse(
            url=f"/?oauth_error=server_error&platform={platform}&message={str(e)}",
            status_code=302
        )


@router.post("/connect/{platform}")
async def initiate_oauth(platform: str):
    """
    Initiate OAuth flow for a platform

    Args:
        platform: Platform name

    Returns:
        OAuth authorization URL
    """
    manager = OAuthManager()

    # Check if Clerk is configured
    clerk_config = manager.config.get("clerk_config", {})
    if not clerk_config.get("configured"):
        raise HTTPException(
            status_code=400,
            detail="Clerk authentication not configured. Please configure Clerk first."
        )

    # Get setup instructions for the platform
    instructions = manager.get_setup_instructions(platform)

    if not instructions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported platform: {platform}"
        )

    # In production, this would generate a Clerk OAuth URL
    # For now, return setup instructions
    return {
        "success": True,
        "platform": platform,
        "message": "OAuth not fully configured. Please complete Clerk setup.",
        "instructions": instructions,
        "clerk_dashboard_url": "https://dashboard.clerk.com/"
    }


@router.delete("/disconnect/{platform}")
async def disconnect_platform(platform: str):
    """
    Disconnect a social media platform

    Args:
        platform: Platform name

    Returns:
        Success status
    """
    manager = OAuthManager()

    success = manager.remove_platform(platform)

    if success:
        return {
            "success": True,
            "message": f"{platform.capitalize()} disconnected successfully"
        }
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Platform {platform} not found or not connected"
        )


@router.get("/setup/{platform}")
async def get_platform_setup(platform: str):
    """
    Get setup instructions for a platform

    Args:
        platform: Platform name

    Returns:
        Setup instructions
    """
    manager = OAuthManager()
    instructions = manager.get_setup_instructions(platform)

    if not instructions:
        raise HTTPException(
            status_code=404,
            detail=f"Platform {platform} not found"
        )

    return {
        "success": True,
        "platform": platform,
        "instructions": instructions
    }


@router.post("/configure/clerk")
async def configure_clerk(
    secret_key: str,
    user_id: str
):
    """
    Configure Clerk authentication

    Args:
        secret_key: Clerk secret key
        user_id: Milton's user ID in Clerk

    Returns:
        Success status
    """
    manager = OAuthManager()

    # Validate keys
    if not secret_key.startswith("sk_test_") and not secret_key.startswith("sk_live_"):
        raise HTTPException(
            status_code=400,
            detail="Invalid Clerk secret key format"
        )

    if not user_id.startswith("user_"):
        raise HTTPException(
            status_code=400,
            detail="Invalid user ID format"
        )

    success = manager.configure_clerk(secret_key, user_id)

    if success:
        return {
            "success": True,
            "message": "Clerk configured successfully",
            "next_steps": [
                "Configure social connections in Clerk dashboard",
                "Return to this dashboard and connect platforms"
            ]
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to configure Clerk"
        )


@router.get("/health")
async def oauth_health_check():
    """
    Comprehensive OAuth health check

    Returns:
        Health status for all OAuth components
    """
    manager = OAuthManager()

    # Check Clerk configuration
    clerk_config = manager.config.get("clerk_config", {})
    clerk_healthy = clerk_config.get("configured", False)

    # Check platform connections
    platform_status = manager.get_platform_status()
    connected_count = sum(1 for status in platform_status.values() if status)

    # Validate configuration
    is_valid, issues = manager.validate_configuration()

    # Check token expiration
    expiring_soon = []
    for platform, config in manager.config.get("platforms", {}).items():
        if config.get("configured"):
            expires_at = config.get("token_expires_at")
            if expires_at:
                expiry = datetime.fromisoformat(expires_at)
                days_until_expiry = (expiry - datetime.now()).days

                if days_until_expiry < 7:
                    expiring_soon.append({
                        "platform": platform,
                        "days_remaining": days_until_expiry
                    })

    overall_health = "healthy" if is_valid and clerk_healthy else "degraded" if connected_count > 0 else "unhealthy"

    return {
        "success": True,
        "overall_health": overall_health,
        "clerk": {
            "configured": clerk_healthy,
            "has_secret_key": bool(clerk_config.get("secret_key")),
            "has_user_id": bool(clerk_config.get("user_id"))
        },
        "platforms": {
            "total": len(platform_status),
            "connected": connected_count,
            "status": platform_status
        },
        "validation": {
            "is_valid": is_valid,
            "issues": issues
        },
        "token_health": {
            "expiring_soon": expiring_soon,
            "count_expiring": len(expiring_soon)
        }
    }


# HTML response for OAuth success/error pages
@router.get("/success", response_class=HTMLResponse)
async def oauth_success_page(platform: str = Query(...)):
    """OAuth success page"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OAuth Success</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}
            .container {{
                background: white;
                padding: 3rem;
                border-radius: 10px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
                max-width: 500px;
            }}
            .icon {{
                font-size: 64px;
                margin-bottom: 1rem;
            }}
            h1 {{
                color: #2d3748;
                margin-bottom: 1rem;
            }}
            p {{
                color: #718096;
                margin-bottom: 2rem;
            }}
            .button {{
                background: #667eea;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                text-decoration: none;
                display: inline-block;
                transition: background 0.2s;
            }}
            .button:hover {{
                background: #5568d3;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">✓</div>
            <h1>Successfully Connected!</h1>
            <p>Your {platform.capitalize()} account has been connected to Milton AI Publicist.</p>
            <a href="/" class="button">Return to Dashboard</a>
        </div>
        <script>
            // Auto-redirect after 3 seconds
            setTimeout(() => {{
                window.location.href = "/?oauth_success=true&platform={platform}";
            }}, 3000);
        </script>
    </body>
    </html>
    """


@router.get("/error", response_class=HTMLResponse)
async def oauth_error_page(
    platform: str = Query(...),
    error: str = Query("unknown_error"),
    message: str = Query("An error occurred during OAuth")
):
    """OAuth error page"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OAuth Error</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            }}
            .container {{
                background: white;
                padding: 3rem;
                border-radius: 10px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
                max-width: 500px;
            }}
            .icon {{
                font-size: 64px;
                margin-bottom: 1rem;
            }}
            h1 {{
                color: #2d3748;
                margin-bottom: 1rem;
            }}
            p {{
                color: #718096;
                margin-bottom: 1rem;
            }}
            .error-details {{
                background: #fff5f5;
                border: 1px solid #feb2b2;
                color: #c53030;
                padding: 1rem;
                border-radius: 6px;
                margin-bottom: 2rem;
                font-size: 0.9rem;
            }}
            .button {{
                background: #667eea;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                text-decoration: none;
                display: inline-block;
                transition: background 0.2s;
                margin: 0 0.5rem;
            }}
            .button:hover {{
                background: #5568d3;
            }}
            .button-secondary {{
                background: #718096;
            }}
            .button-secondary:hover {{
                background: #4a5568;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">✗</div>
            <h1>Connection Failed</h1>
            <p>We couldn't connect your {platform.capitalize()} account.</p>
            <div class="error-details">
                <strong>Error:</strong> {error}<br>
                <strong>Details:</strong> {message}
            </div>
            <a href="/oauth/setup/{platform}" class="button">View Setup Instructions</a>
            <a href="/" class="button button-secondary">Return to Dashboard</a>
        </div>
    </body>
    </html>
    """
