FROM --platform=linux/amd64 python:3.11-slim

#WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt install git

# Copy source code
RUN git clone https://github.com/AJMCS/Vera.git

# Cloud Run will set PORT=8080, but we set a default for local testing
ENV PORT=8080

# Expose the port the app runs on
EXPOSE 8080

#WORKDIR /app/Vera
# Command to run the application
CMD ["python", "-m", "src.search_agent.search_agent"]
