
import aiohttp
import asyncio
import json
from typing import Dict, List, Any, Optional
import base64

from ..config import settings


class GeminiService:
    """Service for Google Gemini Pro 2.5 AI analysis"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-2.0-flash-exp"  # Latest model
        
    async def analyze_product_image(self, image_base64: str, additional_context: str = "") -> Dict[str, Any]:
        """Analyze product image with Gemini Pro Vision"""
        
        prompt = f"""
        Analyze this product image and provide detailed information in JSON format:
        
        {{
            "product_identification": {{
                "name": "exact product name if identifiable",
                "brand": "brand name if visible",
                "model": "model number or specific variant",
                "category": "specific product category",
                "subcategory": "more specific subcategory"
            }},
            "visual_analysis": {{
                "condition_assessment": {{
                    "overall_condition": "condition rating 1-10",
                    "visible_wear": ["list of any visible wear/damage"],
                    "condition_notes": "detailed condition description"
                }},
                "physical_attributes": {{
                    "primary_color": "main color",
                    "secondary_colors": ["other colors present"],
                    "materials": ["materials visible/identifiable"],
                    "size_indicators": "any size information visible",
                    "distinguishing_features": ["unique features or details"]
                }}
            }},
            "market_context": {{
                "estimated_age": "approximate age/era of the product",
                "rarity_level": "common/uncommon/rare/very rare",
                "collectibility": "collectible value assessment",
                "market_demand": "high/medium/low estimated demand"
            }},
            "listing_optimization": {{
                "key_search_terms": ["important keywords for searchability"],
                "selling_points": ["main attractive features for buyers"],
                "condition_highlights": ["positive condition aspects"],
                "potential_concerns": ["issues buyers might have"]
            }},
            "confidence_scores": {{
                "product_identification": 0.0,
                "condition_assessment": 0.0,
                "market_analysis": 0.0,
                "overall_analysis": 0.0
            }}
        }}
        
        Additional context: {additional_context}
        
        Provide only the JSON response, no other text.
        """
        
        url = f"{self.base_url}/models/{self.model}:generateContent"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_base64
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "topK": 32,
                "topP": 1,
                "maxOutputTokens": 2048,
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{url}?key={self.api_key}", 
                                  json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    
                    try:
                        # Parse JSON from response
                        json_start = content.find('{')
                        json_end = content.rfind('}') + 1
                        if json_start != -1 and json_end != -1:
                            json_str = content[json_start:json_end]
                            return json.loads(json_str)
                        else:
                            raise ValueError("No JSON found in response")
                    except (json.JSONDecodeError, ValueError) as e:
                        return {
                            "error": f"Failed to parse Gemini response: {str(e)}",
                            "raw_response": content
                        }
                else:
                    error_text = await response.text()
                    raise Exception(f"Gemini API error: {response.status} - {error_text}")
    
    async def generate_product_description(self, product_data: Dict[str, Any], 
                                         target_platform: str = "general") -> Dict[str, Any]:
        """Generate optimized product description using Gemini"""
        
        prompt = f"""
        Create an optimized product listing for {target_platform} based on this product data:
        
        Product Information:
        {json.dumps(product_data, indent=2)}
        
        Generate:
        1. SEO-optimized title (under 80 characters)
        2. Detailed description (150-500 words)
        3. Key features list
        4. Relevant tags/keywords
        5. Condition statement
        
        Format as JSON:
        {{
            "title": "optimized title",
            "description": "detailed description",
            "key_features": ["feature1", "feature2"],
            "tags": ["tag1", "tag2"],
            "condition_statement": "condition description",
            "platform_specific_notes": "any platform-specific recommendations"
        }}
        
        Make it compelling for buyers while being accurate and honest.
        """
        
        url = f"{self.base_url}/models/{self.model}:generateContent"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024,
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{url}?key={self.api_key}", 
                                  json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    
                    try:
                        json_start = content.find('{')
                        json_end = content.rfind('}') + 1
                        if json_start != -1 and json_end != -1:
                            json_str = content[json_start:json_end]
                            return json.loads(json_str)
                        else:
                            raise ValueError("No JSON found in response")
                    except (json.JSONDecodeError, ValueError) as e:
                        return {
                            "error": f"Failed to parse Gemini response: {str(e)}",
                            "raw_response": content
                        }
                else:
                    error_text = await response.text()
                    raise Exception(f"Gemini API error: {response.status} - {error_text}")
    
    async def research_product_market(self, product_name: str, category: str) -> Dict[str, Any]:
        """Use Gemini to research market information for a product"""
        
        prompt = f"""
        Research current market information for this product:
        
        Product: {product_name}
        Category: {category}
        
        Provide market analysis in JSON format:
        {{
            "market_overview": {{
                "current_market_status": "market condition description",
                "price_trends": "recent price trend analysis",
                "seasonality": "seasonal factors affecting demand",
                "competition_level": "high/medium/low"
            }},
            "platform_recommendations": {{
                "best_platforms": ["platform1", "platform2"],
                "platform_analysis": {{
                    "ebay": "suitability and reasoning",
                    "facebook_marketplace": "suitability and reasoning",
                    "mercari": "suitability and reasoning",
                    "poshmark": "suitability and reasoning"
                }}
            }},
            "pricing_insights": {{
                "typical_price_range": "price range information",
                "factors_affecting_price": ["factor1", "factor2"],
                "condition_impact": "how condition affects pricing"
            }},
            "selling_tips": {{
                "optimal_timing": "best time to sell",
                "key_selling_points": ["point1", "point2"],
                "common_buyer_concerns": ["concern1", "concern2"]
            }}
        }}
        
        Base this on current market knowledge and trends.
        """
        
        url = f"{self.base_url}/models/{self.model}:generateContent"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "topK": 32,
                "topP": 0.8,
                "maxOutputTokens": 1500,
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{url}?key={self.api_key}", 
                                  json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    
                    try:
                        json_start = content.find('{')
                        json_end = content.rfind('}') + 1
                        if json_start != -1 and json_end != -1:
                            json_str = content[json_start:json_end]
                            return json.loads(json_str)
                        else:
                            raise ValueError("No JSON found in response")
                    except (json.JSONDecodeError, ValueError) as e:
                        return {
                            "error": f"Failed to parse Gemini response: {str(e)}",
                            "raw_response": content
                        }
                else:
                    error_text = await response.text()
                    raise Exception(f"Gemini API error: {response.status} - {error_text}")
