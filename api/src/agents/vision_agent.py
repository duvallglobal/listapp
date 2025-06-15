
import base64
import io
from typing import List, Dict, Any, Optional
from PIL import Image
import openai
from google.cloud import vision
from crewai_tools import BaseTool

from src.models.product import ProductIdentification, ProductCategory, ProductCondition
from src.services.vision_service import VisionService


class VisionAnalysisTool(BaseTool):
    name: str = "vision_analysis"
    description: str = "Analyze product images to identify products, assess condition, and extract details"
    
    def __init__(self, vision_service: VisionService):
        super().__init__()
        self.vision_service = vision_service
    
    def _run(self, image_data: str) -> Dict[str, Any]:
        """
        Analyze product image and return identification details
        """
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            
            # Google Vision API analysis
            vision_results = self.vision_service.analyze_image(image_bytes)
            
            # OpenAI GPT-4 Vision analysis for detailed product identification
            gpt_analysis = self.vision_service.analyze_with_gpt4_vision(image_data)
            
            # Combine results
            analysis_result = {
                "google_vision": vision_results,
                "gpt4_analysis": gpt_analysis,
                "product_identification": self._extract_product_details(vision_results, gpt_analysis),
                "image_quality_assessment": self._assess_image_quality(vision_results)
            }
            
            return analysis_result
            
        except Exception as e:
            return {"error": f"Vision analysis failed: {str(e)}"}
    
    def _extract_product_details(self, vision_results: Dict, gpt_analysis: Dict) -> Dict[str, Any]:
        """
        Extract structured product details from vision analysis results
        """
        # Extract product name and category from text detection
        detected_text = vision_results.get("text_annotations", [])
        product_text = " ".join([text.get("description", "") for text in detected_text[:5]])
        
        # Use GPT analysis for detailed extraction
        product_details = gpt_analysis.get("product_details", {})
        
        # Map to our product model
        return {
            "name": product_details.get("name", "Unknown Product"),
            "brand": product_details.get("brand"),
            "model": product_details.get("model"),
            "category": self._categorize_product(product_details.get("category", "other")),
            "condition": self._assess_condition(gpt_analysis.get("condition_assessment", {})),
            "description": product_details.get("description", ""),
            "features": product_details.get("features", []),
            "color": product_details.get("color"),
            "materials": product_details.get("materials", []),
            "identification_confidence": gpt_analysis.get("confidence", 0.8)
        }
    
    def _categorize_product(self, category_text: str) -> str:
        """
        Map detected category to our enum
        """
        category_mapping = {
            "electronics": ProductCategory.ELECTRONICS,
            "electronic": ProductCategory.ELECTRONICS,
            "clothing": ProductCategory.CLOTHING,
            "apparel": ProductCategory.CLOTHING,
            "home": ProductCategory.HOME_GARDEN,
            "garden": ProductCategory.HOME_GARDEN,
            "sports": ProductCategory.SPORTS,
            "collectibles": ProductCategory.COLLECTIBLES,
            "books": ProductCategory.BOOKS,
            "toys": ProductCategory.TOYS,
            "automotive": ProductCategory.AUTOMOTIVE,
            "jewelry": ProductCategory.JEWELRY
        }
        
        category_lower = category_text.lower()
        for key, value in category_mapping.items():
            if key in category_lower:
                return value.value
        
        return ProductCategory.OTHER.value
    
    def _assess_condition(self, condition_data: Dict) -> str:
        """
        Assess product condition from vision analysis
        """
        condition_score = condition_data.get("score", 7.0)
        
        if condition_score >= 9.5:
            return ProductCondition.NEW.value
        elif condition_score >= 8.5:
            return ProductCondition.LIKE_NEW.value
        elif condition_score >= 7.0:
            return ProductCondition.VERY_GOOD.value
        elif condition_score >= 5.5:
            return ProductCondition.GOOD.value
        elif condition_score >= 3.0:
            return ProductCondition.ACCEPTABLE.value
        else:
            return ProductCondition.POOR.value
    
    def _assess_image_quality(self, vision_results: Dict) -> Dict[str, Any]:
        """
        Assess the quality of the uploaded image for marketplace listing
        """
        # Check image properties
        image_properties = vision_results.get("image_properties", {})
        
        quality_score = 7.0  # Default
        issues = []
        suggestions = []
        
        # Check for blur detection
        if vision_results.get("blur_detected", False):
            quality_score -= 2.0
            issues.append("Image appears blurry")
            suggestions.append("Take a sharper photo with better focus")
        
        # Check lighting
        dominant_colors = image_properties.get("dominant_colors", [])
        if len(dominant_colors) > 0:
            brightness = sum(color.get("pixel_fraction", 0) for color in dominant_colors[:3])
            if brightness < 0.3:
                quality_score -= 1.0
                issues.append("Image is too dark")
                suggestions.append("Improve lighting when taking the photo")
        
        return {
            "quality_score": max(0.0, min(10.0, quality_score)),
            "issues": issues,
            "suggestions": suggestions,
            "image_properties": image_properties
        }


class VisionAgent:
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.vision_service = VisionService(api_keys.get("google_vision"))
    
    def get_tools(self) -> List[BaseTool]:
        return [VisionAnalysisTool(self.vision_service)]
    
    def analyze_product_image(self, image_data: str) -> Dict[str, Any]:
        """
        Main method to analyze a product image
        """
        tool = VisionAnalysisTool(self.vision_service)
        return tool._run(image_data)
