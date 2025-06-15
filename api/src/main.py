
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import base64
import uuid
from typing import Optional, Dict, Any
import json

from .config import settings, get_settings
from .dependencies import get_supabase_client, get_redis_client
from .routers import analysis, user, history
from .services.cache_service import CacheService
from .services.vision_service import VisionService
from .services.gemini_service import GeminiService
from .services.microsoft_vision_service import MicrosoftVisionService
from .services.google_shopping_service import GoogleShoppingService
from .services.marketplace_service import MarketplaceService
from .services.ebay_service import EbayService
from .agents.crew import ProductAnalysisCrew

# Initialize FastAPI app
app = FastAPI(
    title="Price Intelligence API",
    description="AI-powered product analysis and marketplace recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://*.replit.dev", "https://*.replit.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])
app.include_router(user.router, prefix="/api/v1", tags=["user"])
app.include_router(history.router, prefix="/api/v1", tags=["history"])

# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Price Intelligence API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test Redis connection
        redis_client = get_redis_client()
        await redis_client.ping()
        redis_status = "healthy"
    except Exception:
        redis_status = "unhealthy"
    
    try:
        # Test Supabase connection
        supabase = get_supabase_client()
        # Simple query to test connection
        result = supabase.table("users").select("count").execute()
        supabase_status = "healthy"
    except Exception:
        supabase_status = "unhealthy"
    
    return {
        "api": "healthy",
        "redis": redis_status,
        "supabase": supabase_status,
        "timestamp": asyncio.get_event_loop().time()
    }

# Background task for product analysis
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
        
        # Initialize services
        vision_service = VisionService(settings.GOOGLE_VISION_API_KEY, settings.OPENAI_API_KEY)
        gemini_service = GeminiService(settings.GOOGLE_GEMINI_API_KEY)
        microsoft_vision_service = MicrosoftVisionService(
            settings.MICROSOFT_VISION_API_KEY, 
            settings.MICROSOFT_VISION_ENDPOINT
        )
        google_shopping_service = GoogleShoppingService(settings.GOOGLE_SHOPPING_API_KEY)
        marketplace_service = MarketplaceService()
        
        # Stage 1: Image Analysis (Multiple AI Services)
        await cache_service.set_analysis(task_id, {
            "status": "processing",
            "stage": "image_analysis",
            "progress": 20
        })
        
        # Convert image to base64 for Gemini
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Run multiple vision analyses in parallel
        google_vision_task = vision_service.analyze_image(image_data)
        gemini_vision_task = gemini_service.analyze_product_image(image_base64, f"Condition: {condition}")
        microsoft_vision_task = microsoft_vision_service.analyze_product_specific(image_data)
        
        google_vision_result, gemini_vision_result, microsoft_vision_result = await asyncio.gather(
            google_vision_task, gemini_vision_task, microsoft_vision_task, return_exceptions=True
        )
        
        # Combine vision results
        vision_results = {
            "google_vision": google_vision_result if not isinstance(google_vision_result, Exception) else {"error": str(google_vision_result)},
            "gemini_vision": gemini_vision_result if not isinstance(gemini_vision_result, Exception) else {"error": str(gemini_vision_result)},
            "microsoft_vision": microsoft_vision_result if not isinstance(microsoft_vision_result, Exception) else {"error": str(microsoft_vision_result)}
        }
        
        # Stage 2: Product Identification
        await cache_service.set_analysis(task_id, {
            "status": "processing",
            "stage": "product_identification",
            "progress": 35
        })
        
        # Extract product information from vision results
        product_info = extract_product_info(vision_results, condition)
        
        # Stage 3: Market Research
        await cache_service.set_analysis(task_id, {
            "status": "processing",
            "stage": "market_research",
            "progress": 50
        })
        
        # Research product on multiple platforms
        product_name = product_info.get("name", "unknown product")
        category = product_info.get("category", "general")
        
        google_shopping_task = google_shopping_service.get_price_insights(product_name)
        marketplace_analysis_task = marketplace_service.analyze_all_marketplaces(product_name, category)
        gemini_market_task = gemini_service.research_product_market(product_name, category)
        
        google_shopping_result, marketplace_analysis_result, gemini_market_result = await asyncio.gather(
            google_shopping_task, marketplace_analysis_task, gemini_market_task, return_exceptions=True
        )
        
        # Stage 4: Price Analysis
        await cache_service.set_analysis(task_id, {
            "status": "processing",
            "stage": "price_analysis",
            "progress": 70
        })
        
        # Calculate price recommendations
        price_analysis = calculate_price_recommendations(
            google_shopping_result if not isinstance(google_shopping_result, Exception) else {},
            marketplace_analysis_result if not isinstance(marketplace_analysis_result, Exception) else [],
            product_info
        )
        
        # Stage 5: Platform Recommendations
        await cache_service.set_analysis(task_id, {
            "status": "processing",
            "stage": "platform_recommendations",
            "progress": 85
        })
        
        # Generate platform recommendations
        platform_recommendations = generate_platform_recommendations(
            product_info, 
            price_analysis,
            marketplace_analysis_result if not isinstance(marketplace_analysis_result, Exception) else []
        )
        
        # Stage 6: Content Generation
        await cache_service.set_analysis(task_id, {
            "status": "processing",
            "stage": "content_generation",
            "progress": 95
        })
        
        # Generate listing content
        content_generation_task = gemini_service.generate_product_description(
            product_info, 
            platform_recommendations[0]["name"] if platform_recommendations else "general"
        )
        
        content_result = await content_generation_task
        if isinstance(content_result, Exception):
            content_result = generate_fallback_content(product_info)
        
        # Final result compilation
        final_result = {
            "status": "completed",
            "task_id": task_id,
            "analysis_timestamp": asyncio.get_event_loop().time(),
            "product_identification": product_info,
            "price_analysis": price_analysis,
            "platform_recommendations": platform_recommendations,
            "generated_content": content_result,
            "vision_analysis": {
                "confidence_score": calculate_overall_confidence(vision_results),
                "sources_used": ["google_vision", "gemini_pro", "microsoft_vision"]
            },
            "market_data": {
                "google_shopping": google_shopping_result if not isinstance(google_shopping_result, Exception) else {},
                "gemini_insights": gemini_market_result if not isinstance(gemini_market_result, Exception) else {}
            }
        }
        
        # Store final result
        await cache_service.set_analysis(task_id, final_result)
        
        # Save to database (Supabase)
        supabase = get_supabase_client()
        try:
            supabase.table("analysis_history").insert({
                "user_id": user_id,
                "task_id": task_id,
                "product_name": product_info.get("name", "Unknown Product"),
                "category": product_info.get("category", "general"),
                "condition": condition,
                "estimated_price": price_analysis.get("recommended_price", 0),
                "top_platform": platform_recommendations[0]["name"] if platform_recommendations else "unknown",
                "confidence_score": calculate_overall_confidence(vision_results),
                "analysis_data": json.dumps(final_result),
                "created_at": "now()"
            }).execute()
        except Exception as db_error:
            print(f"Database save error: {db_error}")
        
    except Exception as e:
        # Handle errors
        error_result = {
            "status": "failed",
            "task_id": task_id,
            "error": str(e),
            "error_type": type(e).__name__
        }
        await cache_service.set_analysis(task_id, error_result)


def extract_product_info(vision_results: Dict[str, Any], condition: str) -> Dict[str, Any]:
    """Extract and combine product information from multiple vision services"""
    
    product_info = {
        "name": "Unknown Product",
        "brand": "",
        "category": "general",
        "condition": condition,
        "confidence_score": 0.0,
        "features": [],
        "colors": [],
        "materials": []
    }
    
    # Process Gemini results (highest priority for product identification)
    gemini_data = vision_results.get("gemini_vision", {})
    if "product_identification" in gemini_data:
        gemini_product = gemini_data["product_identification"]
        product_info.update({
            "name": gemini_product.get("name", product_info["name"]),
            "brand": gemini_product.get("brand", ""),
            "category": gemini_product.get("category", "general")
        })
    
    if "confidence_scores" in gemini_data:
        product_info["confidence_score"] = gemini_data["confidence_scores"].get("overall_analysis", 0.0)
    
    # Enhance with Google Vision data
    google_data = vision_results.get("google_vision", {})
    if "labels" in google_data:
        labels = [label["description"] for label in google_data["labels"][:5]]
        if product_info["name"] == "Unknown Product" and labels:
            product_info["name"] = labels[0]
    
    # Enhance with Microsoft Vision data
    microsoft_data = vision_results.get("microsoft_vision", {})
    if "general_analysis" in microsoft_data:
        ms_analysis = microsoft_data["general_analysis"]
        if "brands" in ms_analysis and ms_analysis["brands"]:
            product_info["brand"] = ms_analysis["brands"][0]["name"]
    
    return product_info


def calculate_price_recommendations(google_shopping_data: Dict, marketplace_data: List, product_info: Dict) -> Dict[str, Any]:
    """Calculate price recommendations based on market data"""
    
    prices = []
    
    # Extract prices from Google Shopping
    if "price_range" in google_shopping_data:
        price_range = google_shopping_data["price_range"]
        if price_range.get("average", 0) > 0:
            prices.extend([price_range["min"], price_range["average"], price_range["max"]])
    
    # Extract prices from marketplace data
    for marketplace in marketplace_data:
        if hasattr(marketplace, 'average_price') and marketplace.average_price:
            prices.append(marketplace.average_price)
        if hasattr(marketplace, 'price_range') and marketplace.price_range:
            prices.extend([marketplace.price_range.low, marketplace.price_range.median, marketplace.price_range.high])
    
    if not prices:
        # Fallback pricing based on category
        category_defaults = {
            "electronics": 150,
            "clothing": 50,
            "home": 75,
            "collectibles": 100,
            "books": 25,
            "toys": 40
        }
        base_price = category_defaults.get(product_info.get("category", "").lower(), 50)
        prices = [base_price * 0.7, base_price, base_price * 1.3]
    
    # Calculate recommendations
    min_price = min(prices)
    max_price = max(prices)
    avg_price = sum(prices) / len(prices)
    
    # Adjust for condition
    condition_multipliers = {
        "new": 1.0,
        "like new": 0.9,
        "very good": 0.8,
        "good": 0.7,
        "acceptable": 0.6,
        "poor": 0.4
    }
    
    condition = product_info.get("condition", "good").lower()
    multiplier = condition_multipliers.get(condition, 0.7)
    
    return {
        "price_range": {
            "low": round(min_price * multiplier, 2),
            "high": round(max_price * multiplier, 2),
            "average": round(avg_price * multiplier, 2)
        },
        "recommended_price": round(avg_price * multiplier, 2),
        "condition_adjustment": f"{int((1-multiplier)*100)}% reduction for {condition} condition",
        "data_sources": len(prices)
    }


def generate_platform_recommendations(product_info: Dict, price_analysis: Dict, marketplace_data: List) -> List[Dict[str, Any]]:
    """Generate platform recommendations with real fee calculations"""
    
    recommended_price = price_analysis.get("recommended_price", 50)
    category = product_info.get("category", "general").lower()
    
    # Platform data with real fee structures
    platforms = [
        {
            "name": "eBay",
            "fee_percentage": 13.25,
            "payment_fee": 2.9,
            "fixed_fee": 0.30,
            "suitability_score": 9 if category in ["electronics", "collectibles"] else 7,
            "audience": "Global marketplace with diverse buyers",
            "best_for": ["electronics", "collectibles", "vintage items"]
        },
        {
            "name": "Facebook Marketplace",
            "fee_percentage": 5.0,
            "payment_fee": 2.9,
            "fixed_fee": 0.30,
            "suitability_score": 8 if category in ["home", "electronics"] else 6,
            "audience": "Local buyers, good for pickup items",
            "best_for": ["furniture", "electronics", "local sales"]
        },
        {
            "name": "Mercari",
            "fee_percentage": 10.0,
            "payment_fee": 2.9,
            "fixed_fee": 0.30,
            "suitability_score": 8 if category in ["clothing", "electronics"] else 7,
            "audience": "Younger demographic, mobile-first",
            "best_for": ["clothing", "accessories", "small electronics"]
        },
        {
            "name": "Poshmark",
            "fee_percentage": 20.0,
            "payment_fee": 2.9,
            "fixed_fee": 0.30,
            "suitability_score": 9 if category == "clothing" else 3,
            "audience": "Fashion-focused, social selling",
            "best_for": ["clothing", "shoes", "accessories"]
        }
    ]
    
    # Calculate fees and profits for each platform
    recommendations = []
    for platform in platforms:
        platform_fee = (recommended_price * platform["fee_percentage"]) / 100
        payment_fee = (recommended_price * platform["payment_fee"]) / 100 + platform["fixed_fee"]
        total_fees = platform_fee + payment_fee
        net_profit = recommended_price - total_fees
        
        # Adjust suitability based on price range
        if recommended_price > 100:
            # Higher value items - prefer platforms with buyer protection
            if platform["name"] in ["eBay", "Poshmark"]:
                platform["suitability_score"] += 1
        elif recommended_price < 25:
            # Lower value items - prefer low fee platforms
            if platform["name"] in ["Facebook Marketplace", "Mercari"]:
                platform["suitability_score"] += 1
        
        recommendations.append({
            "name": platform["name"],
            "suitability_score": platform["suitability_score"],
            "estimated_fees": round(total_fees, 2),
            "estimated_profit": round(net_profit, 2),
            "fee_breakdown": {
                "platform_fee": round(platform_fee, 2),
                "payment_fee": round(payment_fee, 2),
                "total_fee_percentage": round((total_fees / recommended_price) * 100, 1)
            },
            "reasoning": f"Good fit for {category} items. {platform['audience']}",
            "audience": platform["audience"],
            "best_for": platform["best_for"]
        })
    
    # Sort by net profit (highest first)
    recommendations.sort(key=lambda x: x["estimated_profit"], reverse=True)
    
    return recommendations[:3]  # Return top 3 recommendations


def generate_fallback_content(product_info: Dict) -> Dict[str, Any]:
    """Generate fallback content when AI content generation fails"""
    
    name = product_info.get("name", "Product")
    condition = product_info.get("condition", "good")
    brand = product_info.get("brand", "")
    
    title = f"{brand} {name}" if brand else name
    if len(title) > 80:
        title = title[:77] + "..."
    
    description = f"This {name.lower()} is in {condition} condition."
    if brand:
        description += f" Made by {brand}."
    description += " Please see photos for details. Fast shipping and secure packaging guaranteed."
    
    return {
        "title": title,
        "description": description,
        "key_features": ["Good condition", "Fast shipping", "Secure packaging"],
        "tags": [name.lower(), brand.lower() if brand else "quality", condition],
        "condition_statement": f"Item is in {condition} condition as shown in photos."
    }


def calculate_overall_confidence(vision_results: Dict[str, Any]) -> float:
    """Calculate overall confidence score from multiple vision services"""
    
    confidence_scores = []
    
    # Gemini confidence
    gemini_data = vision_results.get("gemini_vision", {})
    if "confidence_scores" in gemini_data:
        confidence_scores.append(gemini_data["confidence_scores"].get("overall_analysis", 0.0))
    
    # Google Vision confidence (average of top labels)
    google_data = vision_results.get("google_vision", {})
    if "labels" in google_data and google_data["labels"]:
        label_confidences = [label.get("score", 0) for label in google_data["labels"][:3]]
        if label_confidences:
            confidence_scores.append(sum(label_confidences) / len(label_confidences))
    
    # Microsoft Vision confidence (average of top tags)
    microsoft_data = vision_results.get("microsoft_vision", {})
    if "general_analysis" in microsoft_data:
        ms_analysis = microsoft_data["general_analysis"]
        if "tags" in ms_analysis and ms_analysis["tags"]:
            tag_confidences = [tag.get("confidence", 0) for tag in ms_analysis["tags"][:3]]
            if tag_confidences:
                confidence_scores.append(sum(tag_confidences) / len(tag_confidences))
    
    if confidence_scores:
        return sum(confidence_scores) / len(confidence_scores)
    else:
        return 0.5  # Default moderate confidence


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
