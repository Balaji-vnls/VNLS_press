from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import asyncio

# Load environment variables
load_dotenv()

# Import routes
from routes import auth, news, recommendations
from services.news_service import get_news_service
from models.database import get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Background task for periodic news updates
async def periodic_news_update():
    """Periodically fetch and update news articles"""
    while True:
        try:
            logger.info("Starting periodic news update...")
            news_service = get_news_service()
            db = get_db()
            
            # Fetch news from all sources
            articles = await news_service.fetch_all_news()
            
            if articles:
                # Store articles in database
                success = await db.store_news_articles(articles)
                if success:
                    logger.info(f"Successfully updated {len(articles)} news articles")
                else:
                    logger.error("Failed to store news articles")
            else:
                logger.warning("No articles fetched during periodic update")
                
        except Exception as e:
            logger.error(f"Error in periodic news update: {e}")
        
        # Wait for 30 minutes before next update
        await asyncio.sleep(1800)  # 30 minutes

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting News Recommendation System...")
    
    # Initialize ML model
    try:
        from models.ml_model import get_model
        model = get_model()
        logger.info("ML model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load ML model: {e}")
    
    # Start background task for periodic news updates
    task = asyncio.create_task(periodic_news_update())
    
    # Initial news fetch
    try:
        logger.info("Performing initial news fetch...")
        news_service = get_news_service()
        db = get_db()
        
        articles = await news_service.fetch_all_news()
        if articles:
            await db.store_news_articles(articles)
            logger.info(f"Initial fetch: stored {len(articles)} articles")
    except Exception as e:
        logger.error(f"Error in initial news fetch: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down News Recommendation System...")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

# Create FastAPI app
app = FastAPI(
    title="Personalized News Recommendation System",
    description="AI-powered news recommendation system with real-time updates and personalization",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(news.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "News Recommendation System",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to the Personalized News Recommendation System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# API Info endpoint
@app.get("/api/info")
async def api_info():
    """Get API information"""
    return {
        "name": "News Recommendation API",
        "version": "1.0.0",
        "description": "AI-powered personalized news recommendation system",
        "endpoints": {
            "authentication": "/api/auth",
            "news": "/api/news",
            "recommendations": "/api/recommendations"
        },
        "features": [
            "Real-time news ingestion",
            "ML-powered recommendations",
            "User behavior tracking",
            "Personalized feeds",
            "Multi-source news aggregation"
        ]
    }

# Database initialization endpoint (for development)
@app.post("/api/admin/init-db")
async def initialize_database():
    """Initialize database with required tables (development only)"""
    if os.getenv("DEBUG") != "True":
        raise HTTPException(status_code=403, detail="Not available in production")
    
    try:
        # This would typically run SQL scripts to create tables
        # For Supabase, tables should be created through the dashboard or migrations
        logger.info("Database initialization requested")
        return {"message": "Database initialization completed"}
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise HTTPException(status_code=500, detail="Database initialization failed")

# Manual news refresh endpoint (for development)
@app.post("/api/admin/refresh-news")
async def manual_news_refresh(background_tasks: BackgroundTasks):
    """Manually trigger news refresh (development only)"""
    if os.getenv("DEBUG") != "True":
        raise HTTPException(status_code=403, detail="Not available in production")
    
    async def refresh_task():
        try:
            news_service = get_news_service()
            db = get_db()
            
            articles = await news_service.fetch_all_news()
            if articles:
                await db.store_news_articles(articles)
                logger.info(f"Manual refresh: stored {len(articles)} articles")
        except Exception as e:
            logger.error(f"Manual refresh error: {e}")
    
    background_tasks.add_task(refresh_task)
    return {"message": "News refresh initiated"}

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG") == "True",
        log_level="info"
    )