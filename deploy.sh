#!/bin/bash

# Default values
ENV=${1:-production}
DEBUG=${2:-false}
CONTAINER_NAME="voice-agent-${ENV}"

# Exit on error
set -e

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found"
    exit 1
fi

# Build the image
echo "Building Docker image for ${ENV} environment..."
docker build \
    --build-arg ENV=${ENV} \
    --build-arg DEBUG=${DEBUG} \
    -t voice-agent:${ENV} .

# Stop and remove existing container if it exists
echo "Stopping existing container if any..."
docker stop ${CONTAINER_NAME} || true
docker rm ${CONTAINER_NAME} || true

# Set resource limits based on environment
if [ "$ENV" = "production" ]; then
    MEMORY="2g"
    MEMORY_SWAP="2g"
    CPUS="1.0"
else
    MEMORY="1g"
    MEMORY_SWAP="1g"
    CPUS="0.5"
fi

# Run the container
echo "Starting container for ${ENV} environment..."
docker run -d \
    --name ${CONTAINER_NAME} \
    --restart unless-stopped \
    --memory=${MEMORY} \
    --memory-swap=${MEMORY_SWAP} \
    --cpus=${CPUS} \
    -p 7880:7880 \
    --env-file .env \
    voice-agent:${ENV}

# Wait for container to start
echo "Waiting for container to start..."
sleep 10

# Check container status
echo "Container status:"
docker ps -f name=${CONTAINER_NAME}

# Show logs
echo "Container logs:"
docker logs ${CONTAINER_NAME} 