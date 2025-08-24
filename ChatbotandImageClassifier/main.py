from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
from datetime import datetime

# Import your route modules
from routes.chat import router as chat_router
from routes.upload_Image import router as upload_router
from routes.user_uploaded_images import router as images_router
from routes.view_history import router as history_router

# Import database setup
from database import db_manager
from models import Base 

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Recycling & Sustainability Assistant API",
    description="AI-powered chatbot for waste management and sustainability guidance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - adjust origins based on your frontend deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        # Add your production domains here
        # "https://yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handler
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

# Global exception handler
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

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and perform startup tasks"""
    try:
        await db_manager.initialize()
        # Create tables
        async with db_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized and tables created successfully")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    logger.info("Application shutdown completed")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Recycling & Sustainability Assistant API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "chat": "/api/chat",
            "upload": "/api/upload", 
            "images": "/api/images",
            "history": "/api/history"
        }
    }

# Include all routers
app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(images_router)
app.include_router(history_router)

# Serve static files if you have any (optional)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Additional utility endpoints
@app.get("/api/status")
async def get_api_status():
    """Get API status and statistics"""
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
    """Endpoint for user feedback (you can implement storage/processing)"""
    logger.info(f"Received feedback: {feedback}")
    
    # Here you could:
    # - Store feedback in database
    # - Send to analytics service
    # - Process for improvements
    
    return {
        "message": "Thank you for your feedback!",
        "received_at": datetime.utcnow().isoformat()
    }

# Development server configuration
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info"
    )