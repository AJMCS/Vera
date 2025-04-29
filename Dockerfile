FROM python:3.13-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the application files
COPY search_agent/src/search_agent ./search_agent
COPY search_agent/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create the package structure
RUN mkdir -p search_agent/providers

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8080
ENV MODEL_API_KEY="fw_3Zn8kNDzBpMtckSRHxwUR4jd"
ENV TAVILY_API_KEY="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"

# Run the application
CMD ["python3", "-m", "search_agent.search_agent"]