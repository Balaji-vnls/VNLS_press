from supabase import create_client, Client
from typing import Dict, Any, Optional
import os
import logging
from datetime import datetime, timedelta
import jwt

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service using Supabase Auth"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        
        self.client: Client = create_client(self.url, self.key)
    
    async def sign_up(self, email: str, password: str, user_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Sign up a new user"""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata or {}
                }
            })
            
            if response.user:
                logger.info(f"User signed up successfully: {email}")
                return {
                    "success": True,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "created_at": response.user.created_at,
                        "user_metadata": response.user.user_metadata
                    },
                    "session": {
                        "access_token": response.session.access_token if response.session else None,
                        "refresh_token": response.session.refresh_token if response.session else None,
                        "expires_at": response.session.expires_at if response.session else None
                    } if response.session else None
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create user"
                }
                
        except Exception as e:
            logger.error(f"Sign up error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in an existing user"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                logger.info(f"User signed in successfully: {email}")
                return {
                    "success": True,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "user_metadata": response.user.user_metadata,
                        "last_sign_in_at": response.user.last_sign_in_at
                    },
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                        "expires_at": response.session.expires_at,
                        "token_type": response.session.token_type
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid credentials"
                }
                
        except Exception as e:
            logger.error(f"Sign in error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sign_out(self, access_token: str) -> Dict[str, Any]:
        """Sign out a user"""
        try:
            # Set the session for the client
            self.client.auth.set_session(access_token, "")
            
            response = self.client.auth.sign_out()
            
            logger.info("User signed out successfully")
            return {
                "success": True,
                "message": "Signed out successfully"
            }
            
        except Exception as e:
            logger.error(f"Sign out error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh user session token"""
        try:
            response = self.client.auth.refresh_session(refresh_token)
            
            if response.session:
                return {
                    "success": True,
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                        "expires_at": response.session.expires_at,
                        "token_type": response.session.token_type
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to refresh token"
                }
                
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from access token"""
        try:
            # Set the session for the client
            self.client.auth.set_session(access_token, "")
            
            response = self.client.auth.get_user()
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_metadata": response.user.user_metadata,
                    "created_at": response.user.created_at,
                    "last_sign_in_at": response.user.last_sign_in_at
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Get user error: {e}")
            return None
    
    async def update_user(self, access_token: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user information"""
        try:
            # Set the session for the client
            self.client.auth.set_session(access_token, "")
            
            response = self.client.auth.update_user(updates)
            
            if response.user:
                return {
                    "success": True,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "user_metadata": response.user.user_metadata,
                        "updated_at": response.user.updated_at
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update user"
                }
                
        except Exception as e:
            logger.error(f"Update user error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def reset_password(self, email: str) -> Dict[str, Any]:
        """Send password reset email"""
        try:
            response = self.client.auth.reset_password_email(email)
            
            return {
                "success": True,
                "message": "Password reset email sent"
            }
            
        except Exception as e:
            logger.error(f"Password reset error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and extract user information"""
        try:
            # For Supabase tokens, we can decode without verification for basic info
            # In production, you should verify the signature with Supabase's public key
            decoded = jwt.decode(token, options={"verify_signature": False})
            
            # Check if token is expired
            if decoded.get('exp', 0) < datetime.utcnow().timestamp():
                return None
            
            return {
                "user_id": decoded.get('sub'),
                "email": decoded.get('email'),
                "role": decoded.get('role', 'authenticated'),
                "exp": decoded.get('exp')
            }
            
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    def create_custom_token(self, user_id: str, email: str, expires_in_hours: int = 24) -> str:
        """Create a custom JWT token for internal use"""
        try:
            payload = {
                "user_id": user_id,
                "email": email,
                "exp": datetime.utcnow() + timedelta(hours=expires_in_hours),
                "iat": datetime.utcnow()
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm="HS256")
            return token
            
        except Exception as e:
            logger.error(f"Custom token creation error: {e}")
            raise

# Global auth service instance
_auth_service = None

def get_auth_service() -> AuthService:
    """Get singleton auth service instance"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service