import base64
import io
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..config import settings
from ..models.analysis import VisionAnalysisResult

class VisionService:
    """Service for analyzing images using various vision APIs"""
    
    def __init__(self):
        self.google_api_key = settings.GOOGLE_VISION_API_KEY
        self.azure_api_key = settings.AZURE_VISION_API_KEY
        self.executor = ThreadPoolExecutor(max_workers=3)
    
    async def analyze_image(self, image_data: str) -> VisionAnalysisResult:
        """Analyze image using available vision services"""
        import time
        start_time = time.time()
        
        # Prepare image data
        image_bytes = self._prepare_image_data(image_data)
        
        # Run multiple vision services in parallel
        tasks = []
        
        if self.google_api_key:
            tasks.append(self._analyze_with_google_vision(image_bytes))
        
        if self.azure_api_key:
            tasks.append(self._analyze_with_azure_vision(image_bytes))
        
        # Fallback to basic image analysis if no API keys
        if not tasks:
            tasks.append(self._basic_image_analysis(image_bytes))
        
        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        combined_result = self._combine_vision_results(results)
        combined_result.processing_time = time.time() - start_time
        
        return combined_result
    
    def _prepare_image_data(self, image_data: str) -> bytes:
        """Convert base64 image data to bytes"""
        try:
            # Handle data URL format
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            
            # Validate and potentially resize image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Resize if too large (max 4MB for most APIs)
            max_size = (2048, 2048)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convert back to bytes
                output = io.BytesIO()
                image.save(output, format='JPEG', quality=85)
                image_bytes = output.getvalue()
            
            return image_bytes
            
        except Exception as e:
            raise ValueError(f"Invalid image data: {str(e)}")
    
    async def _analyze_with_google_vision(self, image_bytes: bytes) -> Dict[str, Any]:
        """Analyze image using Google Cloud Vision API"""
        try:
            url = f"https://vision.googleapis.com/v1/images:annotate?key={self.google_api_key}"
            
            # Encode image for API
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            payload = {
                "requests": [{
                    "image": {"content": image_b64},
                    "features": [
                        {"type": "LABEL_DETECTION", "maxResults": 20},
                        {"type": "TEXT_DETECTION", "maxResults": 10},
                        {"type": "OBJECT_LOCALIZATION", "maxResults": 15},
                        {"type": "IMAGE_PROPERTIES", "maxResults": 10}
                    ]
                }]
            }
            
            # Make async request
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                lambda: requests.post(url, json=payload, timeout=30)
            )
            
            if response.status_code != 200:
                raise Exception(f"Google Vision API error: {response.status_code}")
            
            data = response.json()
            return self._parse_google_vision_response(data)
            
        except Exception as e:
            print(f"Google Vision API error: {e}")
            return {"source": "google", "error": str(e)}
    
    async def _analyze_with_azure_vision(self, image_bytes: bytes) -> Dict[str, Any]:
        """Analyze image using Azure Computer Vision API"""
        try:
            # Azure Computer Vision endpoint (you'd need to set this up)
            endpoint = "https://your-resource.cognitiveservices.azure.com/"
            url = f"{endpoint}vision/v3.2/analyze"
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.azure_api_key,
                'Content-Type': 'application/octet-stream'
            }
            
            params = {
                'visualFeatures': 'Categories,Description,Objects,Tags,Color',
                'details': 'Landmarks'
            }
            
            # Make async request
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                lambda: requests.post(url, headers=headers, params=params, data=image_bytes, timeout=30)
            )
            
            if response.status_code != 200:
                raise Exception(f"Azure Vision API error: {response.status_code}")
            
            data = response.json()
            return self._parse_azure_vision_response(data)
            
        except Exception as e:
            print(f"Azure Vision API error: {e}")
            return {"source": "azure", "error": str(e)}
    
    async def _basic_image_analysis(self, image_bytes: bytes) -> Dict[str, Any]:
        """Basic image analysis without external APIs"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Basic image properties
            width, height = image.size
            mode = image.mode
            
            # Dominant colors (simplified)
            colors = self._extract_dominant_colors(image)
            
            # Basic object detection based on image properties
            labels = self._basic_object_detection(image)
            
            return {
                "source": "basic",
                "labels": labels,
                "colors": colors,
                "properties": {
                    "width": width,
                    "height": height,
                    "mode": mode
                }
            }
            
        except Exception as e:
            print(f"Basic image analysis error: {e}")
            return {"source": "basic", "error": str(e)}
    
    def _parse_google_vision_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Google Vision API response"""
        result = {"source": "google", "labels": [], "objects": [], "text_detections": [], "colors": []}
        
        if "responses" in data and len(data["responses"]) > 0:
            response = data["responses"][0]
            
            # Labels
            if "labelAnnotations" in response:
                result["labels"] = [
                    label["description"] for label in response["labelAnnotations"]
                    if label.get("score", 0) > 0.5
                ]
            
            # Objects
            if "localizedObjectAnnotations" in response:
                result["objects"] = [
                    {
                        "name": obj["name"],
                        "confidence": obj.get("score", 0)
                    }
                    for obj in response["localizedObjectAnnotations"]
                ]
            
            # Text
            if "textAnnotations" in response:
                result["text_detections"] = [
                    text["description"] for text in response["textAnnotations"]
                ]
            
            # Colors
            if "imagePropertiesAnnotation" in response:
                colors_data = response["imagePropertiesAnnotation"].get("dominantColors", {})
                if "colors" in colors_data:
                    result["colors"] = [
                        f"rgb({int(color['color']['red'])},{int(color['color']['green'])},{int(color['color']['blue'])})"
                        for color in colors_data["colors"][:5]
                    ]
        
        return result
    
    def _parse_azure_vision_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Azure Vision API response"""
        result = {"source": "azure", "labels": [], "objects": [], "text_detections": [], "colors": []}
        
        # Tags/Labels
        if "tags" in data:
            result["labels"] = [
                tag["name"] for tag in data["tags"]
                if tag.get("confidence", 0) > 0.5
            ]
        
        # Objects
        if "objects" in data:
            result["objects"] = [
                {
                    "name": obj["object"],
                    "confidence": obj.get("confidence", 0)
                }
                for obj in data["objects"]
            ]
        
        # Colors
        if "color" in data:
            color_data = data["color"]
            result["colors"] = [
                color_data.get("dominantColorForeground", ""),
                color_data.get("dominantColorBackground", "")
            ]
        
        return result
    
    def _extract_dominant_colors(self, image: Image.Image, num_colors: int = 5) -> List[str]:
        """Extract dominant colors from image"""
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize for faster processing
            image = image.resize((150, 150))
            
            # Get colors using quantization
            quantized = image.quantize(colors=num_colors)
            palette = quantized.getpalette()
            
            colors = []
            for i in range(num_colors):
                r = palette[i * 3]
                g = palette[i * 3 + 1]
                b = palette[i * 3 + 2]
                colors.append(f"rgb({r},{g},{b})")
            
            return colors
            
        except Exception:
            return ["rgb(128,128,128)"]  # Default gray
    
    def _basic_object_detection(self, image: Image.Image) -> List[str]:
        """Basic object detection based on image characteristics"""
        labels = []
        
        try:
            width, height = image.size
            aspect_ratio = width / height
            
            # Basic heuristics
            if aspect_ratio > 1.5:
                labels.append("rectangular object")
            elif 0.8 <= aspect_ratio <= 1.2:
                labels.append("square object")
            
            # Analyze brightness
            grayscale = image.convert('L')
            histogram = grayscale.histogram()
            
            # Calculate average brightness
            total_pixels = sum(histogram)
            weighted_sum = sum(i * histogram[i] for i in range(256))
            avg_brightness = weighted_sum / total_pixels
            
            if avg_brightness < 85:
                labels.append("dark object")
            elif avg_brightness > 170:
                labels.append("bright object")
            
            # Add generic labels
            labels.extend(["product", "item", "object"])
            
        except Exception:
            labels = ["product", "item"]
        
        return labels
    
    def _combine_vision_results(self, results: List[Any]) -> VisionAnalysisResult:
        """Combine results from multiple vision services"""
        combined = VisionAnalysisResult()
        
        all_labels = set()
        all_objects = []
        all_text = set()
        all_colors = set()
        confidence_scores = {}
        
        for result in results:
            if isinstance(result, Exception):
                continue
            
            if "error" in result:
                continue
            
            # Combine labels
            if "labels" in result:
                all_labels.update(result["labels"])
            
            # Combine objects
            if "objects" in result:
                all_objects.extend(result["objects"])
            
            # Combine text
            if "text_detections" in result:
                all_text.update(result["text_detections"])
            
            # Combine colors
            if "colors" in result:
                all_colors.update(result["colors"])
            
            # Store confidence scores by source
            confidence_scores[result.get("source", "unknown")] = 0.8
        
        # Convert sets to lists and limit results
        combined.labels = list(all_labels)[:20]
        combined.objects = all_objects[:15]
        combined.text_detections = list(all_text)[:10]
        combined.colors = list(all_colors)[:10]
        combined.confidence_scores = confidence_scores
        
        return combined
