#!/bin/bash

# Exit on error
set -e

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found"
    exit 1
fi

# Build the production image
echo "Building production Docker image..."
docker build -t voice-agent:prod -f Dockerfile.prod .

# Stop and remove existing container if it exists
echo "Stopping existing container if any..."
docker stop voice-agent-prod || true
docker rm voice-agent-prod || true

# Run the new container
echo "Starting production container..."
docker run -d \
    --name voice-agent-prod \
    --restart unless-stopped \
    --memory="2g" \
    --memory-swap="2g" \
    --cpus="1.0" \
    -p 7880:7880 \
    --env-file .env \
    voice-agent:prod

# Wait for container to start
echo "Waiting for container to start..."
sleep 10

# Check container status
echo "Container status:"
docker ps -f name=voice-agent-prod

# Show logs
echo "Container logs:"
docker logs voice-agent-prod 