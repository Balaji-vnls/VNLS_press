from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import logging

from services.recommendation_service import get_recommendation_service
from models.database import get_db
from routes.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/personalized")
async def get_personalized_recommendations(
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get personalized news recommendations for the current user"""
    try:
        recommendation_service = get_recommendation_service()
        db = get_db()
        
        # Get available articles
        if category:
            articles = await db.get_recent_news(limit=limit * 3, category=category)
        else:
            articles = await db.get_recent_news(limit=limit * 3)
        
        if not articles:
            return {
                "recommendations": [],
                "total": 0,
                "message": "No articles available for recommendations"
            }
        
        # Get personalized recommendations
        recommendations = await recommendation_service.get_personalized_recommendations(
            user_id=current_user["user_id"],
            articles=articles,
            top_k=limit
        )
        
        return {
            "recommendations": recommendations,
            "total": len(recommendations),
            "user_id": current_user["user_id"],
            "category": category
        }
        
    except Exception as e:
        logger.error(f"Error getting personalized recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/for-you")
async def get_for_you_feed(
    limit: int = Query(20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get 'For You' personalized news feed"""
    try:
        recommendation_service = get_recommendation_service()
        db = get_db()
        
        # Get diverse articles from multiple categories
        categories = ["technology", "business", "health", "science", "general"]
        all_articles = []
        
        for category in categories:
            category_articles = await db.get_recent_news(limit=30, category=category)
            all_articles.extend(category_articles)
        
        if not all_articles:
            return {
                "feed": [],
                "total": 0,
                "message": "No articles available"
            }
        
        # Get personalized recommendations
        recommendations = await recommendation_service.get_personalized_recommendations(
            user_id=current_user["user_id"],
            articles=all_articles,
            top_k=limit
        )
        
        # Add feed metadata
        for i, rec in enumerate(recommendations):
            rec["feed_position"] = i + 1
            rec["feed_type"] = "personalized"
        
        return {
            "feed": recommendations,
            "total": len(recommendations),
            "user_id": current_user["user_id"],
            "feed_type": "for_you"
        }
        
    except Exception as e:
        logger.error(f"Error getting for you feed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/similar/{article_id}")
async def get_similar_articles(
    article_id: str,
    limit: int = Query(10, ge=1, le=50),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get articles similar to a specific article"""
    try:
        db = get_db()
        recommendation_service = get_recommendation_service()
        
        # Get the reference article
        reference_articles = await db.get_news_by_ids([article_id])
        if not reference_articles:
            raise HTTPException(status_code=404, detail="Article not found")
        
        reference_article = reference_articles[0]
        reference_category = reference_article.get("category", "general")
        
        # Get articles from the same category
        similar_articles = await db.get_recent_news(limit=limit * 3, category=reference_category)
        
        # Remove the reference article from results
        similar_articles = [a for a in similar_articles if a.get("id") != article_id]
        
        if current_user:
            # Get personalized similar articles
            recommendations = await recommendation_service.get_personalized_recommendations(
                user_id=current_user["user_id"],
                articles=similar_articles,
                top_k=limit
            )
        else:
            # Get general recommendations
            recommendations = recommendation_service.ml_model.get_personalized_recommendations(
                similar_articles, top_k=limit
            )
        
        return {
            "similar_articles": recommendations,
            "total": len(recommendations),
            "reference_article": reference_article,
            "category": reference_category
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting similar articles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/trending")
async def get_trending_recommendations(
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None)
):
    """Get trending news recommendations (non-personalized)"""
    try:
        recommendation_service = get_recommendation_service()
        
        if category:
            recommendations = await recommendation_service.get_category_recommendations(
                category=category,
                limit=limit
            )
        else:
            recommendations = await recommendation_service.get_trending_recommendations(limit=limit)
        
        # Add trending metadata
        for i, rec in enumerate(recommendations):
            rec["trending_position"] = i + 1
            rec["trending_score"] = rec.get("trending_score", rec.get("recommendation_score", 0))
        
        return {
            "trending": recommendations,
            "total": len(recommendations),
            "category": category
        }
        
    except Exception as e:
        logger.error(f"Error getting trending recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/categories/{category}")
async def get_category_recommendations(
    category: str,
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get recommendations for a specific category"""
    try:
        recommendation_service = get_recommendation_service()
        
        user_id = current_user["user_id"] if current_user else None
        recommendations = await recommendation_service.get_category_recommendations(
            category=category,
            user_id=user_id,
            limit=limit
        )
        
        return {
            "recommendations": recommendations,
            "total": len(recommendations),
            "category": category,
            "personalized": current_user is not None
        }
        
    except Exception as e:
        logger.error(f"Error getting category recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/history")
async def get_recommendation_history(
    limit: int = Query(50, ge=1, le=200),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user's recommendation history"""
    try:
        db = get_db()
        
        # Get user's reading history
        reading_history = await db.get_user_reading_history(
            current_user["user_id"], 
            limit=limit
        )
        
        return {
            "history": reading_history,
            "total": len(reading_history),
            "user_id": current_user["user_id"]
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendation history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/preferences")
async def get_recommendation_preferences(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user's recommendation preferences and insights"""
    try:
        db = get_db()
        
        # Get user profile
        user_profile = await db.get_user_profile(current_user["user_id"])
        
        # Get category preferences based on reading history
        category_preferences = await db.get_user_category_preferences(current_user["user_id"])
        
        # Get recent interactions
        recent_interactions = await db.get_user_interactions(
            current_user["user_id"], 
            limit=100, 
            days_back=30
        )
        
        # Calculate engagement metrics
        total_interactions = len(recent_interactions)
        interaction_types = {}
        for interaction in recent_interactions:
            int_type = interaction.get("interaction_type", "unknown")
            interaction_types[int_type] = interaction_types.get(int_type, 0) + 1
        
        return {
            "user_preferences": user_profile.get("preferences", {}) if user_profile else {},
            "category_preferences": category_preferences,
            "engagement_metrics": {
                "total_interactions": total_interactions,
                "interaction_types": interaction_types,
                "days_active": min(30, len(set(
                    interaction.get("timestamp", "")[:10] 
                    for interaction in recent_interactions
                )))
            },
            "recommendation_insights": {
                "top_categories": sorted(
                    category_preferences.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:5],
                "activity_level": "high" if total_interactions > 50 else "medium" if total_interactions > 10 else "low"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendation preferences: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/feedback")
async def submit_recommendation_feedback(
    article_id: str,
    feedback_type: str = Query(..., regex="^(like|dislike|not_interested|report)$"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Submit feedback on a recommendation"""
    try:
        db = get_db()
        
        # Log feedback as a special interaction
        success = await db.log_user_interaction(
            user_id=current_user["user_id"],
            article_id=article_id,
            interaction_type="feedback",
            metadata={
                "feedback_type": feedback_type,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        if success:
            return {"message": "Feedback submitted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to submit feedback")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")