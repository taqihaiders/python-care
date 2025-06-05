# Use Python 3.12 as specified in README
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create a non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose the LiveKit WebSocket port
EXPOSE 7880

# Set environment variables
ENV LIVEKIT_URL=""
ENV LIVEKIT_API_KEY=""
ENV LIVEKIT_API_SECRET=""
ENV ANTHROPIC_API_KEY=""
ENV DEEPGRAM_API_KEY=""
ENV CARTESIA_API_KEY=""
ENV CARE_MANAGEMENT_BASE_URL=""
ENV CARE_MANAGEMENT_AUTH_TOKEN=""
ENV HOST="0.0.0.0"
ENV PORT="7880"

# Command to run the application
CMD ["python", "-m", "voice_agent", "start"] 