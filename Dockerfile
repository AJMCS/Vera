FROM --platform=linux/amd64 python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY search_agent/requirements.txt .

# Install Python dependencies with verbose output
RUN pip install --no-cache-dir -r requirements.txt && \
    pip show sentient-agent-framework && \
    python -c "import sys; print('Python path:', sys.path)" && \
    python -c "import sentient_agent_framework; print('Framework location:', sentient_agent_framework.__file__)"

# Copy the search_agent directory with src structure
COPY search_agent/src /app/src

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV LOG_LEVEL=DEBUG

# Debug: List directory contents and verify Python path
RUN echo "Python path: $PYTHONPATH" && \
    python -c "import sys; print('Python sys.path:', sys.path)" && \
    ls -la /app && \
    echo "---" && \
    ls -la /app/src

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application with debug logging
CMD ["python", "-m", "src.search_agent.search_agent"]
