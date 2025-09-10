from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime

# Database
from services.db.postgres import db_manager
from services.models import Base

# Routes 
from api.chat import router as chat_router

from langsmith.run_helpers import traceable, get_current_run_tree
from config import LANGSMITH_API_KEY
import yaml


# use langsmith client
from langsmith import Client
client = Client(api_key=LANGSMITH_API_KEY)

YAML_PATH = "services/utils/chatbot_prompt.yaml"


async def load_and_save_system_prompt():
    """Load system prompt from LangSmith and save to YAML file."""
    try:
        prompt = client.pull_prompt("dawaragent")

        # Convert to string
        if hasattr(prompt, "format"):  # ChatPromptTemplate
            system_prompt_str = prompt.format(question="")
        elif hasattr(prompt, "to_string"):  # PromptValue
            system_prompt_str = prompt.to_string()
        elif isinstance(prompt, str):
            system_prompt_str = prompt
        else:
            system_prompt_str = str(prompt)

        # Write to YAML
        data = {"system_prompt": system_prompt_str}
        with open(YAML_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)

        print(f"✅ System prompt loaded from LangSmith and saved to YAML at {YAML_PATH}")
        return system_prompt_str

    except Exception as e:
        print(f"⚠️ Failed to load system prompt from LangSmith: {e}")
        return None

# ----------------------------------------------------
# Logging
# ----------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ----------------------------------------------------
# FastAPI App
# ----------------------------------------------------
app = FastAPI(
    title="Recycling & Sustainability Assistant API",
    description="AI-powered chatbot for waste management and sustainability guidance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# AI instances are now imported from core.initializers

# ----------------------------------------------------
# Middleware
# ----------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # or your frontend domain(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# Exception Handlers
# ----------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )

# ----------------------------------------------------
# Startup & Shutdown
# ----------------------------------------------------
@app.on_event("startup")
async def startup_event():
    """Initialize database and AI services"""
    try:
        await db_manager.initialize()
        async with db_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database initialized and tables created successfully")

        # 2) Load and overwrite system prompt
        await load_and_save_system_prompt()
        logger.info("✅ system_prompt")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup database connections"""
    try:
        await db_manager.close()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")
    logger.info("Application shutdown completed")

# ----------------------------------------------------
# Meta Endpoints
# ----------------------------------------------------
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {
        "message": "Recycling & Sustainability Assistant API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "chat": "/api/chat",
            "upload": "/api/upload", 
            "images": "/api/images"
        }
    }

@app.get("/api/status")
async def get_api_status():
    return {
        "api_status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "chat": True,
            "image_upload": True,
            "image_classification": True,
            "conversation_history": True,
            "export_data": True
        },
        "ai_services": {
            "gemini_chatbot": True,
            "waste_management_agent": True
        }
    }

@app.post("/api/feedback")
async def submit_feedback(feedback: dict):
    logger.info(f"Received feedback: {feedback}")
    return {
        "message": "Thank you for your feedback!",
        "received_at": datetime.utcnow().isoformat()
    }

# ----------------------------------------------------
# Routers
# ----------------------------------------------------
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
#app.include_router(upload_router, prefix="/api/upload", tags=["Upload"])

# ----------------------------------------------------
# Run Server
# ----------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )