from supabase import create_client, Client
from typing import List, Dict, Any, Optional
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Supabase database client for news recommendation system"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.client: Client = create_client(self.url, self.key)
    
    # User Management
    async def create_user_profile(self, user_id: str, email: str, preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create user profile in database"""
        try:
            profile_data = {
                "user_id": user_id,
                "email": email,
                "preferences": preferences or {},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("user_profiles").insert(profile_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating user profile: {e}")
            raise
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by user_id"""
        try:
            result = self.client.table("user_profiles").select("*").eq("user_id", user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        try:
            result = self.client.table("user_profiles").update({
                "preferences": preferences,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("user_id", user_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False
    
    # News Articles Management
    async def store_news_articles(self, articles: List[Dict[str, Any]]) -> bool:
        """Store news articles in database"""
        try:
            # Add timestamps
            for article in articles:
                article["created_at"] = datetime.utcnow().isoformat()
                article["updated_at"] = datetime.utcnow().isoformat()
            
            result = self.client.table("news_articles").upsert(articles).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error storing news articles: {e}")
            return False
    
    async def get_recent_news(self, limit: int = 100, category: str = None) -> List[Dict[str, Any]]:
        """Get recent news articles"""
        try:
            query = self.client.table("news_articles").select("*")
            
            if category:
                query = query.eq("category", category)
            
            # Get articles from last 24 hours
            yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
            query = query.gte("published_at", yesterday)
            
            result = query.order("published_at", desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting recent news: {e}")
            return []
    
    async def get_news_by_ids(self, article_ids: List[str]) -> List[Dict[str, Any]]:
        """Get news articles by IDs"""
        try:
            result = self.client.table("news_articles").select("*").in_("id", article_ids).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting news by IDs: {e}")
            return []
    
    # User Behavior Tracking
    async def log_user_interaction(self, user_id: str, article_id: str, interaction_type: str, 
                                 duration: float = None, metadata: Dict[str, Any] = None) -> bool:
        """Log user interaction with news article"""
        try:
            interaction_data = {
                "user_id": user_id,
                "article_id": article_id,
                "interaction_type": interaction_type,  # 'click', 'read', 'like', 'share'
                "duration": duration,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("user_interactions").insert(interaction_data).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error logging user interaction: {e}")
            return False
    
    async def get_user_interactions(self, user_id: str, limit: int = 100, 
                                  days_back: int = 30) -> List[Dict[str, Any]]:
        """Get user's recent interactions"""
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
            
            result = self.client.table("user_interactions").select("*").eq("user_id", user_id)\
                .gte("timestamp", cutoff_date).order("timestamp", desc=True).limit(limit).execute()
            
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting user interactions: {e}")
            return []
    
    async def get_user_reading_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's reading history with article details"""
        try:
            # Get interactions with article details
            result = self.client.table("user_interactions").select("""
                *,
                news_articles (
                    id,
                    title,
                    category,
                    published_at,
                    source
                )
            """).eq("user_id", user_id).eq("interaction_type", "read")\
                .order("timestamp", desc=True).limit(limit).execute()
            
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting user reading history: {e}")
            return []
    
    # Recommendation Logging
    async def log_recommendations(self, user_id: str, article_ids: List[str], 
                                scores: List[float], algorithm: str = "mtl_model") -> bool:
        """Log recommendations shown to user"""
        try:
            recommendation_data = {
                "user_id": user_id,
                "article_ids": article_ids,
                "scores": scores,
                "algorithm": algorithm,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("recommendation_logs").insert(recommendation_data).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error logging recommendations: {e}")
            return False
    
    # Analytics
    async def get_user_category_preferences(self, user_id: str) -> Dict[str, int]:
        """Get user's category preferences based on interaction history"""
        try:
            result = self.client.table("user_interactions").select("""
                news_articles (category)
            """).eq("user_id", user_id).execute()
            
            category_counts = {}
            for interaction in result.data or []:
                if interaction.get("news_articles") and interaction["news_articles"].get("category"):
                    category = interaction["news_articles"]["category"]
                    category_counts[category] = category_counts.get(category, 0) + 1
            
            return category_counts
        except Exception as e:
            logger.error(f"Error getting user category preferences: {e}")
            return {}

# Global database client instance
_db_client = None

def get_db() -> SupabaseClient:
    """Get singleton database client instance"""
    global _db_client
    if _db_client is None:
        _db_client = SupabaseClient()
    return _db_client