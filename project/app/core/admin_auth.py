import os
import jwt
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Request, Depends


class AdminAuthService:
    """Service for admin authentication and token management"""

    # Token expiration: 24 hours
    TOKEN_EXPIRATION_HOURS = 24
    
    @staticmethod
    def _get_jwt_secret() -> str:
        """Get JWT secret key from environment"""
        secret = os.getenv("JWT_SECRET_KEY")
        if not secret:
            # Fallback to a default if not set (should be configured in production)
            secret = "your-secret-key-change-in-production"
        return secret

    @classmethod
    def create_admin_token(cls, clerk_id: str) -> str:
        """
        Create a JWT token for admin session
        
        Args:
            clerk_id: The Clerk user ID of the admin
            
        Returns:
            JWT token string
        """
        secret = cls._get_jwt_secret()
        payload = {
            "clerk_id": clerk_id,
            "is_admin": True,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=cls.TOKEN_EXPIRATION_HOURS)
        }
        
        token = jwt.encode(payload, secret, algorithm="HS256")
        return token

    @classmethod
    def verify_admin_token(cls, token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT admin token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        secret = cls._get_jwt_secret()
        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin token"
            )

    @staticmethod
    def get_admin_token_from_request(request: Request) -> str:
        """
        Extract admin token from request (cookie or header)
        
        Args:
            request: FastAPI request object
            
        Returns:
            Token string
            
        Raises:
            HTTPException: If token not found
        """
        # Try to get from cookie first
        token = request.cookies.get("dogo-admin-token")
        
        # Fall back to Authorization header
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin token not found"
            )
        
        return token


async def verify_admin(request: Request) -> Dict[str, Any]:
    """
    Dependency for FastAPI routes to verify admin authentication
    
    Args:
        request: FastAPI request object
        
    Returns:
        Decoded token payload with admin_id and is_admin
        
    Raises:
        HTTPException: If authentication fails
    """
    token = AdminAuthService.get_admin_token_from_request(request)
    payload = AdminAuthService.verify_admin_token(token)
    
    if not payload.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an admin"
        )
    
    return payload
