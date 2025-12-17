from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import logging

from services.auth_service import get_auth_service
from models.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

# Pydantic models for request/response
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    preferences: Optional[Dict[str, Any]] = None

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UpdateUserRequest(BaseModel):
    user_metadata: Optional[Dict[str, Any]] = None
    password: Optional[str] = None

class ResetPasswordRequest(BaseModel):
    email: EmailStr

# Dependency to get current user
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user from authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    auth_service = get_auth_service()
    
    user_info = auth_service.verify_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user_info

@router.post("/signup")
async def sign_up(request: SignUpRequest):
    """Sign up a new user"""
    try:
        auth_service = get_auth_service()
        db = get_db()
        
        # Sign up with Supabase
        result = await auth_service.sign_up(
            email=request.email,
            password=request.password,
            user_metadata=request.preferences
        )
        
        if result["success"]:
            # Create user profile in database
            user_id = result["user"]["id"]
            await db.create_user_profile(
                user_id=user_id,
                email=request.email,
                preferences=request.preferences or {}
            )
            
            return {
                "message": "User created successfully",
                "user": result["user"],
                "session": result["session"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sign up error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/signin")
async def sign_in(request: SignInRequest):
    """Sign in an existing user"""
    try:
        auth_service = get_auth_service()
        
        result = await auth_service.sign_in(
            email=request.email,
            password=request.password
        )
        
        if result["success"]:
            return {
                "message": "Signed in successfully",
                "user": result["user"],
                "session": result["session"]
            }
        else:
            raise HTTPException(status_code=401, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sign in error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/signout")
async def sign_out(current_user: Dict[str, Any] = Depends(get_current_user),
                  authorization: str = Header(...)):
    """Sign out current user"""
    try:
        auth_service = get_auth_service()
        token = authorization.split(" ")[1]
        
        result = await auth_service.sign_out(token)
        
        if result["success"]:
            return {"message": "Signed out successfully"}
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sign out error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """Refresh user session token"""
    try:
        auth_service = get_auth_service()
        
        result = await auth_service.refresh_token(request.refresh_token)
        
        if result["success"]:
            return {
                "message": "Token refreshed successfully",
                "session": result["session"]
            }
        else:
            raise HTTPException(status_code=401, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/me")
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information"""
    try:
        db = get_db()
        
        # Get user profile from database
        user_profile = await db.get_user_profile(current_user["user_id"])
        
        return {
            "user": {
                **current_user,
                "profile": user_profile
            }
        }
        
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/me")
async def update_current_user(request: UpdateUserRequest,
                             current_user: Dict[str, Any] = Depends(get_current_user),
                             authorization: str = Header(...)):
    """Update current user information"""
    try:
        auth_service = get_auth_service()
        db = get_db()
        token = authorization.split(" ")[1]
        
        # Update user in Supabase
        updates = {}
        if request.user_metadata:
            updates["data"] = request.user_metadata
        if request.password:
            updates["password"] = request.password
        
        if updates:
            result = await auth_service.update_user(token, updates)
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result["error"])
        
        # Update user preferences in database
        if request.user_metadata:
            await db.update_user_preferences(
                current_user["user_id"], 
                request.user_metadata
            )
        
        return {"message": "User updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Send password reset email"""
    try:
        auth_service = get_auth_service()
        
        result = await auth_service.reset_password(request.email)
        
        if result["success"]:
            return {"message": "Password reset email sent"}
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/preferences")
async def get_user_preferences(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user preferences and reading history"""
    try:
        db = get_db()
        
        # Get user profile
        user_profile = await db.get_user_profile(current_user["user_id"])
        
        # Get category preferences based on reading history
        category_preferences = await db.get_user_category_preferences(current_user["user_id"])
        
        # Get recent reading history
        reading_history = await db.get_user_reading_history(current_user["user_id"], limit=20)
        
        return {
            "preferences": user_profile.get("preferences", {}) if user_profile else {},
            "category_preferences": category_preferences,
            "reading_history": reading_history
        }
        
    except Exception as e:
        logger.error(f"Get preferences error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")