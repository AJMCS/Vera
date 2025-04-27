FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
COPY setup.py .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create the package structure
RUN mkdir -p search_agent/providers

# Copy the application files
COPY search_agent/src/search_agent/search_agent.py search_agent/
COPY search_agent/src/search_agent/providers/* search_agent/providers/
COPY search_agent/src/search_agent/__init__.py search_agent/
COPY search_agent/src/search_agent/providers/__init__.py search_agent/providers/

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8080

# Run the application
CMD ["uvicorn", "search_agent.search_agent:app", "--host", "0.0.0.0", "--port", "8080"] 