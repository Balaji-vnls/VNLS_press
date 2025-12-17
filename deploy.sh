#!/bin/bash

# News Recommendation System Deployment Script

set -e

echo "🚀 Deploying News Recommendation System..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one with your configuration."
    exit 1
fi

# Load environment variables
source .env

# Check required environment variables
required_vars=("SUPABASE_URL" "SUPABASE_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set"
        exit 1
    fi
done

echo "✅ Environment variables validated"

# Check if model files exist
model_files=("mtl_model.py" "mtl_model.pt" "X_inputs.pkl" "y_click_labels.pkl" "y_relevance_labels.pkl")
for file in "${model_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Model file $file not found"
        exit 1
    fi
done

echo "✅ Model files validated"

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running successfully!"
    echo ""
    echo "🌐 Application URLs:"
    echo "   - API: https://vnls-press-backend.onrender.com"
    echo "   - API Docs: https://vnls-press-backend.onrender.com/docs"
    echo "   - Health Check: https://vnls-press-backend.onrender.com/health"
    echo ""
    echo "📊 View logs with: docker-compose logs -f"
    echo "🛑 Stop services with: docker-compose down"
else
    echo "❌ Services failed to start. Check logs with: docker-compose logs"
    exit 1
fi