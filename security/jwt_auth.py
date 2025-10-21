"""
JWT Authentication Module
Handles JWT token generation, validation, and user authentication
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from functools import wraps
from fastapi import HTTPException, Security, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security scheme
security = HTTPBearer()


class JWTAuth:
    """JWT Authentication Manager"""

    @staticmethod
    def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a new JWT access token

        Args:
            data: Dictionary of claims to encode in the token
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: Dict) -> str:
        """
        Create a new JWT refresh token

        Args:
            data: Dictionary of claims to encode in the token

        Returns:
            Encoded JWT refresh token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Dict:
        """
        Verify and decode a JWT token

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )

        except jwt.JWTError:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )

    @staticmethod
    def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict:
        """
        Get current user from JWT token (FastAPI dependency)

        Args:
            credentials: HTTP Bearer credentials from request

        Returns:
            User data from token payload

        Raises:
            HTTPException: If authentication fails
        """
        token = credentials.credentials
        payload = JWTAuth.verify_token(token)

        # Verify it's an access token
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return payload

    @staticmethod
    def optional_auth(authorization: Optional[str] = Header(None)) -> Optional[Dict]:
        """
        Optional authentication - returns user if token provided, None otherwise

        Args:
            authorization: Optional Authorization header

        Returns:
            User data if authenticated, None otherwise
        """
        if not authorization:
            return None

        try:
            # Extract token from "Bearer <token>"
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                return None

            payload = JWTAuth.verify_token(token)
            if payload.get("type") != "access":
                return None

            return payload

        except Exception:
            return None


def create_user_token(user_id: str, email: str, name: Optional[str] = None) -> Dict:
    """
    Create access and refresh tokens for a user

    Args:
        user_id: User ID
        email: User email
        name: Optional user name

    Returns:
        Dictionary with access_token and refresh_token
    """
    token_data = {
        "sub": user_id,
        "email": email,
        "name": name
    }

    access_token = JWTAuth.create_access_token(token_data)
    refresh_token = JWTAuth.create_refresh_token({"sub": user_id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds
    }


def refresh_access_token(refresh_token: str) -> str:
    """
    Create a new access token from a refresh token

    Args:
        refresh_token: Valid refresh token

    Returns:
        New access token

    Raises:
        HTTPException: If refresh token is invalid
    """
    payload = JWTAuth.verify_token(refresh_token)

    # Verify it's a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid token type"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )

    # Create new access token
    new_token = JWTAuth.create_access_token({"sub": user_id})
    return new_token


# Development/Testing utilities
def create_dev_token() -> str:
    """
    Create a development token for testing

    Returns:
        Development JWT token
    """
    return JWTAuth.create_access_token({
        "sub": "dev-user-001",
        "email": "dev@milton-publicist.local",
        "name": "Development User",
        "dev": True
    })


if __name__ == "__main__":
    # Generate a development token for testing
    print("=" * 60)
    print("MILTON AI PUBLICIST - JWT TOKEN GENERATOR")
    print("=" * 60)

    dev_token = create_dev_token()

    print(f"\nDevelopment Token (valid for {ACCESS_TOKEN_EXPIRE_MINUTES} minutes):")
    print("-" * 60)
    print(dev_token)
    print("-" * 60)

    print("\nUse this token in API requests:")
    print('Authorization: Bearer <token>')

    print("\nExample curl command:")
    print(f'curl -H "Authorization: Bearer {dev_token}" http://localhost:8080/api/posts')

    print("\n" + "=" * 60)
