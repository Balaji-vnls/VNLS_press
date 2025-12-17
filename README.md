# 🏢 NARAYANASWAMY SONS - News Intelligence Platform

A production-ready, AI-powered news intelligence platform by Narayanaswamy Sons, built with advanced ML models, FastAPI backend, React frontend, and real-time news integration.

## ✨ Features

### 🤖 AI-Powered Recommendations
- **Multi-Task Learning Model**: Uses your existing PyTorch MTL model for click prediction and dwell time estimation
- **Real-time Inference**: Serves personalized recommendations using your trained model
- **Behavioral Learning**: Adapts to user reading patterns and preferences

### 📰 Real-Time News Ingestion
- **Multiple Sources**: NewsAPI, GNews, RSS feeds from trusted sources
- **Live Updates**: Continuous news fetching and database updates
- **No Dummy Data**: All news content is real and current

### 🔐 Full Authentication System
- **Supabase Auth**: Secure email/password authentication
- **Session Management**: JWT tokens with refresh capability
- **User Profiles**: Customizable preferences and reading history

### 🎯 Personalization Features
- **For You Feed**: Personalized news recommendations
- **Category Preferences**: Learn from user interactions
- **Reading History**: Track and analyze user behavior
- **Recommendation Scoring**: ML-driven relevance scoring

### 🏗️ Production Architecture
- **Scalable Backend**: FastAPI with async operations
- **Real-time Database**: Supabase with Row Level Security
- **Modern Frontend**: React with responsive design
- **Cloud Ready**: Docker and deployment configurations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Supabase account

### 1. Clone and Setup
```bash
git clone <repository-url>
cd news-recommendation-system
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials
```

### 3. Database Setup
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Create a new project
3. Run the SQL from `database_schema.sql` in the SQL Editor
4. Update `.env` with your Supabase URL and API key

### 4. Start Backend
```bash
python run_backend.py
```
Backend will be available at: https://vnls-press-backend.onrender.com

### 5. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will be available at: http://localhost:3000

## 📊 ML Model Integration

Your existing ML model files are automatically integrated:

### Model Files Used
- `mtl_model.py` - Multi-task model architecture
- `mtl_model.pt` - Trained PyTorch model weights
- `X_inputs.pkl` - Input feature encoders
- `y_click_labels.pkl` - Click prediction labels
- `y_relevance_labels.pkl` - Relevance/dwell time labels

### Model Features
- **Input**: 768-dimensional BERT embeddings from news text
- **Outputs**: Click probability + dwell time prediction
- **Architecture**: Shared layers with task-specific heads
- **Real-time**: Serves predictions via REST API

## 🗄️ Database Schema

### Core Tables
- `user_profiles` - User information and preferences
- `news_articles` - Real-time news content
- `user_interactions` - Click/read behavior tracking
- `recommendation_logs` - ML recommendation history

### Security
- Row Level Security (RLS) enabled
- User data isolation
- Secure API endpoints

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/signin` - User login
- `POST /api/auth/signout` - User logout
- `GET /api/auth/me` - Get current user

### News
- `GET /api/news/trending` - Trending news
- `GET /api/news/category/{category}` - Category news
- `GET /api/news/search` - Search news
- `POST /api/news/article/{id}/interact` - Log interaction

### Recommendations
- `GET /api/recommendations/personalized` - ML recommendations
- `GET /api/recommendations/for-you` - Personalized feed
- `GET /api/recommendations/similar/{id}` - Similar articles

## 🎨 Frontend Features

### Pages
- **Home**: Landing page with trending news
- **Feed**: Personalized "For You" recommendations
- **Categories**: Browse by news category
- **Article**: Full article view with interactions
- **Profile**: User preferences and history
- **Search**: Search across all news

### Components
- **Responsive Design**: Mobile-first approach
- **Real-time Updates**: Live news feed updates
- **Infinite Scroll**: Smooth content loading
- **Loading States**: Professional UX patterns

## 🔄 Real-Time Features

### News Updates
- Automatic news fetching every 30 minutes
- Background processing with FastAPI
- Duplicate detection and filtering

### User Interactions
- Real-time click/read tracking
- Immediate recommendation updates
- Behavioral pattern learning

## 🚀 Deployment

### Environment Variables
```bash
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# News APIs (optional)
NEWS_API_KEY=your_newsapi_key
GNEWS_API_KEY=your_gnews_key

# Security
SECRET_KEY=your_secret_key
```

### Docker Deployment
```bash
# Build and run with Docker
docker-compose up --build
```

### Cloud Deployment
- **Backend**: Deploy to AWS/GCP/Azure with Docker
- **Frontend**: Deploy to Vercel/Netlify
- **Database**: Supabase (already cloud-hosted)

## 📈 Monitoring & Analytics

### Built-in Analytics
- User engagement metrics
- Article popularity tracking
- Category preference analysis
- Recommendation performance

### Logging
- Structured logging with Python logging
- Error tracking and monitoring
- Performance metrics

## 🔒 Security Features

### Authentication
- JWT token-based authentication
- Secure password hashing
- Session management

### Data Protection
- Row Level Security (RLS)
- Input validation
- CORS protection
- Rate limiting ready

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: https://vnls-press-backend.onrender.com/docs
- **ReDoc**: https://vnls-press-backend.onrender.com/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

### Common Issues

**Model Loading Error**
- Ensure all `.pkl` and `.pt` files are in the root directory
- Check Python dependencies are installed

**Database Connection Error**
- Verify Supabase URL and API key in `.env`
- Run the database schema SQL in Supabase

**News API Errors**
- News APIs are optional - system works with RSS feeds
- Add API keys to `.env` for better coverage

### Getting Help
- Check the logs in the terminal
- Visit API docs at `/docs` endpoint
- Review database tables in Supabase dashboard

## 🎯 Next Steps

### Enhancements
- [ ] Add more news sources
- [ ] Implement push notifications
- [ ] Add social sharing features
- [ ] Create admin dashboard
- [ ] Add A/B testing framework

### Scaling
- [ ] Add Redis caching
- [ ] Implement CDN for images
- [ ] Add load balancing
- [ ] Set up monitoring alerts

---

**Built with ❤️ by NARAYANASWAMY SONS using advanced ML models, FastAPI, React, and real-time news APIs**