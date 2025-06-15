
import aiohttp
import asyncio
import json
from typing import Dict, List, Any, Optional
import base64

from ..config import settings


class MicrosoftVisionService:
    """Service for Microsoft Computer Vision API"""
    
    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        self.api_key = api_key or settings.MICROSOFT_VISION_API_KEY
        self.endpoint = endpoint or settings.MICROSOFT_VISION_ENDPOINT
        self.api_version = "2023-02-01-preview"
        
    async def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze image using Microsoft Computer Vision"""
        
        url = f"{self.endpoint}/vision/v3.2/analyze"
        
        params = {
            "visualFeatures": "Categories,Description,Objects,Brands,Tags,Adult,Color,ImageType,Faces",
            "details": "Landmarks,Celebrities",
            "language": "en"
        }
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/octet-stream"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params, data=image_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_analysis_results(data)
                else:
                    error_text = await response.text()
                    raise Exception(f"Microsoft Vision API error: {response.status} - {error_text}")
    
    async def read_text_from_image(self, image_data: bytes) -> Dict[str, Any]:
        """Extract text from image using Microsoft OCR"""
        
        # Start the read operation
        read_url = f"{self.endpoint}/vision/v3.2/read/analyze"
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/octet-stream"
        }
        
        async with aiohttp.ClientSession() as session:
            # Submit image for processing
            async with session.post(read_url, data=image_data, headers=headers) as response:
                if response.status == 202:
                    operation_location = response.headers.get("Operation-Location")
                    if not operation_location:
                        raise Exception("No operation location returned")
                    
                    # Poll for results
                    return await self._poll_read_results(session, operation_location)
                else:
                    error_text = await response.text()
                    raise Exception(f"Microsoft Read API error: {response.status} - {error_text}")
    
    async def _poll_read_results(self, session: aiohttp.ClientSession, operation_url: str) -> Dict[str, Any]:
        """Poll for OCR results"""
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key
        }
        
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            await asyncio.sleep(1)  # Wait 1 second between polls
            
            async with session.get(operation_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get("status")
                    
                    if status == "succeeded":
                        return self._process_read_results(data)
                    elif status == "failed":
                        raise Exception("Text extraction failed")
                    # If running, continue polling
                else:
                    error_text = await response.text()
                    raise Exception(f"Polling error: {response.status} - {error_text}")
            
            attempt += 1
        
        raise Exception("Text extraction timed out")
    
    async def detect_objects(self, image_data: bytes) -> Dict[str, Any]:
        """Detect objects in image"""
        
        url = f"{self.endpoint}/vision/v3.2/detect"
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/octet-stream"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=image_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_object_detection(data)
                else:
                    error_text = await response.text()
                    raise Exception(f"Microsoft Object Detection error: {response.status} - {error_text}")
    
    async def analyze_product_specific(self, image_data: bytes) -> Dict[str, Any]:
        """Comprehensive product analysis combining multiple Microsoft Vision features"""
        
        # Run multiple analyses in parallel
        analysis_task = self.analyze_image(image_data)
        text_task = self.read_text_from_image(image_data)
        objects_task = self.detect_objects(image_data)
        
        try:
            analysis_result, text_result, objects_result = await asyncio.gather(
                analysis_task, text_task, objects_task, return_exceptions=True
            )
            
            # Combine results
            combined_result = {
                "general_analysis": analysis_result if not isinstance(analysis_result, Exception) else {"error": str(analysis_result)},
                "text_extraction": text_result if not isinstance(text_result, Exception) else {"error": str(text_result)},
                "object_detection": objects_result if not isinstance(objects_result, Exception) else {"error": str(objects_result)},
                "product_insights": self._generate_product_insights(analysis_result, text_result, objects_result)
            }
            
            return combined_result
            
        except Exception as e:
            return {"error": f"Microsoft Vision analysis failed: {str(e)}"}
    
    def _process_analysis_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process general analysis results"""
        
        processed = {
            "categories": [],
            "tags": [],
            "description": {},
            "objects": [],
            "brands": [],
            "colors": {},
            "image_properties": {}
        }
        
        # Categories
        if "categories" in data:
            processed["categories"] = [
                {
                    "name": cat.get("name", ""),
                    "score": cat.get("score", 0),
                    "detail": cat.get("detail", {})
                }
                for cat in data["categories"]
            ]
        
        # Tags
        if "tags" in data:
            processed["tags"] = [
                {
                    "name": tag.get("name", ""),
                    "confidence": tag.get("confidence", 0)
                }
                for tag in data["tags"]
            ]
        
        # Description
        if "description" in data:
            processed["description"] = {
                "captions": data["description"].get("captions", []),
                "tags": data["description"].get("tags", [])
            }
        
        # Objects
        if "objects" in data:
            processed["objects"] = [
                {
                    "object": obj.get("object", ""),
                    "confidence": obj.get("confidence", 0),
                    "rectangle": obj.get("rectangle", {})
                }
                for obj in data["objects"]
            ]
        
        # Brands
        if "brands" in data:
            processed["brands"] = [
                {
                    "name": brand.get("name", ""),
                    "confidence": brand.get("confidence", 0),
                    "rectangle": brand.get("rectangle", {})
                }
                for brand in data["brands"]
            ]
        
        # Colors
        if "color" in data:
            processed["colors"] = {
                "dominant_color_foreground": data["color"].get("dominantColorForeground"),
                "dominant_color_background": data["color"].get("dominantColorBackground"),
                "dominant_colors": data["color"].get("dominantColors", []),
                "accent_color": data["color"].get("accentColor"),
                "is_black_and_white": data["color"].get("isBwImg", False)
            }
        
        return processed
    
    def _process_read_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process OCR results"""
        
        extracted_text = []
        full_text = ""
        
        analyze_result = data.get("analyzeResult", {})
        read_results = analyze_result.get("readResults", [])
        
        for page in read_results:
            for line in page.get("lines", []):
                text = line.get("text", "")
                extracted_text.append({
                    "text": text,
                    "bounding_box": line.get("boundingBox", []),
                    "words": line.get("words", [])
                })
                full_text += text + " "
        
        return {
            "extracted_text": extracted_text,
            "full_text": full_text.strip(),
            "total_lines": len(extracted_text)
        }
    
    def _process_object_detection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process object detection results"""
        
        objects = []
        for obj in data.get("objects", []):
            objects.append({
                "object": obj.get("object", ""),
                "confidence": obj.get("confidence", 0),
                "rectangle": obj.get("rectangle", {}),
                "parent": obj.get("parent", {})
            })
        
        return {
            "objects": objects,
            "total_objects": len(objects)
        }
    
    def _generate_product_insights(self, analysis_result: Dict, text_result: Dict, objects_result: Dict) -> Dict[str, Any]:
        """Generate product-specific insights from combined results"""
        
        if isinstance(analysis_result, Exception) or isinstance(text_result, Exception) or isinstance(objects_result, Exception):
            return {"error": "Unable to generate insights due to API errors"}
        
        insights = {
            "identified_brands": [],
            "product_categories": [],
            "text_clues": [],
            "condition_indicators": [],
            "notable_features": []
        }
        
        # Extract brands
        if "brands" in analysis_result:
            insights["identified_brands"] = [brand["name"] for brand in analysis_result["brands"]]
        
        # Extract product categories
        if "categories" in analysis_result:
            insights["product_categories"] = [cat["name"] for cat in analysis_result["categories"] if cat["score"] > 0.5]
        
        # Extract text clues for product identification
        if "full_text" in text_result:
            text = text_result["full_text"]
            # Look for model numbers, sizes, etc.
            import re
            model_patterns = re.findall(r'\b[A-Z0-9\-]{3,}\b', text)
            insights["text_clues"] = model_patterns[:5]  # Limit to 5 potential clues
        
        # Analyze condition based on tags and description
        if "tags" in analysis_result:
            condition_tags = [tag["name"] for tag in analysis_result["tags"] 
                            if any(word in tag["name"].lower() for word in ["new", "used", "worn", "damaged", "pristine", "mint"])]
            insights["condition_indicators"] = condition_tags
        
        # Notable features from objects and tags
        if "objects" in objects_result:
            notable_objects = [obj["object"] for obj in objects_result["objects"] if obj["confidence"] > 0.7]
            insights["notable_features"].extend(notable_objects)
        
        return insights
