import requests
import feedparser
from typing import List, Dict, Any, Optional
import os
from datetime import datetime, timedelta
import hashlib
import logging
import asyncio
import aiohttp

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

logger = logging.getLogger(__name__)

class NewsService:
    """Service for fetching real-time news from multiple sources"""
    
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.gnews_api_key = os.getenv("GNEWS_API_KEY")
        
        # RSS feeds for different categories
        self.rss_feeds = {
            "technology": [
                "https://feeds.feedburner.com/oreilly/radar",
                "https://techcrunch.com/feed/",
                "https://www.wired.com/feed/rss",
                "https://feeds.arstechnica.com/arstechnica/index"
            ],
            "business": [
                "https://feeds.bloomberg.com/markets/news.rss",
                "https://www.reuters.com/business/finance/rss",
                "https://feeds.fortune.com/fortune/headlines"
            ],
            "health": [
                "https://feeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC",
                "https://www.medicalnewstoday.com/rss"
            ],
            "science": [
                "https://feeds.nature.com/nature/rss/current",
                "https://www.sciencedaily.com/rss/all.xml"
            ],
            "general": [
                "https://feeds.bbci.co.uk/news/rss.xml",
                "https://rss.cnn.com/rss/edition.rss",
                "https://feeds.reuters.com/reuters/topNews"
            ]
        }
    
    def generate_article_id(self, title: str, source: str, published_at: str) -> str:
        """Generate unique article ID"""
        content = f"{title}_{source}_{published_at}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def clean_html(self, html_content: str) -> str:
        """Clean HTML content and extract text"""
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text().strip()
    
    async def fetch_from_newsapi(self, category: str = "general", page_size: int = 50) -> List[Dict[str, Any]]:
        """Fetch news from NewsAPI"""
        if not self.news_api_key:
            logger.warning("NewsAPI key not configured")
            return []
        
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "apiKey": self.news_api_key,
                "category": category,
                "language": "en",
                "pageSize": page_size,
                "sortBy": "publishedAt"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = []
                        
                        for article in data.get("articles", []):
                            if article.get("title") and article.get("description"):
                                processed_article = {
                                    "id": self.generate_article_id(
                                        article["title"], 
                                        article.get("source", {}).get("name", "NewsAPI"),
                                        article.get("publishedAt", "")
                                    ),
                                    "title": article["title"],
                                    "content": article.get("description", "") + " " + (article.get("content", "") or ""),
                                    "summary": article.get("description", ""),
                                    "url": article.get("url", ""),
                                    "source": article.get("source", {}).get("name", "NewsAPI"),
                                    "category": category,
                                    "published_at": article.get("publishedAt", datetime.utcnow().isoformat()),
                                    "image_url": article.get("urlToImage"),
                                    "author": article.get("author")
                                }
                                articles.append(processed_article)
                        
                        logger.info(f"Fetched {len(articles)} articles from NewsAPI")
                        return articles
                    else:
                        logger.error(f"NewsAPI error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching from NewsAPI: {e}")
            return []
    
    async def fetch_from_gnews(self, category: str = "general", max_articles: int = 50) -> List[Dict[str, Any]]:
        """Fetch news from GNews API"""
        if not self.gnews_api_key:
            logger.warning("GNews API key not configured")
            return []
        
        try:
            url = "https://gnews.io/api/v4/top-headlines"
            params = {
                "token": self.gnews_api_key,
                "lang": "en",
                "country": "us",
                "max": max_articles,
                "category": category
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = []
                        
                        for article in data.get("articles", []):
                            if article.get("title") and article.get("description"):
                                processed_article = {
                                    "id": self.generate_article_id(
                                        article["title"], 
                                        article.get("source", {}).get("name", "GNews"),
                                        article.get("publishedAt", "")
                                    ),
                                    "title": article["title"],
                                    "content": article.get("description", "") + " " + (article.get("content", "") or ""),
                                    "summary": article.get("description", ""),
                                    "url": article.get("url", ""),
                                    "source": article.get("source", {}).get("name", "GNews"),
                                    "category": category,
                                    "published_at": article.get("publishedAt", datetime.utcnow().isoformat()),
                                    "image_url": article.get("image")
                                }
                                articles.append(processed_article)
                        
                        logger.info(f"Fetched {len(articles)} articles from GNews")
                        return articles
                    else:
                        logger.error(f"GNews error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching from GNews: {e}")
            return []
    
    async def fetch_from_rss(self, category: str = "general", max_articles: int = 20) -> List[Dict[str, Any]]:
        """Fetch news from RSS feeds"""
        try:
            feeds = self.rss_feeds.get(category, self.rss_feeds["general"])
            all_articles = []
            
            for feed_url in feeds:
                try:
                    # Parse RSS feed
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:max_articles]:
                        if hasattr(entry, 'title') and hasattr(entry, 'summary'):
                            # Extract content
                            content = ""
                            if hasattr(entry, 'content'):
                                content = entry.content[0].value if entry.content else ""
                            elif hasattr(entry, 'description'):
                                content = entry.description
                            else:
                                content = entry.summary
                            
                            # Clean HTML content
                            content = self.clean_html(content)
                            summary = self.clean_html(entry.summary)
                            
                            published_at = datetime.utcnow().isoformat()
                            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                published_at = datetime(*entry.published_parsed[:6]).isoformat()
                            
                            processed_article = {
                                "id": self.generate_article_id(
                                    entry.title,
                                    feed.feed.get("title", "RSS"),
                                    published_at
                                ),
                                "title": entry.title,
                                "content": content,
                                "summary": summary,
                                "url": entry.link if hasattr(entry, 'link') else "",
                                "source": feed.feed.get("title", "RSS Feed"),
                                "category": category,
                                "published_at": published_at,
                                "author": entry.get("author", "")
                            }
                            all_articles.append(processed_article)
                
                except Exception as e:
                    logger.error(f"Error parsing RSS feed {feed_url}: {e}")
                    continue
            
            logger.info(f"Fetched {len(all_articles)} articles from RSS feeds")
            return all_articles[:max_articles]
            
        except Exception as e:
            logger.error(f"Error fetching from RSS: {e}")
            return []
    
    async def fetch_all_news(self, categories: List[str] = None, max_per_source: int = 30) -> List[Dict[str, Any]]:
        """Fetch news from all available sources"""
        if categories is None:
            categories = ["general", "technology", "business", "health", "science"]
        
        all_articles = []
        
        for category in categories:
            try:
                # Fetch from multiple sources concurrently
                tasks = [
                    self.fetch_from_newsapi(category, max_per_source),
                    self.fetch_from_gnews(category, max_per_source),
                    self.fetch_from_rss(category, max_per_source)
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, list):
                        all_articles.extend(result)
                    elif isinstance(result, Exception):
                        logger.error(f"Error in news fetching task: {result}")
                
            except Exception as e:
                logger.error(f"Error fetching news for category {category}: {e}")
        
        # Remove duplicates based on title similarity
        unique_articles = self._remove_duplicates(all_articles)
        
        logger.info(f"Fetched total {len(unique_articles)} unique articles")
        return unique_articles
    
    def _remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate articles based on title similarity"""
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            title_lower = article["title"].lower().strip()
            # Simple duplicate detection - can be improved with fuzzy matching
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_articles.append(article)
        
        return unique_articles
    
    async def get_trending_news(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get trending news articles"""
        try:
            # For now, return recent articles from all sources
            # In production, this could be based on engagement metrics
            articles = await self.fetch_all_news(max_per_source=20)
            
            # Sort by published date (most recent first)
            articles.sort(key=lambda x: x.get("published_at", ""), reverse=True)
            
            return articles[:limit]
        except Exception as e:
            logger.error(f"Error getting trending news: {e}")
            return []

# Global news service instance
_news_service = None

def get_news_service() -> NewsService:
    """Get singleton news service instance"""
    global _news_service
    if _news_service is None:
        _news_service = NewsService()
    return _news_service