from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from services.news_service import get_news_service
from services.recommendation_service import get_recommendation_service
from models.database import get_db
from routes.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/news", tags=["news"])

@router.get("/trending")
async def get_trending_news(
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None)
):
    """Get trending news articles"""
    try:
        recommendation_service = get_recommendation_service()
        
        if category:
            trending_articles = await recommendation_service.get_category_recommendations(
                category=category,
                limit=limit
            )
        else:
            trending_articles = await recommendation_service.get_trending_recommendations(limit=limit)
        
        return {
            "articles": trending_articles,
            "total": len(trending_articles),
            "category": category
        }
        
    except Exception as e:
        logger.error(f"Error getting trending news: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/categories")
async def get_news_categories():
    """Get available news categories"""
    categories = [
        {"id": "general", "name": "General", "description": "General news and current events"},
        {"id": "technology", "name": "Technology", "description": "Tech news, startups, and innovation"},
        {"id": "business", "name": "Business", "description": "Business news, markets, and finance"},
        {"id": "health", "name": "Health", "description": "Health, medicine, and wellness"},
        {"id": "science", "name": "Science", "description": "Scientific discoveries and research"},
        {"id": "sports", "name": "Sports", "description": "Sports news and updates"},
        {"id": "entertainment", "name": "Entertainment", "description": "Entertainment and celebrity news"}
    ]
    
    return {"categories": categories}

@router.get("/category/{category}")
async def get_news_by_category(
    category: str,
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get news articles by category"""
    try:
        recommendation_service = get_recommendation_service()
        
        user_id = current_user["user_id"] if current_user else None
        articles = await recommendation_service.get_category_recommendations(
            category=category,
            user_id=user_id,
            limit=limit
        )
        
        return {
            "articles": articles,
            "total": len(articles),
            "category": category
        }
        
    except Exception as e:
        logger.error(f"Error getting news by category: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search")
async def search_news(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None)
):
    """Search news articles"""
    try:
        db = get_db()
        
        # Simple search implementation - can be enhanced with full-text search
        articles = await db.get_recent_news(limit=limit * 2, category=category)
        
        # Filter articles by search query
        search_results = []
        query_lower = q.lower()
        
        for article in articles:
            title = article.get("title", "").lower()
            content = article.get("content", "").lower()
            summary = article.get("summary", "").lower()
            
            if (query_lower in title or 
                query_lower in content or 
                query_lower in summary):
                search_results.append(article)
        
        # Limit results
        search_results = search_results[:limit]
        
        return {
            "articles": search_results,
            "total": len(search_results),
            "query": q,
            "category": category
        }
        
    except Exception as e:
        logger.error(f"Error searching news: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/article/{article_id}")
async def get_article(
    article_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get a specific news article"""
    try:
        db = get_db()
        
        articles = await db.get_news_by_ids([article_id])
        
        if not articles:
            raise HTTPException(status_code=404, detail="Article not found")
        
        article = articles[0]
        
        # Log user interaction if user is authenticated
        if current_user:
            await db.log_user_interaction(
                user_id=current_user["user_id"],
                article_id=article_id,
                interaction_type="view",
                metadata={"timestamp": datetime.utcnow().isoformat()}
            )
        
        return {"article": article}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting article: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/article/{article_id}/interact")
async def log_article_interaction(
    article_id: str,
    interaction_type: str = Query(..., regex="^(click|read|like|share|bookmark)$"),
    duration: Optional[float] = Query(None, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Log user interaction with an article"""
    try:
        db = get_db()
        
        # Log the interaction
        success = await db.log_user_interaction(
            user_id=current_user["user_id"],
            article_id=article_id,
            interaction_type=interaction_type,
            duration=duration,
            metadata={
                "timestamp": datetime.utcnow().isoformat(),
                "user_agent": "web"  # Can be extracted from request headers
            }
        )
        
        if success:
            return {"message": "Interaction logged successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to log interaction")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging interaction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/refresh")
async def refresh_news(background_tasks: BackgroundTasks):
    """Refresh news articles from external sources"""
    try:
        # Add background task to fetch and store new articles
        background_tasks.add_task(fetch_and_store_news)
        
        return {"message": "News refresh initiated"}
        
    except Exception as e:
        logger.error(f"Error initiating news refresh: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def fetch_and_store_news():
    """Background task to fetch and store news articles"""
    try:
        news_service = get_news_service()
        db = get_db()
        
        # Fetch news from all sources
        articles = await news_service.fetch_all_news()
        
        if articles:
            # Store articles in database
            success = await db.store_news_articles(articles)
            if success:
                logger.info(f"Successfully stored {len(articles)} news articles")
            else:
                logger.error("Failed to store news articles")
        else:
            logger.warning("No articles fetched from news sources")
            
    except Exception as e:
        logger.error(f"Error in background news fetch: {e}")

@router.get("/sources")
async def get_news_sources():
    """Get available news sources"""
    sources = [
        {"id": "newsapi", "name": "NewsAPI", "description": "Global news aggregator"},
        {"id": "gnews", "name": "GNews", "description": "Google News API"},
        {"id": "rss", "name": "RSS Feeds", "description": "Various RSS news feeds"},
        {"id": "reuters", "name": "Reuters", "description": "Reuters news feed"},
        {"id": "bbc", "name": "BBC", "description": "BBC news feed"},
        {"id": "techcrunch", "name": "TechCrunch", "description": "Technology news"}
    ]
    
    return {"sources": sources}

@router.get("/stats")
async def get_news_stats():
    """Get news statistics"""
    try:
        db = get_db()
        
        # Get recent articles count by category
        categories = ["general", "technology", "business", "health", "science"]
        stats = {}
        
        for category in categories:
            articles = await db.get_recent_news(limit=1000, category=category)
            stats[category] = len(articles)
        
        # Get total articles
        all_articles = await db.get_recent_news(limit=10000)
        total_articles = len(all_articles)
        
        return {
            "total_articles": total_articles,
            "by_category": stats,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting news stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")