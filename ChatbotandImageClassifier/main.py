from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime

# Database
from database import db_manager
from models import Base

# AI instances (imported here to initialize them before routes)
# from core.initializers import chatbot

# Routes (imported after AI instances to avoid circular imports)
from routes.chat import router as chat_router
from routes.upload_Image import router as upload_router
from routes.user_uploaded_images import router as images_router

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
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        # "https://your-production-domain.com",
    ],
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
        logger.info("✅ Chatbot & Agent initialized")
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
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(upload_router, prefix="/api/upload", tags=["Upload"])
app.include_router(images_router, prefix="/api/images", tags=["Images"])

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