import logging
import os
from dotenv import load_dotenv
import sentient_agent_framework
from sentient_agent_framework.agent import AbstractAgent
from sentient_agent_framework.server import DefaultServer
from sentient_agent_framework.types import Session, Query
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uuid
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class SearchAgent(AbstractAgent):
    def __init__(self, name: str):
        super().__init__(name)
        # Initialize providers only if API keys are available
        self._model_provider = None
        self._search_provider = None
        
        model_api_key = os.getenv("MODEL_API_KEY")
        if model_api_key:
            try:
                from src.search_agent.providers.model_provider import ModelProvider
                self._model_provider = ModelProvider(api_key=model_api_key)
                logger.info("Model provider initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize model provider: {str(e)}")
        
        search_api_key = os.getenv("TAVILY_API_KEY")
        if search_api_key:
            try:
                from src.search_agent.providers.search_provider import SearchProvider
                self._search_provider = SearchProvider(api_key=search_api_key)
                logger.info("Search provider initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize search provider: {str(e)}")

    async def assist(self, session: Session, query: Query):
        try:
            # For now, just return a simple response
            response = {
                "response": f"Received query: {query.prompt}",
                "session_id": session.processor_id
            }
            
            # Add provider status to response
            if self._model_provider:
                response["model_provider"] = "available"
            else:
                response["model_provider"] = "not configured"
                
            if self._search_provider:
                response["search_provider"] = "available"
            else:
                response["search_provider"] = "not configured"
                
            return response
            
        except Exception as e:
            logger.error(f"Error in assist: {str(e)}", exc_info=True)
            raise

# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create agent instance
agent = SearchAgent(name="Vera")
server = DefaultServer(agent)

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/assist")
async def assist(request: Request):
    try:
        data = await request.json()
        query = data.get("query", {})
        session = data.get("session", {})
        
        # Create proper Query and Session objects
        query_obj = Query(
            id=query.get("id", str(uuid.uuid4())),
            prompt=query.get("prompt", "")
        )
        
        session_obj = Session(
            processor_id=session.get("processor_id", "Vera"),
            activity_id=session.get("activity_id", str(uuid.uuid4())),
            request_id=session.get("request_id", str(uuid.uuid4())),
            interactions=session.get("interactions", [])
        )
        
        # Process the query
        result = await agent.assist(session_obj, query_obj)
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    # Get port from Railway environment variable or use default
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    
    # Get host from Railway environment variable or use default
    host = os.environ.get("HOST", "0.0.0.0")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )