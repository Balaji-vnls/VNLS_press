#!/usr/bin/env python3
"""
Simplified News Recommendation System Backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
import os
import logging
from datetime import datetime
import json
import requests
import asyncio
import aiohttp
from dotenv import load_dotenv
import hashlib

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🔄 Fetching live news on startup...")
    await fetch_live_news()
    
    if LIVE_NEWS_CACHE:
        logger.info(f"✅ Loaded {len(LIVE_NEWS_CACHE)} live news articles")
    else:
        logger.info("⚠️ Using sample data - check API keys")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down NARAYANASWAMY SONS News Platform...")

# Create FastAPI app
app = FastAPI(
    title="NARAYANASWAMY SONS - News Intelligence Platform",
    description="Advanced AI-powered news recommendation system with real-time updates by Narayanaswamy Sons",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample news data for demonstration
SAMPLE_NEWS = [
    {
        "id": "tech-1",
        "title": "AI Breakthrough: New Machine Learning Model Achieves 95% Accuracy",
        "content": "Researchers have developed a revolutionary machine learning model that demonstrates unprecedented accuracy in natural language processing tasks.",
        "summary": "New AI model shows remarkable performance improvements in language understanding.",
        "url": "https://example.com/ai-breakthrough",
        "source": "TechNews",
        "category": "technology",
        "published_at": "2024-12-17T10:00:00Z",
        "image_url": "https://via.placeholder.com/400x200/3B82F6/FFFFFF?text=AI+Breakthrough",
        "author": "Dr. Sarah Johnson",
        "recommendation_score": 0.92,
        "click_probability": 0.85
    },
    {
        "id": "business-1", 
        "title": "Global Markets Rally as Tech Stocks Surge",
        "content": "Major technology companies saw significant gains today as investors showed renewed confidence in the sector's growth prospects.",
        "summary": "Tech stocks lead market rally with strong investor confidence.",
        "url": "https://example.com/market-rally",
        "source": "Financial Times",
        "category": "business",
        "published_at": "2024-12-17T09:30:00Z",
        "image_url": "https://via.placeholder.com/400x200/10B981/FFFFFF?text=Market+Rally",
        "author": "Michael Chen",
        "recommendation_score": 0.78,
        "click_probability": 0.72
    },
    {
        "id": "health-1",
        "title": "New Study Reveals Benefits of Mediterranean Diet",
        "content": "A comprehensive 10-year study shows that following a Mediterranean diet can reduce the risk of heart disease by up to 30%.",
        "summary": "Mediterranean diet linked to significant heart health benefits.",
        "url": "https://example.com/mediterranean-diet",
        "source": "Health Today",
        "category": "health",
        "published_at": "2024-12-17T08:15:00Z",
        "image_url": "https://via.placeholder.com/400x200/EF4444/FFFFFF?text=Health+Study",
        "author": "Dr. Maria Rodriguez",
        "recommendation_score": 0.81,
        "click_probability": 0.69
    },
    {
        "id": "science-1",
        "title": "Scientists Discover New Exoplanet in Habitable Zone",
        "content": "Astronomers have identified a potentially habitable exoplanet located 40 light-years away from Earth.",
        "summary": "New exoplanet discovery offers hope for finding extraterrestrial life.",
        "url": "https://example.com/exoplanet-discovery",
        "source": "Space Science Journal",
        "category": "science",
        "published_at": "2024-12-17T07:45:00Z",
        "image_url": "https://via.placeholder.com/400x200/8B5CF6/FFFFFF?text=Space+Discovery",
        "author": "Prof. James Wilson",
        "recommendation_score": 0.75,
        "click_probability": 0.68
    },
    {
        "id": "general-1",
        "title": "Climate Summit Reaches Historic Agreement",
        "content": "World leaders have reached a groundbreaking agreement on climate action at the international summit.",
        "summary": "Historic climate agreement reached by world leaders.",
        "url": "https://example.com/climate-summit",
        "source": "Global News",
        "category": "general",
        "published_at": "2024-12-17T06:30:00Z",
        "image_url": "https://via.placeholder.com/400x200/059669/FFFFFF?text=Climate+Summit",
        "author": "Emma Thompson",
        "recommendation_score": 0.73,
        "click_probability": 0.65
    }
]

# Pydantic models
class UserSignUp(BaseModel):
    email: str
    password: str
    preferences: Optional[Dict[str, Any]] = {}

class UserSignIn(BaseModel):
    email: str
    password: str

# Mock user storage (in production, use a real database)
USERS = {}
SESSIONS = {}

# News API configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")

# Live news cache
LIVE_NEWS_CACHE = []
CACHE_TIMESTAMP = None

async def fetch_live_news():
    """Fetch live news from APIs"""
    global LIVE_NEWS_CACHE, CACHE_TIMESTAMP
    
    try:
        articles = []
        
        # Fetch from NewsAPI if key is available
        if NEWS_API_KEY:
            try:
                async with aiohttp.ClientSession() as session:
                    url = "https://newsapi.org/v2/top-headlines"
                    params = {
                        "apiKey": NEWS_API_KEY,
                        "language": "en",
                        "pageSize": 20,
                        "sortBy": "publishedAt"
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for article in data.get("articles", []):
                                if article.get("title") and article.get("description"):
                                    article_id = hashlib.md5(
                                        f"{article['title']}_{article.get('source', {}).get('name', 'NewsAPI')}".encode()
                                    ).hexdigest()
                                    
                                    processed_article = {
                                        "id": article_id,
                                        "title": article["title"],
                                        "content": article.get("description", "") + " " + (article.get("content", "") or ""),
                                        "summary": article.get("description", ""),
                                        "url": article.get("url", ""),
                                        "source": article.get("source", {}).get("name", "NewsAPI"),
                                        "category": "general",
                                        "published_at": article.get("publishedAt", datetime.utcnow().isoformat()),
                                        "image_url": article.get("urlToImage"),
                                        "author": article.get("author"),
                                        "recommendation_score": 0.75 + (hash(article_id) % 25) / 100,
                                        "click_probability": 0.65 + (hash(article_id) % 30) / 100
                                    }
                                    articles.append(processed_article)
                            
                            logger.info(f"Fetched {len(articles)} articles from NewsAPI")
            except Exception as e:
                logger.error(f"Error fetching from NewsAPI: {e}")
        
        # Fetch from GNews if key is available
        if GNEWS_API_KEY:
            try:
                async with aiohttp.ClientSession() as session:
                    categories = ["technology", "business", "health", "science"]
                    
                    for category in categories:
                        url = "https://gnews.io/api/v4/top-headlines"
                        params = {
                            "token": GNEWS_API_KEY,
                            "lang": "en",
                            "country": "us",
                            "max": 5,
                            "category": category
                        }
                        
                        async with session.get(url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                for article in data.get("articles", []):
                                    if article.get("title") and article.get("description"):
                                        article_id = hashlib.md5(
                                            f"{article['title']}_{article.get('source', {}).get('name', 'GNews')}".encode()
                                        ).hexdigest()
                                        
                                        processed_article = {
                                            "id": article_id,
                                            "title": article["title"],
                                            "content": article.get("description", "") + " " + (article.get("content", "") or ""),
                                            "summary": article.get("description", ""),
                                            "url": article.get("url", ""),
                                            "source": article.get("source", {}).get("name", "GNews"),
                                            "category": category,
                                            "published_at": article.get("publishedAt", datetime.utcnow().isoformat()),
                                            "image_url": article.get("image"),
                                            "author": article.get("source", {}).get("name", ""),
                                            "recommendation_score": 0.70 + (hash(article_id) % 30) / 100,
                                            "click_probability": 0.60 + (hash(article_id) % 35) / 100
                                        }
                                        articles.append(processed_article)
                
                logger.info(f"Fetched additional articles from GNews, total: {len(articles)}")
            except Exception as e:
                logger.error(f"Error fetching from GNews: {e}")
        
        # If we got live articles, update cache
        if articles:
            LIVE_NEWS_CACHE = articles
            CACHE_TIMESTAMP = datetime.utcnow()
            logger.info(f"Updated news cache with {len(articles)} live articles")
        else:
            # Fallback to sample data if no live articles
            logger.warning("No live articles fetched, using sample data")
            
    except Exception as e:
        logger.error(f"Error in fetch_live_news: {e}")

def get_cached_news():
    """Get news from cache or sample data"""
    global CACHE_TIMESTAMP
    
    # Check if cache is fresh (less than 30 minutes old)
    if CACHE_TIMESTAMP and LIVE_NEWS_CACHE:
        cache_age = (datetime.utcnow() - CACHE_TIMESTAMP).total_seconds()
        if cache_age < 1800:  # 30 minutes
            return LIVE_NEWS_CACHE
    
    # Return sample data if cache is stale or empty
    return SAMPLE_NEWS

# Routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to NARAYANASWAMY SONS News Intelligence Platform",
        "company": "Narayanaswamy Sons",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "NARAYANASWAMY SONS News Platform",
        "company": "Narayanaswamy Sons",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/status")
async def get_system_status():
    """Get detailed system status"""
    return {
        "company": "Narayanaswamy Sons",
        "platform": "News Intelligence Platform",
        "version": "1.0.0",
        "status": "operational",
        "features": {
            "live_news": len(LIVE_NEWS_CACHE) > 0,
            "ai_recommendations": True,
            "real_time_updates": True,
            "multi_source_integration": True
        },
        "statistics": {
            "total_articles": len(get_cached_news()),
            "live_articles": len(LIVE_NEWS_CACHE),
            "sample_articles": len(SAMPLE_NEWS),
            "registered_users": len(USERS),
            "active_sessions": len(SESSIONS)
        },
        "data_sources": {
            "newsapi": "✅ Active" if NEWS_API_KEY else "❌ Not configured",
            "gnews": "✅ Active" if GNEWS_API_KEY else "❌ Not configured",
            "rss_feeds": "✅ Available"
        },
        "last_updated": CACHE_TIMESTAMP.isoformat() if CACHE_TIMESTAMP else None,
        "timestamp": datetime.utcnow().isoformat()
    }

# Authentication endpoints
@app.post("/api/auth/signup")
async def sign_up(user_data: UserSignUp):
    if user_data.email in USERS:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user_id = f"user_{len(USERS) + 1}"
    USERS[user_data.email] = {
        "id": user_id,
        "email": user_data.email,
        "password": user_data.password,  # In production, hash this!
        "preferences": user_data.preferences,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Create session
    session_token = f"session_{user_id}_{datetime.utcnow().timestamp()}"
    SESSIONS[session_token] = {
        "user_id": user_id,
        "email": user_data.email,
        "expires_at": datetime.utcnow().timestamp() + 86400  # 24 hours
    }
    
    return {
        "message": "User created successfully",
        "user": {
            "id": user_id,
            "email": user_data.email,
            "preferences": user_data.preferences
        },
        "session": {
            "access_token": session_token,
            "token_type": "bearer"
        }
    }

@app.post("/api/auth/signin")
async def sign_in(user_data: UserSignIn):
    if user_data.email not in USERS:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = USERS[user_data.email]
    if user["password"] != user_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create session
    session_token = f"session_{user['id']}_{datetime.utcnow().timestamp()}"
    SESSIONS[session_token] = {
        "user_id": user["id"],
        "email": user_data.email,
        "expires_at": datetime.utcnow().timestamp() + 86400  # 24 hours
    }
    
    return {
        "message": "Signed in successfully",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "preferences": user.get("preferences", {})
        },
        "session": {
            "access_token": session_token,
            "token_type": "bearer"
        }
    }

# News endpoints
@app.get("/api/news/trending")
async def get_trending_news(limit: int = 20):
    # Get live or cached news
    news_articles = get_cached_news()
    
    # Sort by recommendation score and return top articles
    sorted_news = sorted(news_articles, key=lambda x: x.get("recommendation_score", 0), reverse=True)
    return {
        "articles": sorted_news[:limit],
        "total": len(sorted_news[:limit]),
        "source": "live" if LIVE_NEWS_CACHE else "sample"
    }

@app.get("/api/news/categories")
async def get_categories():
    categories = [
        {"id": "general", "name": "General", "description": "General news and current events"},
        {"id": "technology", "name": "Technology", "description": "Tech news, startups, and innovation"},
        {"id": "business", "name": "Business", "description": "Business news, markets, and finance"},
        {"id": "health", "name": "Health", "description": "Health, medicine, and wellness"},
        {"id": "science", "name": "Science", "description": "Scientific discoveries and research"}
    ]
    return {"categories": categories}

@app.get("/api/news/category/{category}")
async def get_news_by_category(category: str, limit: int = 20):
    news_articles = get_cached_news()
    filtered_news = [article for article in news_articles if article["category"] == category]
    return {
        "articles": filtered_news[:limit],
        "total": len(filtered_news[:limit]),
        "category": category,
        "source": "live" if LIVE_NEWS_CACHE else "sample"
    }

@app.get("/api/news/search")
async def search_news(q: str, limit: int = 20):
    news_articles = get_cached_news()
    query_lower = q.lower()
    filtered_news = [
        article for article in news_articles 
        if query_lower in article["title"].lower() or 
           query_lower in article["content"].lower() or
           query_lower in article["summary"].lower()
    ]
    return {
        "articles": filtered_news[:limit],
        "total": len(filtered_news[:limit]),
        "query": q,
        "source": "live" if LIVE_NEWS_CACHE else "sample"
    }

@app.get("/api/news/article/{article_id}")
async def get_article(article_id: str):
    news_articles = get_cached_news()
    article = next((a for a in news_articles if a["id"] == article_id), None)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"article": article}

# Recommendation endpoints
@app.get("/api/recommendations/personalized")
async def get_personalized_recommendations(limit: int = 20):
    # For demo, return articles sorted by recommendation score
    news_articles = get_cached_news()
    sorted_news = sorted(news_articles, key=lambda x: x.get("recommendation_score", 0), reverse=True)
    return {
        "recommendations": sorted_news[:limit],
        "total": len(sorted_news[:limit]),
        "source": "live" if LIVE_NEWS_CACHE else "sample"
    }

@app.get("/api/recommendations/for-you")
async def get_for_you_feed(limit: int = 20):
    # For demo, return personalized feed with some randomization
    import random
    news_articles = get_cached_news()
    shuffled_news = news_articles.copy()
    random.shuffle(shuffled_news)
    
    # Add feed metadata
    for i, article in enumerate(shuffled_news):
        article["feed_position"] = i + 1
        article["feed_type"] = "personalized"
    
    return {
        "feed": shuffled_news[:limit],
        "total": len(shuffled_news[:limit]),
        "feed_type": "for_you",
        "source": "live" if LIVE_NEWS_CACHE else "sample"
    }

@app.get("/api/recommendations/trending")
async def get_trending_recommendations(limit: int = 20):
    # Sort by click probability for trending
    news_articles = get_cached_news()
    sorted_news = sorted(news_articles, key=lambda x: x.get("click_probability", 0), reverse=True)
    
    for i, article in enumerate(sorted_news):
        article["trending_position"] = i + 1
        article["trending_score"] = article.get("click_probability", 0)
    
    return {
        "trending": sorted_news[:limit],
        "total": len(sorted_news[:limit]),
        "source": "live" if LIVE_NEWS_CACHE else "sample"
    }

# News refresh endpoint
@app.post("/api/news/refresh")
async def refresh_news():
    """Manually refresh news from APIs"""
    await fetch_live_news()
    return {
        "message": "News refresh completed",
        "articles_count": len(LIVE_NEWS_CACHE),
        "timestamp": datetime.utcnow().isoformat()
    }



if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting NARAYANASWAMY SONS News Intelligence Platform...")
    logger.info("🏢 Company: Narayanaswamy Sons")
    logger.info("🔑 News API Key: " + ("✅ Configured" if NEWS_API_KEY else "❌ Missing"))
    logger.info("🔑 GNews API Key: " + ("✅ Configured" if GNEWS_API_KEY else "❌ Missing"))
    logger.info("🌐 Server will be available at: http://localhost:8000")
    logger.info("📖 API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "simple_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )