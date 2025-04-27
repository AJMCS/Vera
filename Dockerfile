FROM --platform=linux/amd64 python:3.11-slim



# Copy requirements and install dependencies
RUN apt update
RUN apt install git -y


# Copy source code
RUN git clone https://github.com/AJMCS/Vera.git /app

WORKDIR /app/search_agent

RUN pip install --no-cache-dir -r requirements.txt

# Cloud Run will set PORT=8080, but we set a default for local testing
ENV PORT=8080

# Expose the port the app runs on
EXPOSE 8080

WORKDIR /app/search_agent
# Command to run the application
CMD ["python", "-m", "src.search_agent.search_agent"]
