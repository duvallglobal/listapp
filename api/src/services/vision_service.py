
import asyncio
import aiohttp
import base64
from typing import Dict, Any, List, Optional
import logging
from google.cloud import vision
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import time
from ..config import settings

logger = logging.getLogger(__name__)

class VisionService:
    """Service for analyzing images using multiple vision APIs"""
    
    def __init__(self):
        self.google_client = self._init_google_client()
        self.azure_client = self._init_azure_client()
    
    def _init_google_client(self):
        """Initialize Google Vision client"""
        try:
            if settings.GOOGLE_VISION_API_KEY:
                # Use API key authentication
                import os
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.GOOGLE_VISION_API_KEY
            return vision.ImageAnnotatorClient()
        except Exception as e:
            logger.warning(f"Failed to initialize Google Vision client: {e}")
            return None
    
    def _init_azure_client(self):
        """Initialize Azure Computer Vision client"""
        try:
            if settings.MICROSOFT_VISION_API_KEY and settings.MICROSOFT_VISION_ENDPOINT:
                credentials = CognitiveServicesCredentials(settings.MICROSOFT_VISION_API_KEY)
                return ComputerVisionClient(settings.MICROSOFT_VISION_ENDPOINT, credentials)
        except Exception as e:
            logger.warning(f"Failed to initialize Azure Vision client: {e}")
            return None
    
    async def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze image using both Google Vision and Azure Computer Vision
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Combined analysis results from both services
        """
        tasks = []
        
        if self.google_client:
            tasks.append(self._analyze_with_google(image_data))
        
        if self.azure_client:
            tasks.append(self._analyze_with_azure(image_data))
        
        if not tasks:
            raise ValueError("No vision services available")
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results from both services
        combined_result = self._combine_vision_results(results)
        
        return combined_result
    
    async def _analyze_with_google(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze image with Google Vision API"""
        try:
            image = vision.Image(content=image_data)
            
            # Run multiple detection types in parallel
            tasks = [
                self._run_google_detection(image, 'label_detection'),
                self._run_google_detection(image, 'object_localization'),
                self._run_google_detection(image, 'text_detection'),
                self._run_google_detection(image, 'logo_detection'),
                self._run_google_detection(image, 'product_search')
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                "service": "google_vision",
                "labels": results[0] if not isinstance(results[0], Exception) else [],
                "objects": results[1] if not isinstance(results[1], Exception) else [],
                "text": results[2] if not isinstance(results[2], Exception) else [],
                "logos": results[3] if not isinstance(results[3], Exception) else [],
                "products": results[4] if not isinstance(results[4], Exception) else []
            }
            
        except Exception as e:
            logger.error(f"Google Vision analysis failed: {str(e)}")
            return {"service": "google_vision", "error": str(e)}
    
    async def _run_google_detection(self, image: vision.Image, detection_type: str) -> List[Dict[str, Any]]:
        """Run specific Google Vision detection"""
        try:
            if detection_type == 'label_detection':
                response = self.google_client.label_detection(image=image)
                return [{"description": label.description, "score": label.score} 
                       for label in response.label_annotations]
            
            elif detection_type == 'object_localization':
                response = self.google_client.object_localization(image=image)
                return [{"name": obj.name, "score": obj.score} 
                       for obj in response.localized_object_annotations]
            
            elif detection_type == 'text_detection':
                response = self.google_client.text_detection(image=image)
                texts = response.text_annotations
                return [text.description for text in texts] if texts else []
            
            elif detection_type == 'logo_detection':
                response = self.google_client.logo_detection(image=image)
                return [{"description": logo.description, "score": logo.score} 
                       for logo in response.logo_annotations]
            
            elif detection_type == 'product_search':
                response = self.google_client.product_search(image=image)
                return [{"product_id": result.product.name, "score": result.score} 
                       for result in response.product_search_results.results]
            
        except Exception as e:
            logger.warning(f"Google {detection_type} failed: {str(e)}")
            return []
    
    async def _analyze_with_azure(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze image with Azure Computer Vision"""
        try:
            # Azure requires image to be uploaded or accessible via URL
            # For this implementation, we'll use the analyze_image_in_stream method
            
            features = [
                "Categories", "Description", "Tags", "Objects", 
                "Brands", "Faces", "Color", "ImageType"
            ]
            
            # Convert to stream-like object
            from io import BytesIO
            image_stream = BytesIO(image_data)
            
            analysis = self.azure_client.analyze_image_in_stream(
                image_stream, visual_features=features
            )
            
            return {
                "service": "azure_vision",
                "categories": [{"name": cat.name, "score": cat.score} 
                             for cat in analysis.categories] if analysis.categories else [],
                "description": {
                    "captions": [{"text": cap.text, "confidence": cap.confidence} 
                               for cap in analysis.description.captions] if analysis.description.captions else [],
                    "tags": analysis.description.tags or []
                },
                "tags": [{"name": tag.name, "confidence": tag.confidence} 
                        for tag in analysis.tags] if analysis.tags else [],
                "objects": [{"object": obj.object_property, "confidence": obj.confidence} 
                           for obj in analysis.objects] if analysis.objects else [],
                "brands": [{"name": brand.name, "confidence": brand.confidence} 
                          for brand in analysis.brands] if analysis.brands else [],
                "color": {
                    "dominant_colors": analysis.color.dominant_colors,
                    "accent_color": analysis.color.accent_color,
                    "is_bw_img": analysis.color.is_bw_img
                } if analysis.color else {}
            }
            
        except Exception as e:
            logger.error(f"Azure Vision analysis failed: {str(e)}")
            return {"service": "azure_vision", "error": str(e)}
    
    def _combine_vision_results(self, results: List[Any]) -> Dict[str, Any]:
        """Combine results from multiple vision services"""
        combined = {
            "services_used": [],
            "labels": [],
            "objects": [],
            "text": [],
            "brands": [],
            "description": "",
            "categories": [],
            "confidence_score": 0.0,
            "detected_features": []
        }
        
        all_labels = []
        all_descriptions = []
        
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Vision service error: {result}")
                continue
                
            if "error" in result:
                logger.warning(f"Vision service error: {result['error']}")
                continue
            
            service_name = result.get("service", "unknown")
            combined["services_used"].append(service_name)
            
            if service_name == "google_vision":
                # Process Google Vision results
                combined["labels"].extend(result.get("labels", []))
                combined["objects"].extend(result.get("objects", []))
                combined["text"].extend(result.get("text", []))
                all_labels.extend([label["description"] for label in result.get("labels", [])])
                
            elif service_name == "azure_vision":
                # Process Azure Vision results
                combined["categories"].extend(result.get("categories", []))
                combined["brands"].extend(result.get("brands", []))
                
                description_data = result.get("description", {})
                captions = description_data.get("captions", [])
                if captions:
                    all_descriptions.extend([cap["text"] for cap in captions])
                
                tags = result.get("tags", [])
                all_labels.extend([tag["name"] for tag in tags])
        
        # Generate combined description
        if all_descriptions:
            combined["description"] = max(all_descriptions, key=len)
        elif all_labels:
            combined["description"] = f"Image contains: {', '.join(all_labels[:5])}"
        
        # Calculate overall confidence
        all_scores = []
        for result in results:
            if isinstance(result, dict) and "error" not in result:
                # Extract confidence scores from various sources
                for item in result.get("labels", []):
                    if "score" in item:
                        all_scores.append(item["score"])
                for item in result.get("tags", []):
                    if "confidence" in item:
                        all_scores.append(item["confidence"])
        
        if all_scores:
            combined["confidence_score"] = sum(all_scores) / len(all_scores)
        
        # Deduplicate and sort labels by confidence
        unique_labels = {}
        for result in results:
            if isinstance(result, dict) and "error" not in result:
                for item in result.get("labels", []):
                    label = item.get("description") or item.get("name", "")
                    score = item.get("score") or item.get("confidence", 0)
                    if label and (label not in unique_labels or score > unique_labels[label]):
                        unique_labels[label] = score
        
        combined["detected_features"] = sorted(
            [{"name": k, "confidence": v} for k, v in unique_labels.items()],
            key=lambda x: x["confidence"],
            reverse=True
        )[:10]  # Top 10 features
        
        return combined
