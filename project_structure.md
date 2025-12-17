# Personalized News Recommendation System

## Project Structure
```
news-recommendation-system/
├── backend/
│   ├── app.py                 # FastAPI main application
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ml_model.py        # ML model wrapper
│   │   └── database.py        # Supabase integration
│   ├── services/
│   │   ├── __init__.py
│   │   ├── news_service.py    # News API integration
│   │   ├── recommendation_service.py
│   │   └── auth_service.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── news.py
│   │   └── recommendations.py
│   └── utils/
│       ├── __init__.py
│       └── preprocessing.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   ├── package.json
│   └── index.html
├── ml_models/
│   ├── mtl_model.py          # Your existing model
│   ├── mtl_model.pt          # Your trained model
│   ├── X_inputs.pkl          # Your data files
│   ├── y_click_labels.pkl
│   └── y_relevance_labels.pkl
├── .env
├── requirements.txt
└── README.md
```