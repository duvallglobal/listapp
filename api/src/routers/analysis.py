
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import uuid
import asyncio
from datetime import datetime

from ..dependencies import get_current_user, get_redis_client, rate_limit_per_minute
from ..services.cache_service import CacheService
from ..services.vision_service import VisionService
from ..services.gemini_service import GeminiService
from ..services.microsoft_vision_service import MicrosoftVisionService
from ..services.google_shopping_service import GoogleShoppingService
from ..services.marketplace_service import MarketplaceService
from ..config import settings
from ..models.analysis import AnalysisRequest, AnalysisResponse

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("/upload", response_model=Dict[str, str])
async def upload_image_for_analysis(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    condition: str = Form(...),
    user = Depends(get_current_user),
    redis_client = Depends(get_redis_client),
    _rate_limit = Depends(rate_limit_per_minute)
):
    """Upload image and start analysis process"""
    
    # Validate file type
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Read image data
    image_data = await image.read()
    
    # Validate file size
    if len(image_data) > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large")
    
    # Initialize cache service
    cache_service = CacheService(redis_client)
    
    # Set initial status
    await cache_service.set_analysis(task_id, {
        "status": "queued",
        "stage": "upload_complete",
        "progress": 0,
        "user_id": user.id,
        "created_at": datetime.utcnow().isoformat()
    })
    
    # Start background analysis
    background_tasks.add_task(
        process_product_analysis,
        task_id,
        image_data,
        condition,
        user.id,
        cache_service
    )
    
    return {"task_id": task_id, "status": "processing"}

@router.get("/status/{task_id}")
async def get_analysis_status(
    task_id: str,
    user = Depends(get_current_user),
    redis_client = Depends(get_redis_client)
):
    """Get analysis status and results"""
    
    cache_service = CacheService(redis_client)
    analysis = await cache_service.get_analysis(task_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Verify ownership
    if analysis.get("user_id") != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return analysis

@router.get("/history")
async def get_analysis_history(
    limit: int = 20,
    offset: int = 0,
    user = Depends(get_current_user)
):
    """Get user's analysis history"""
    
    # Implementation would fetch from database
    # For now, return mock data structure
    return {
        "analyses": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }

async def process_product_analysis(
    task_id: str,
    image_data: bytes,
    condition: str,
    user_id: str,
    cache_service: CacheService
):
    """Background task to process product analysis"""
    
    try:
        # Update status to processing
        await cache_service.set_analysis(task_id, {
            "status": "processing",
            "stage": "initializing",
            "progress": 10
        })
        
        # Initialize AI services
        vision_service = VisionService(settings.GOOGLE_VISION_API_KEY, settings.OPENAI_API_KEY)
        gemini_service = GeminiService(settings.GOOGLE_GEMINI_API_KEY)
        microsoft_vision = MicrosoftVisionService(
            settings.MICROSOFT_VISION_API_KEY,
            settings.MICROSOFT_VISION_ENDPOINT
        )
        google_shopping = GoogleShoppingService(settings.GOOGLE_SHOPPING_API_KEY)
        marketplace_service = MarketplaceService()
        
        # Stage 1: Vision Analysis
        await cache_service.set_analysis(task_id, {
            "status": "processing",
            "stage": "vision_analysis",
            "progress": 25
        })
        
        # Run vision analyses in parallel
        vision_tasks = [
            vision_service.analyze_image(image_data),
            gemini_service.analyze_product_image(image_data, condition),
            microsoft_vision.analyze_product_specific(image_data)
        ]
        
        vision_results = await asyncio.gather(*vision_tasks, return_exceptions=True)
        
        # Stage 2: Market Research
        await cache_service.set_analysis(task_id, {
            "status": "processing", 
            "stage": "market_research",
            "progress": 50
        })
        
        # Extract product info from vision results
        product_name = "Product"  # Extract from vision results
        
        # Search for similar products
        market_data = await google_shopping.search_products(
            query=f"{product_name} {condition}",
            limit=10
        )
        
        # Stage 3: Price Analysis
        await cache_service.set_analysis(task_id, {
            "status": "processing",
            "stage": "price_analysis", 
            "progress": 75
        })
        
        # Generate pricing recommendations
        pricing_analysis = marketplace_service.analyze_pricing(market_data, condition)
        
        # Stage 4: Final Results
        await cache_service.set_analysis(task_id, {
            "status": "completed",
            "stage": "complete",
            "progress": 100,
            "results": {
                "vision_analysis": vision_results,
                "market_data": market_data,
                "pricing_analysis": pricing_analysis,
                "recommendations": {
                    "best_platforms": ["eBay", "Facebook Marketplace"],
                    "estimated_price": pricing_analysis.get("estimated_price", 0),
                    "confidence": pricing_analysis.get("confidence", 0.5)
                }
            },
            "completed_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        await cache_service.set_analysis(task_id, {
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })
