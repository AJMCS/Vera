#!/bin/bash
set -e

# Variables
PROJECT_ID="sentient-chat-hacks-2025"
SERVICE_NAME="vera"
REGION="us-west2"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

# Check for required environment variables
if [ -z "$MODEL_API_KEY" ] || [ -z "$TAVILY_API_KEY" ]; then
    echo "❌ Error: MODEL_API_KEY and TAVILY_API_KEY must be set"
    exit 1
fi

echo "🚀 Starting deployment process..."

# Build with platform specification
echo "📦 Building Docker image..."
docker buildx build --platform linux/amd64 -t $IMAGE_NAME .

# Push to Container Registry
echo "📤 Pushing image to Container Registry..."
gcloud auth configure-docker -q
docker push $IMAGE_NAME

# Deploy to Cloud Run with proper configuration
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars "MODEL_API_KEY=$MODEL_API_KEY,TAVILY_API_KEY=$TAVILY_API_KEY" \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --verbosity debug \
  --port 8080

echo "✅ Deployment complete!"
echo "🌐 Your service is now live at: $(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')" 