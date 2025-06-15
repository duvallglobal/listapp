
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import JSONResponse
import uuid
import logging
from typing import Optional, Dict, Any
import asyncio

from ..dependencies import get_current_user, get_optional_user, get_redis_client
from ..models.analysis import AnalysisResponse, AnalysisRequest
from ..agents.crew import product_analysis_crew
from ..services.cache_service import CacheService

router = APIRouter(prefix="/analysis", tags=["analysis"])
logger = logging.getLogger(__name__)

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_product_image(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    estimated_cost: Optional[float] = Form(0.0),
    user = Depends(get_optional_user),
    redis_client = Depends(get_redis_client)
):
    """
    Analyze a product image and get pricing and platform recommendations
    
    This endpoint:
    1. Accepts an image file upload
    2. Runs the ProductAnalysisCrew workflow in the background
    3. Returns an analysis ID for status tracking
    4. Stores results in Redis cache when complete
    """
    
    try:
        # Validate image file
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image data
        image_data = await image.read()
        
        if len(image_data) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="Image file too large (max 10MB)")
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Initialize cache service
        cache_service = CacheService(redis_client)
        
        # Set initial status
        await cache_service.set_analysis_status(analysis_id, "processing", "Analysis started")
        
        # Start background analysis
        background_tasks.add_task(
            run_product_analysis,
            analysis_id,
            image_data,
            estimated_cost or 0.0,
            cache_service,
            user.id if user else None
        )
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="processing",
            message="Analysis started. Use the analysis_id to check status.",
            estimated_completion_time=120  # 2 minutes estimate
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start analysis")

async def run_product_analysis(
    analysis_id: str,
    image_data: bytes,
    estimated_cost: float,
    cache_service: CacheService,
    user_id: Optional[str] = None
):
    """Background task to run the complete product analysis"""
    
    try:
        logger.info(f"Starting product analysis {analysis_id}")
        
        # Update status
        await cache_service.set_analysis_status(
            analysis_id, 
            "processing", 
            "Running AI analysis workflow..."
        )
        
        # Run the CrewAI analysis
        result = await product_analysis_crew.analyze_product_image(image_data, estimated_cost)
        
        # Store complete results
        await cache_service.set_analysis_result(analysis_id, result)
        
        # Update status to completed
        await cache_service.set_analysis_status(
            analysis_id, 
            "completed", 
            "Analysis completed successfully"
        )
        
        # Store in user history if user is authenticated
        if user_id and result.get('confidence', 0) > 0.5:
            try:
                await store_user_analysis_history(user_id, analysis_id, result)
            except Exception as e:
                logger.warning(f"Failed to store user history: {str(e)}")
        
        logger.info(f"Analysis {analysis_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Analysis {analysis_id} failed: {str(e)}")
        
        # Store error result
        error_result = {
            "error": str(e),
            "analysis_id": analysis_id,
            "status": "failed"
        }
        
        await cache_service.set_analysis_result(analysis_id, error_result)
        await cache_service.set_analysis_status(
            analysis_id, 
            "failed", 
            f"Analysis failed: {str(e)}"
        )

@router.get("/status/{analysis_id}")
async def get_analysis_status(
    analysis_id: str,
    redis_client = Depends(get_redis_client)
):
    """Get the status of a running analysis"""
    
    try:
        cache_service = CacheService(redis_client)
        status = await cache_service.get_analysis_status(analysis_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analysis status")

@router.get("/result/{analysis_id}")
async def get_analysis_result(
    analysis_id: str,
    redis_client = Depends(get_redis_client)
):
    """Get the results of a completed analysis"""
    
    try:
        cache_service = CacheService(redis_client)
        
        # Check status first
        status = await cache_service.get_analysis_status(analysis_id)
        if not status:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        if status["status"] != "completed":
            return {
                "analysis_id": analysis_id,
                "status": status["status"],
                "message": status.get("message", "Analysis not completed")
            }
        
        # Get results
        result = await cache_service.get_analysis_result(analysis_id)
        if not result:
            raise HTTPException(status_code=404, detail="Analysis results not found")
        
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis result: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analysis result")

@router.delete("/result/{analysis_id}")
async def delete_analysis_result(
    analysis_id: str,
    user = Depends(get_current_user),
    redis_client = Depends(get_redis_client)
):
    """Delete analysis results (authenticated users only)"""
    
    try:
        cache_service = CacheService(redis_client)
        
        # Delete from cache
        await cache_service.delete_analysis(analysis_id)
        
        return {"message": "Analysis deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete analysis")

async def store_user_analysis_history(user_id: str, analysis_id: str, result: Dict[str, Any]):
    """Store analysis in user's history (placeholder for database integration)"""
    # This would integrate with your database to store user analysis history
    # For now, just log it
    logger.info(f"Would store analysis {analysis_id} for user {user_id}")
    
    # Example integration with Supabase would go here:
    # supabase_client = get_supabase_client()
    # await supabase_client.table("analysis_history").insert({
    #     "user_id": user_id,
    #     "analysis_id": analysis_id,
    #     "product_name": result.get("productName"),
    #     "recommended_platform": result.get("platformRecommendation", {}).get("recommendedPlatform"),
    #     "recommended_price": result.get("recommendedPricing", {}).get("suggestedPrice"),
    #     "analysis_data": result
    # })

@router.get("/history")
async def get_user_analysis_history(
    user = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """Get user's analysis history (placeholder)"""
    
    # This would query the database for user's analysis history
    # For now, return empty list
    return {
        "analyses": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }
