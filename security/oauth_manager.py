"""
OAuth Configuration Manager
Handles OAuth setup, token management, and social media authentication
"""

import os
import json
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class OAuthManager:
    """
    Manages OAuth configuration and tokens for social media platforms
    """

    SUPPORTED_PLATFORMS = ['linkedin', 'twitter', 'instagram', 'facebook']

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize OAuth manager

        Args:
            config_file: Path to OAuth config file
        """
        if config_file is None:
            config_file = Path(__file__).parent.parent / ".oauth_config.json"

        self.config_file = Path(config_file)
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load OAuth configuration from file"""
        if not self.config_file.exists():
            return {
                "platforms": {},
                "clerk_config": {
                    "secret_key": os.getenv("CLERK_SECRET_KEY", ""),
                    "user_id": os.getenv("MILTON_USER_ID", ""),
                    "configured": False
                },
                "last_updated": None
            }

        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load OAuth config: {e}")
            return {"platforms": {}, "clerk_config": {}, "last_updated": None}

    def _save_config(self) -> None:
        """Save OAuth configuration to file"""
        self.config["last_updated"] = datetime.now().isoformat()

        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def configure_clerk(self, secret_key: str, user_id: str) -> bool:
        """
        Configure Clerk authentication

        Args:
            secret_key: Clerk secret key
            user_id: User ID

        Returns:
            True if successful
        """
        try:
            self.config["clerk_config"] = {
                "secret_key": secret_key,
                "user_id": user_id,
                "configured": True,
                "configured_at": datetime.now().isoformat()
            }
            self._save_config()

            # Update .env file
            self._update_env_var("CLERK_SECRET_KEY", secret_key)
            self._update_env_var("MILTON_USER_ID", user_id)

            return True
        except Exception as e:
            print(f"Error configuring Clerk: {e}")
            return False

    def add_platform(
        self,
        platform: str,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        token_expires_at: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Add or update OAuth configuration for a platform

        Args:
            platform: Platform name (linkedin, twitter, instagram, facebook)
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            token_expires_at: Token expiration timestamp
            **kwargs: Additional platform-specific configuration

        Returns:
            True if successful
        """
        if platform not in self.SUPPORTED_PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}")

        self.config["platforms"][platform] = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_expires_at": token_expires_at,
            "configured": bool(access_token),
            "configured_at": datetime.now().isoformat() if access_token else None,
            **kwargs
        }

        self._save_config()
        return True

    def get_platform_config(self, platform: str) -> Optional[Dict]:
        """
        Get OAuth configuration for a platform

        Args:
            platform: Platform name

        Returns:
            Platform configuration or None
        """
        return self.config["platforms"].get(platform)

    def is_platform_configured(self, platform: str) -> bool:
        """
        Check if a platform is configured

        Args:
            platform: Platform name

        Returns:
            True if configured
        """
        config = self.get_platform_config(platform)
        return config is not None and config.get("configured", False)

    def get_access_token(self, platform: str) -> Optional[str]:
        """
        Get access token for a platform

        Args:
            platform: Platform name

        Returns:
            Access token or None
        """
        config = self.get_platform_config(platform)
        if not config:
            return None

        # Check if token is expired
        expires_at = config.get("token_expires_at")
        if expires_at:
            expiry = datetime.fromisoformat(expires_at)
            if datetime.now() >= expiry:
                print(f"Warning: Access token for {platform} has expired")
                return None

        return config.get("access_token")

    def refresh_platform_token(self, platform: str) -> bool:
        """
        Refresh access token for a platform

        Args:
            platform: Platform name

        Returns:
            True if successful
        """
        # This would integrate with Clerk or platform-specific refresh logic
        # For now, return False (to be implemented)
        print(f"Token refresh for {platform} not yet implemented")
        return False

    def remove_platform(self, platform: str) -> bool:
        """
        Remove OAuth configuration for a platform

        Args:
            platform: Platform name

        Returns:
            True if successful
        """
        if platform in self.config["platforms"]:
            del self.config["platforms"][platform]
            self._save_config()
            return True
        return False

    def get_configured_platforms(self) -> List[str]:
        """
        Get list of configured platforms

        Returns:
            List of platform names
        """
        return [
            platform
            for platform, config in self.config["platforms"].items()
            if config.get("configured", False)
        ]

    def get_platform_status(self) -> Dict[str, bool]:
        """
        Get configuration status for all platforms

        Returns:
            Dictionary of platform: configured status
        """
        status = {}
        for platform in self.SUPPORTED_PLATFORMS:
            status[platform] = self.is_platform_configured(platform)
        return status

    def validate_configuration(self) -> Tuple[bool, List[str]]:
        """
        Validate OAuth configuration

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []

        # Check Clerk configuration
        clerk_config = self.config.get("clerk_config", {})
        if not clerk_config.get("configured"):
            issues.append("Clerk authentication not configured")

        if not clerk_config.get("secret_key"):
            issues.append("Clerk secret key missing")

        if not clerk_config.get("user_id"):
            issues.append("Milton user ID missing")

        # Check if at least one platform is configured
        configured_platforms = self.get_configured_platforms()
        if not configured_platforms:
            issues.append("No social media platforms configured")

        # Check token expiration
        for platform, config in self.config["platforms"].items():
            if config.get("configured"):
                expires_at = config.get("token_expires_at")
                if expires_at:
                    expiry = datetime.fromisoformat(expires_at)
                    if datetime.now() >= expiry:
                        issues.append(f"{platform.capitalize()} access token has expired")

        return len(issues) == 0, issues

    def get_setup_instructions(self, platform: str) -> Dict:
        """
        Get setup instructions for a platform

        Args:
            platform: Platform name

        Returns:
            Dictionary with setup instructions
        """
        instructions = {
            "linkedin": {
                "steps": [
                    "Go to https://www.linkedin.com/developers/",
                    "Create a new app or select existing",
                    "Add OAuth 2.0 redirect URL: http://localhost:8080/oauth/callback/linkedin",
                    "Enable 'Share on LinkedIn' and 'Sign In with LinkedIn' products",
                    "Copy Client ID and Client Secret",
                    "Add to Clerk dashboard: https://dashboard.clerk.com/",
                    "Navigate to 'Social Connections' → 'LinkedIn'",
                    "Paste Client ID and Client Secret",
                    "Save and enable LinkedIn",
                    "Return to dashboard and click 'Connect LinkedIn'"
                ],
                "redirect_url": "http://localhost:8080/oauth/callback/linkedin",
                "scopes": ["r_liteprofile", "r_emailaddress", "w_member_social"],
                "docs": "https://docs.microsoft.com/en-us/linkedin/shared/authentication/authentication"
            },
            "twitter": {
                "steps": [
                    "Go to https://developer.twitter.com/",
                    "Create a new app or select existing",
                    "Enable OAuth 2.0",
                    "Add callback URL: http://localhost:8080/oauth/callback/twitter",
                    "Copy API Key and API Secret",
                    "Add to Clerk dashboard",
                    "Enable required permissions: Read and Write",
                    "Return to dashboard and connect"
                ],
                "redirect_url": "http://localhost:8080/oauth/callback/twitter",
                "scopes": ["tweet.read", "tweet.write", "users.read"],
                "docs": "https://developer.twitter.com/en/docs/authentication/oauth-2-0"
            },
            "instagram": {
                "steps": [
                    "Go to https://developers.facebook.com/",
                    "Create or select Facebook app",
                    "Add Instagram Graph API product",
                    "Configure OAuth redirect: http://localhost:8080/oauth/callback/instagram",
                    "Request instagram_basic, instagram_content_publish permissions",
                    "Add to Clerk dashboard",
                    "Connect Instagram Business account"
                ],
                "redirect_url": "http://localhost:8080/oauth/callback/instagram",
                "scopes": ["instagram_basic", "instagram_content_publish"],
                "docs": "https://developers.facebook.com/docs/instagram-api"
            },
            "facebook": {
                "steps": [
                    "Go to https://developers.facebook.com/",
                    "Create or select app",
                    "Add Facebook Login product",
                    "Configure OAuth redirect: http://localhost:8080/oauth/callback/facebook",
                    "Request pages_manage_posts, pages_read_engagement permissions",
                    "Add to Clerk dashboard",
                    "Connect Facebook Page"
                ],
                "redirect_url": "http://localhost:8080/oauth/callback/facebook",
                "scopes": ["pages_manage_posts", "pages_read_engagement"],
                "docs": "https://developers.facebook.com/docs/facebook-login"
            }
        }

        return instructions.get(platform, {})

    def export_config(self) -> Dict:
        """
        Export OAuth configuration (without sensitive data)

        Returns:
            Sanitized configuration
        """
        export = {
            "platforms": {},
            "clerk_configured": self.config.get("clerk_config", {}).get("configured", False),
            "last_updated": self.config.get("last_updated")
        }

        for platform, config in self.config["platforms"].items():
            export["platforms"][platform] = {
                "configured": config.get("configured", False),
                "configured_at": config.get("configured_at"),
                "token_expires_at": config.get("token_expires_at")
            }

        return export

    def _update_env_var(self, key: str, value: str) -> None:
        """Update environment variable in .env file"""
        env_path = Path(__file__).parent.parent / '.env'

        if not env_path.exists():
            return

        with open(env_path, 'r') as f:
            lines = f.readlines()

        updated = False
        new_lines = []

        for line in lines:
            if line.startswith(f"{key}="):
                new_lines.append(f"{key}={value}\n")
                updated = True
            else:
                new_lines.append(line)

        if not updated:
            new_lines.append(f"\n{key}={value}\n")

        with open(env_path, 'w') as f:
            f.writelines(new_lines)


# Convenience functions

def get_oauth_manager() -> OAuthManager:
    """Get singleton OAuth manager instance"""
    if not hasattr(get_oauth_manager, '_instance'):
        get_oauth_manager._instance = OAuthManager()
    return get_oauth_manager._instance


def is_oauth_configured() -> bool:
    """Check if OAuth is configured"""
    manager = get_oauth_manager()
    is_valid, _ = manager.validate_configuration()
    return is_valid


def get_configured_platforms() -> List[str]:
    """Get list of configured platforms"""
    manager = get_oauth_manager()
    return manager.get_configured_platforms()


if __name__ == "__main__":
    # Demo/testing
    print("=" * 60)
    print("OAUTH CONFIGURATION MANAGER")
    print("=" * 60)

    manager = OAuthManager()

    print("\nCurrent Configuration:")
    print(f"  Clerk Configured: {manager.config.get('clerk_config', {}).get('configured', False)}")

    print("\nPlatform Status:")
    status = manager.get_platform_status()
    for platform, configured in status.items():
        symbol = "[OK]" if configured else "[  ]"
        print(f"  {symbol} {platform.capitalize()}")

    print("\nValidation:")
    is_valid, issues = manager.validate_configuration()
    if is_valid:
        print("  [OK] Configuration valid")
    else:
        print("  [WARN] Configuration issues:")
        for issue in issues:
            print(f"    - {issue}")

    print("\n" + "=" * 60)
