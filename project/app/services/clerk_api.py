import os
import httpx
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ClerkAPIService:
    """Service for interacting with Clerk API"""

    CLERK_API_URL = "https://api.clerk.com/v1"

    @staticmethod
    def _get_clerk_secret_key() -> str:
        """Get Clerk secret key from environment"""
        secret = os.getenv("CLERK_SECRET_KEY")
        if not secret:
            raise ValueError("CLERK_SECRET_KEY not configured")
        return secret

    @classmethod
    async def get_user(cls, clerk_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch user data from Clerk API
        
        Args:
            clerk_id: The Clerk user ID
            
        Returns:
            User data dict with firstName, lastName, email, etc.
            Returns None if user not found or error occurs
        """
        try:
            secret_key = cls._get_clerk_secret_key()
            url = f"{cls.CLERK_API_URL}/users/{clerk_id}"
            
            headers = {
                "Authorization": f"Bearer {secret_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10.0)
                
                if response.status_code == 404:
                    logger.warning(f"User {clerk_id} not found in Clerk")
                    return None
                
                if response.status_code != 200:
                    logger.error(f"Clerk API error {response.status_code}: {response.text}")
                    return None
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Error fetching user from Clerk: {str(e)}")
            return None

    @classmethod
    async def list_users(cls) -> Optional[list]:
        """
        Fetch all users from Clerk API
        
        Returns:
            List of user data dicts
        """
        try:
            secret_key = cls._get_clerk_secret_key()
            url = f"{cls.CLERK_API_URL}/users"
            
            headers = {
                "Authorization": f"Bearer {secret_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10.0)
                
                if response.status_code != 200:
                    logger.error(f"Clerk API error {response.status_code}: {response.text}")
                    return None
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Error fetching users from Clerk: {str(e)}")
            return None

    @staticmethod
    def extract_user_info(user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract relevant user information from Clerk API response
        
        Args:
            user_data: Raw user data from Clerk API
            
        Returns:
            Dict with firstName, lastName, email
        """
        email = None
        email_addresses = user_data.get("email_addresses") or []
        if isinstance(email_addresses, list) and len(email_addresses) > 0:
            email = (
                email_addresses[0].get("email_address")
                if isinstance(email_addresses[0], dict)
                else None
            )
        
        return {
            "firstName": user_data.get("first_name") or "",
            "lastName": user_data.get("last_name") or "",
            "email": email or ""
        }
