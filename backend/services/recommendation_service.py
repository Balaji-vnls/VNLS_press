from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict

from models.ml_model import get_model
from models.database import get_db

logger = logging.getLogger(__name__)

class RecommendationService:
    """Service for generating personalized news recommendations"""
    
    def __init__(self):
        self.ml_model = get_model()
        self.db = get_db()
        
        # Category weights for different user preferences
        self.category_weights = {
            "technology": 1.0,
            "business": 1.0,
            "health": 1.0,
            "science": 1.0,
            "general": 0.8,
            "sports": 0.7,
            "entertainment": 0.6
        }
    
    async def get_personalized_recommendations(self, 
                                            user_id: str, 
                                            articles: List[Dict[str, Any]], 
                                            top_k: int = 20) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations for a user
        
        Args:
            user_id: User identifier
            articles: List of available news articles
            top_k: Number of recommendations to return
            
        Returns:
            List of recommended articles with scores
        """
        try:
            if not articles:
                return []
            
            # Get user profile and history
            user_profile = await self.db.get_user_profile(user_id)
            user_interactions = await self.db.get_user_interactions(user_id, limit=100)
            
            # Get ML model predictions
            ml_recommendations = self.ml_model.get_personalized_recommendations(
                articles, 
                user_history=user_interactions,
                top_k=len(articles)  # Get scores for all articles
            )
            
            # Apply personalization factors
            personalized_recommendations = await self._apply_personalization(
                user_id, ml_recommendations, user_profile, user_interactions
            )
            
            # Sort by final score and return top-k
            personalized_recommendations.sort(
                key=lambda x: x.get('final_score', 0), 
                reverse=True
            )
            
            final_recommendations = personalized_recommendations[:top_k]
            
            # Log recommendations
            article_ids = [rec['id'] for rec in final_recommendations]
            scores = [rec.get('final_score', 0) for rec in final_recommendations]
            await self.db.log_recommendations(user_id, article_ids, scores)
            
            logger.info(f"Generated {len(final_recommendations)} recommendations for user {user_id}")
            return final_recommendations
            
        except Exception as e:
            logger.error(f"Error generating personalized recommendations: {e}")
            return articles[:top_k]  # Fallback to recent articles
    
    async def _apply_personalization(self, 
                                   user_id: str,
                                   ml_recommendations: List[Dict[str, Any]],
                                   user_profile: Optional[Dict[str, Any]],
                                   user_interactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply personalization factors to ML recommendations"""
        
        # Get user preferences
        category_preferences = await self._get_user_category_preferences(user_id, user_interactions)
        time_preferences = self._get_user_time_preferences(user_interactions)
        source_preferences = self._get_user_source_preferences(user_interactions)
        
        personalized_recommendations = []
        
        for article in ml_recommendations:
            # Start with ML model score
            base_score = article.get('recommendation_score', 0.5)
            
            # Apply category preference boost
            category_boost = self._calculate_category_boost(
                article.get('category', 'general'), 
                category_preferences
            )
            
            # Apply recency boost
            recency_boost = self._calculate_recency_boost(article.get('published_at'))
            
            # Apply source preference boost
            source_boost = self._calculate_source_boost(
                article.get('source', ''), 
                source_preferences
            )
            
            # Apply diversity penalty (avoid too many articles from same category/source)
            diversity_penalty = self._calculate_diversity_penalty(
                article, personalized_recommendations
            )
            
            # Calculate final score
            final_score = (
                base_score * 0.6 +  # ML model score (60%)
                category_boost * 0.2 +  # Category preference (20%)
                recency_boost * 0.1 +   # Recency (10%)
                source_boost * 0.05 +   # Source preference (5%)
                diversity_penalty * 0.05  # Diversity (5%)
            )
            
            article['final_score'] = final_score
            article['personalization_factors'] = {
                'base_score': base_score,
                'category_boost': category_boost,
                'recency_boost': recency_boost,
                'source_boost': source_boost,
                'diversity_penalty': diversity_penalty
            }
            
            personalized_recommendations.append(article)
        
        return personalized_recommendations
    
    async def _get_user_category_preferences(self, 
                                           user_id: str, 
                                           interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate user's category preferences based on interaction history"""
        try:
            category_counts = await self.db.get_user_category_preferences(user_id)
            
            if not category_counts:
                # Default preferences for new users
                return {
                    "technology": 0.8,
                    "business": 0.7,
                    "general": 0.6,
                    "health": 0.5,
                    "science": 0.5
                }
            
            # Normalize counts to preferences (0-1 scale)
            total_interactions = sum(category_counts.values())
            preferences = {}
            
            for category, count in category_counts.items():
                preferences[category] = min(count / total_interactions * 2, 1.0)
            
            return preferences
            
        except Exception as e:
            logger.error(f"Error calculating category preferences: {e}")
            return {}
    
    def _get_user_time_preferences(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze user's reading time patterns"""
        # Simple implementation - can be enhanced with more sophisticated analysis
        hour_counts = defaultdict(int)
        
        for interaction in interactions:
            try:
                timestamp = datetime.fromisoformat(interaction['timestamp'].replace('Z', '+00:00'))
                hour = timestamp.hour
                hour_counts[hour] += 1
            except:
                continue
        
        return dict(hour_counts)
    
    def _get_user_source_preferences(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate user's source preferences"""
        source_counts = defaultdict(int)
        
        for interaction in interactions:
            if 'news_articles' in interaction and interaction['news_articles']:
                source = interaction['news_articles'].get('source', '')
                if source:
                    source_counts[source] += 1
        
        # Normalize to 0-1 scale
        if source_counts:
            max_count = max(source_counts.values())
            return {source: count / max_count for source, count in source_counts.items()}
        
        return {}
    
    def _calculate_category_boost(self, article_category: str, category_preferences: Dict[str, float]) -> float:
        """Calculate category preference boost for an article"""
        base_weight = self.category_weights.get(article_category, 0.5)
        user_preference = category_preferences.get(article_category, 0.5)
        
        return base_weight * user_preference
    
    def _calculate_recency_boost(self, published_at: str) -> float:
        """Calculate recency boost based on article publication time"""
        try:
            pub_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            now = datetime.utcnow()
            hours_old = (now - pub_time).total_seconds() / 3600
            
            # Boost recent articles (within 24 hours)
            if hours_old <= 1:
                return 1.0
            elif hours_old <= 6:
                return 0.8
            elif hours_old <= 24:
                return 0.6
            elif hours_old <= 72:
                return 0.4
            else:
                return 0.2
                
        except:
            return 0.5  # Default for unparseable dates
    
    def _calculate_source_boost(self, article_source: str, source_preferences: Dict[str, float]) -> float:
        """Calculate source preference boost"""
        return source_preferences.get(article_source, 0.5)
    
    def _calculate_diversity_penalty(self, 
                                   article: Dict[str, Any], 
                                   existing_recommendations: List[Dict[str, Any]]) -> float:
        """Calculate diversity penalty to avoid too many similar articles"""
        if not existing_recommendations:
            return 1.0
        
        article_category = article.get('category', '')
        article_source = article.get('source', '')
        
        # Count similar articles in existing recommendations
        similar_category_count = sum(1 for rec in existing_recommendations 
                                   if rec.get('category') == article_category)
        similar_source_count = sum(1 for rec in existing_recommendations 
                                 if rec.get('source') == article_source)
        
        # Apply penalty for too many similar articles
        category_penalty = max(0.5, 1.0 - (similar_category_count * 0.1))
        source_penalty = max(0.5, 1.0 - (similar_source_count * 0.15))
        
        return min(category_penalty, source_penalty)
    
    async def get_trending_recommendations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get trending news recommendations (non-personalized)"""
        try:
            # Get recent articles from database
            recent_articles = await self.db.get_recent_news(limit=limit * 2)
            
            if not recent_articles:
                return []
            
            # Use ML model to score articles
            ml_recommendations = self.ml_model.get_personalized_recommendations(
                recent_articles, top_k=limit
            )
            
            # Add trending score based on recency and source credibility
            for article in ml_recommendations:
                recency_score = self._calculate_recency_boost(article.get('published_at', ''))
                source_credibility = self._get_source_credibility(article.get('source', ''))
                
                article['trending_score'] = (
                    article.get('recommendation_score', 0.5) * 0.6 +
                    recency_score * 0.3 +
                    source_credibility * 0.1
                )
            
            # Sort by trending score
            ml_recommendations.sort(key=lambda x: x.get('trending_score', 0), reverse=True)
            
            return ml_recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error getting trending recommendations: {e}")
            return []
    
    def _get_source_credibility(self, source: str) -> float:
        """Get credibility score for news source"""
        # Simple credibility mapping - can be enhanced with more sophisticated scoring
        credible_sources = {
            "Reuters": 1.0,
            "BBC": 1.0,
            "Associated Press": 1.0,
            "Bloomberg": 0.9,
            "CNN": 0.8,
            "TechCrunch": 0.8,
            "Wired": 0.8,
            "Nature": 1.0,
            "Science Daily": 0.9
        }
        
        return credible_sources.get(source, 0.6)  # Default credibility
    
    async def get_category_recommendations(self, 
                                         category: str, 
                                         user_id: str = None, 
                                         limit: int = 20) -> List[Dict[str, Any]]:
        """Get recommendations for a specific category"""
        try:
            # Get articles from the specified category
            category_articles = await self.db.get_recent_news(limit=limit * 2, category=category)
            
            if not category_articles:
                return []
            
            if user_id:
                # Get personalized recommendations for the category
                return await self.get_personalized_recommendations(user_id, category_articles, limit)
            else:
                # Get general recommendations for the category
                ml_recommendations = self.ml_model.get_personalized_recommendations(
                    category_articles, top_k=limit
                )
                return ml_recommendations
                
        except Exception as e:
            logger.error(f"Error getting category recommendations: {e}")
            return []

# Global recommendation service instance
_recommendation_service = None

def get_recommendation_service() -> RecommendationService:
    """Get singleton recommendation service instance"""
    global _recommendation_service
    if _recommendation_service is None:
        _recommendation_service = RecommendationService()
    return _recommendation_service