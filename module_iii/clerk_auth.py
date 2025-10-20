"""
Clerk OAuth Authentication for Social Media Publishing
Secure, platform-approved OAuth 2.0 token management
"""

import os
from typing import Dict, Optional
from clerk_backend_api import Clerk


class ClerkSocialAuth:
    """
    Clerk-based OAuth authentication for social media platforms

    Benefits:
    - Secure token storage (encrypted in Clerk)
    - Automatic token refresh
    - Multi-account support
    - Centralized session management

    Supported Platforms:
    - LinkedIn (oauth_linkedin)
    - Twitter/X (oauth_twitter)
    - Instagram via Facebook (oauth_facebook)
    """

    def __init__(self, secret_key: Optional[str] = None, user_id: Optional[str] = None):
        """
        Initialize Clerk authentication

        Args:
            secret_key: Clerk secret key (defaults to CLERK_SECRET_KEY env var)
            user_id: Milton's Clerk user ID (defaults to MILTON_USER_ID env var)
        """
        self.secret_key = secret_key or os.getenv("CLERK_SECRET_KEY")
        self.user_id = user_id or os.getenv("MILTON_USER_ID")

        if not self.secret_key:
            raise ValueError("CLERK_SECRET_KEY not found in environment")

        if not self.user_id:
            raise ValueError(
                "MILTON_USER_ID not found in environment. "
                "Please sign in to Clerk and add your user ID to .env"
            )

        # Initialize Clerk client
        self.clerk = Clerk(bearer_auth=self.secret_key)

    def get_linkedin_access_token(self) -> Optional[str]:
        """
        Get LinkedIn OAuth access token for Milton

        Returns:
            Valid LinkedIn access token or None if not connected

        Raises:
            Exception if user not found or token retrieval fails
        """
        try:
            # Get Milton's user account from Clerk
            user = self.clerk.users.get(user_id=self.user_id)

            # Find LinkedIn OAuth account
            if user.external_accounts:
                for account in user.external_accounts:
                    if account.provider == "oauth_linkedin":
                        # Clerk automatically refreshes tokens if expired
                        if hasattr(account, 'access_token') and account.access_token:
                            return account.access_token

            return None

        except Exception as e:
            print(f"Error getting LinkedIn token: {e}")
            raise

    def get_twitter_access_token(self) -> Optional[str]:
        """
        Get Twitter/X OAuth access token for Milton

        Returns:
            Valid Twitter access token or None if not connected
        """
        try:
            user = self.clerk.users.get(user_id=self.user_id)

            if user.external_accounts:
                for account in user.external_accounts:
                    if account.provider == "oauth_twitter":
                        if hasattr(account, 'access_token') and account.access_token:
                            return account.access_token

            return None

        except Exception as e:
            print(f"Error getting Twitter token: {e}")
            raise

    def get_instagram_access_token(self) -> Optional[str]:
        """
        Get Instagram OAuth access token for Milton

        Note: Instagram uses Facebook OAuth

        Returns:
            Valid Instagram/Facebook access token or None if not connected
        """
        try:
            user = self.clerk.users.get(user_id=self.user_id)

            if user.external_accounts:
                for account in user.external_accounts:
                    if account.provider == "oauth_facebook":
                        # Instagram uses Facebook OAuth
                        if hasattr(account, 'access_token') and account.access_token:
                            return account.access_token

            return None

        except Exception as e:
            print(f"Error getting Instagram token: {e}")
            raise

    def verify_all_connections(self) -> Dict[str, bool]:
        """
        Verify all social media connections are active

        Returns:
            Dict of platform: connected status
            Example: {"linkedin": True, "twitter": False, "instagram": True}
        """
        connections = {
            "linkedin": False,
            "twitter": False,
            "instagram": False
        }

        try:
            connections["linkedin"] = self.get_linkedin_access_token() is not None
            connections["twitter"] = self.get_twitter_access_token() is not None
            connections["instagram"] = self.get_instagram_access_token() is not None

        except Exception as e:
            print(f"Error verifying connections: {e}")

        return connections

    def get_user_info(self) -> Optional[Dict]:
        """
        Get Milton's Clerk user information

        Returns:
            User info dict with email, name, connected accounts
        """
        try:
            user = self.clerk.users.get(user_id=self.user_id)

            email = None
            if user.email_addresses and len(user.email_addresses) > 0:
                email = user.email_addresses[0].email_address

            connected_accounts = []
            if user.external_accounts:
                for account in user.external_accounts:
                    connected_accounts.append({
                        "provider": account.provider,
                        "username": account.username if hasattr(account, 'username') else None,
                        "connected": hasattr(account, 'access_token') and account.access_token is not None
                    })

            return {
                "user_id": user.id,
                "email": email,
                "created_at": user.created_at,
                "connected_accounts": connected_accounts
            }

        except Exception as e:
            print(f"Error getting user info: {e}")
            return None

    def get_connect_url(self, platform: str, redirect_url: str) -> str:
        """
        Get OAuth connection URL for a platform

        Args:
            platform: "linkedin", "twitter", or "instagram"
            redirect_url: URL to redirect after OAuth completion

        Returns:
            OAuth authorization URL

        Note: This is typically handled by Clerk's pre-built UI
        """
        clerk_frontend_url = os.getenv("CLERK_FRONTEND_URL", "https://cool-fish-70.clerk.accounts.dev")
        return f"{clerk_frontend_url}/sign-in?redirect_url={redirect_url}"


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("="*70)
    print("CLERK OAUTH AUTHENTICATION TEST")
    print("="*70)
    print()

    try:
        auth = ClerkSocialAuth()
        print(f"[OK] Clerk auth initialized for user: {auth.user_id}")
        print()

        # Check connections
        print("[INFO] Checking social media connections...")
        connections = auth.verify_all_connections()

        for platform, connected in connections.items():
            status = "[CONNECTED]" if connected else "[NOT CONNECTED]"
            print(f"  {status} {platform.capitalize()}")

        print()

        # Get user info
        user_info = auth.get_user_info()
        if user_info:
            print("[INFO] User Information:")
            print(f"  Email: {user_info['email']}")
            print(f"  Connected Accounts: {len(user_info['connected_accounts'])}")
            print()

        # Test token retrieval
        if connections["linkedin"]:
            token = auth.get_linkedin_access_token()
            print(f"[OK] LinkedIn token retrieved: {token[:20]}...")
        else:
            print("[INFO] LinkedIn not connected yet")
            print(f"       Connect at: {auth.get_connect_url('linkedin', '/dashboard')}")

        print()

    except ValueError as e:
        print(f"[ERROR] Configuration error: {e}")
        print()
        print("Please ensure:")
        print("1. CLERK_SECRET_KEY is set in .env")
        print("2. MILTON_USER_ID is set in .env (after signing in to Clerk)")

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
