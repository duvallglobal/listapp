from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os

from src.routers import analysis, history, user
from src.config import get_settings
from src.dependencies import get_cache_service, get_vision_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Product Intelligence API...")
    yield
    # Shutdown
    print("Shutting down Product Intelligence API...")


app = FastAPI(
    title="Product Intelligence API",
    description="AI-powered product analysis and marketplace recommendations",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(history.router, prefix="/api/v1/history", tags=["history"])
app.include_router(user.router, prefix="/api/v1/user", tags=["user"])


@app.get("/")
async def root():
    return {"message": "Product Intelligence API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "product-intelligence-api"}


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )