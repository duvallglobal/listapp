from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import base64
import os
from dotenv import load_dotenv
from .config import Settings
from .dependencies import get_api_keys, get_cache_service
from .agents.crew import ProductAnalysisCrew
from .routers import analysis, user, history

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Price Intelligence API",
    description="API for analyzing products and providing pricing intelligence",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router)
app.include_router(user.router)
app.include_router(history.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Price Intelligence API"}

@app.post("/analyze")
async def analyze_product(
    image: UploadFile = File(...),
    condition: str = Form(None),
    api_keys = Depends(get_api_keys),
    cache_service = Depends(get_cache_service)
):
    """
    Analyze a product image and return detailed information
    """
    try:
        # Read and encode image
        contents = await image.read()
        image_data = base64.b64encode(contents).decode("utf-8")
        
        # Create crew and analyze product
        crew = ProductAnalysisCrew(api_keys, cache_service)
        result = crew.analyze_product(image_data, {"condition": condition})
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
