
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import asyncio
from contextlib import asynccontextmanager

from .config import settings
from .routers import analysis, user, history
from .dependencies import get_redis_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up Price Intelligence API")
    
    # Test Redis connection
    try:
        redis_client = await get_redis_client().__anext__()
        await redis_client.ping()
        logger.info("Redis connection successful")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
    
    # Test AI services
    try:
        from .services.gemini_service import GeminiService
        gemini = GeminiService()
        # Don't actually call the API during startup, just check if configured
        if gemini.api_key:
            logger.info("Gemini service configured")
        else:
            logger.warning("Gemini API key not configured")
    except Exception as e:
        logger.warning(f"Gemini service initialization failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Price Intelligence API")

# Create FastAPI app
app = FastAPI(
    title="Price Intelligence API",
    description="AI-powered product analysis and marketplace optimization",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "price-intelligence-api",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Price Intelligence API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

# Include routers
app.include_router(analysis.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(history.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
