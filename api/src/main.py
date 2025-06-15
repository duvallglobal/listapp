from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
import logging
from contextlib import asynccontextmanager

from .config import settings
from .dependencies import get_redis_client, get_supabase_client
from .routers import analysis, user, history
from .services.stripe.webhook import stripe_webhook_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Price Intelligence API")
    
    # Initialize services
    try:
        redis_client = await get_redis_client()
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
    
    try:
        supabase = get_supabase_client()
        logger.info("Supabase client initialized")
    except Exception as e:
        logger.error(f"Supabase initialization failed: {e}")
    
    yield
    
    logger.info("Shutting down Price Intelligence API")

# Create FastAPI app
app = FastAPI(
    title="Price Intelligence API",
    description="AI-powered product analysis and pricing intelligence platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://vigorous-johnson8-5agwa.view-3.tempo-dev.app",
        settings.FRONTEND_URL
    ] if settings.FRONTEND_URL else [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://vigorous-johnson8-5agwa.view-3.tempo-dev.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(user.router, prefix="/api/v1/user", tags=["user"])
app.include_router(history.router, prefix="/api/v1/history", tags=["history"])
app.include_router(stripe_webhook_router, prefix="/api/v1/stripe", tags=["stripe"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Price Intelligence API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    health_status = {
        "api": "healthy",
        "redis": "unknown",
        "supabase": "unknown"
    }
    
    # Check Redis
    try:
        redis_client = await get_redis_client()
        await redis_client.ping()
        health_status["redis"] = "healthy"
    except Exception as e:
        health_status["redis"] = f"unhealthy: {str(e)}"
    
    # Check Supabase
    try:
        supabase = get_supabase_client()
        # Simple query to test connection
        result = supabase.table("users").select("count", count="exact").execute()
        health_status["supabase"] = "healthy"
    except Exception as e:
        health_status["supabase"] = f"unhealthy: {str(e)}"
    
    return health_status

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )
