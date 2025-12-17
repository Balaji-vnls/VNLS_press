import torch
import torch.nn as nn
import joblib
import numpy as np
from typing import List, Dict, Any
import os
from transformers import BertTokenizer, BertModel
import logging

logger = logging.getLogger(__name__)

class MultiTaskNewsModel(nn.Module):
    """Multi-task learning model for news recommendation"""
    def __init__(self, input_dim=768):
        super(MultiTaskNewsModel, self).__init__()
        self.shared_dropout = nn.Dropout(0.3)
        self.click_head = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )
        self.dwell_head = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

    def forward(self, x):
        x = self.shared_dropout(x)
        click_out = self.click_head(x)
        dwell_out = self.dwell_head(x)
        return click_out, dwell_out

class NewsRecommendationModel:
    """Wrapper class for the trained news recommendation model"""
    
    def __init__(self, model_path: str = "./mtl_model.pt"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.bert_model = None
        self.model_path = model_path
        self._load_model()
        self._load_bert()
        
    def _load_model(self):
        """Load the trained PyTorch model"""
        try:
            self.model = MultiTaskNewsModel()
            if os.path.exists(self.model_path):
                state_dict = torch.load(self.model_path, map_location=self.device)
                self.model.load_state_dict(state_dict)
                self.model.to(self.device)
                self.model.eval()
                logger.info(f"Model loaded successfully from {self.model_path}")
            else:
                logger.warning(f"Model file not found at {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def _load_bert(self):
        """Load BERT tokenizer and model for text encoding"""
        try:
            self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
            self.bert_model = BertModel.from_pretrained('bert-base-uncased')
            self.bert_model.to(self.device)
            self.bert_model.eval()
            logger.info("BERT model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading BERT: {e}")
            raise
    
    def encode_text(self, texts: List[str]) -> torch.Tensor:
        """Encode text using BERT to get 768-dimensional embeddings"""
        try:
            # Tokenize texts
            encoded = self.tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors='pt'
            )
            
            # Move to device
            input_ids = encoded['input_ids'].to(self.device)
            attention_mask = encoded['attention_mask'].to(self.device)
            
            # Get BERT embeddings
            with torch.no_grad():
                outputs = self.bert_model(input_ids=input_ids, attention_mask=attention_mask)
                # Use [CLS] token embedding
                embeddings = outputs.last_hidden_state[:, 0, :]
            
            return embeddings
        except Exception as e:
            logger.error(f"Error encoding text: {e}")
            raise
    
    def predict(self, news_texts: List[str], user_context: Dict[str, Any] = None) -> List[Dict[str, float]]:
        """
        Predict click probability and dwell time for news articles
        
        Args:
            news_texts: List of news article texts (title + content)
            user_context: User context information (optional)
            
        Returns:
            List of predictions with click_prob and dwell_score
        """
        try:
            if not self.model or not self.bert_model:
                raise ValueError("Model not loaded properly")
            
            # Encode news texts
            embeddings = self.encode_text(news_texts)
            
            # Get predictions
            with torch.no_grad():
                click_logits, dwell_scores = self.model(embeddings)
                
                # Convert to probabilities
                click_probs = torch.sigmoid(click_logits).cpu().numpy().flatten()
                dwell_scores = dwell_scores.cpu().numpy().flatten()
            
            # Format results
            predictions = []
            for i, (click_prob, dwell_score) in enumerate(zip(click_probs, dwell_scores)):
                predictions.append({
                    'article_index': i,
                    'click_probability': float(click_prob),
                    'dwell_score': float(dwell_score),
                    'recommendation_score': float(click_prob * 0.7 + (dwell_score / 10) * 0.3)  # Combined score
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
            raise
    
    def get_personalized_recommendations(self, 
                                       news_articles: List[Dict[str, Any]], 
                                       user_history: List[Dict[str, Any]] = None,
                                       top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Get personalized news recommendations for a user
        
        Args:
            news_articles: List of news articles with 'title', 'content', 'category', etc.
            user_history: User's reading history
            top_k: Number of recommendations to return
            
        Returns:
            Top-k recommended articles with scores
        """
        try:
            # Prepare text for encoding (title + content)
            news_texts = []
            for article in news_articles:
                text = f"{article.get('title', '')} {article.get('content', '')}"
                news_texts.append(text)
            
            # Get predictions
            predictions = self.predict(news_texts)
            
            # Combine predictions with article data
            recommendations = []
            for pred, article in zip(predictions, news_articles):
                recommendation = {
                    **article,
                    'click_probability': pred['click_probability'],
                    'dwell_score': pred['dwell_score'],
                    'recommendation_score': pred['recommendation_score']
                }
                recommendations.append(recommendation)
            
            # Sort by recommendation score and return top-k
            recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
            
            return recommendations[:top_k]
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            raise

# Global model instance
_model_instance = None

def get_model() -> NewsRecommendationModel:
    """Get singleton model instance"""
    global _model_instance
    if _model_instance is None:
        _model_instance = NewsRecommendationModel()
    return _model_instance