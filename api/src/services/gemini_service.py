
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
import logging
import json
from ..config import settings

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for generating content using Google Gemini Pro"""
    
    def __init__(self):
        self.api_key = settings.GOOGLE_GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model_name = "gemini-pro"
    
    async def generate_content(
        self, 
        prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generate content using Gemini Pro
        
        Args:
            prompt: The prompt to send to Gemini
            max_tokens: Maximum tokens to generate
            temperature: Creativity level (0.0 to 1.0)
            system_instruction: Optional system instruction
            
        Returns:
            Generated text content
        """
        if not self.api_key:
            raise ValueError("Google Gemini API key not configured")
        
        url = f"{self.base_url}/{self.model_name}:generateContent"
        
        # Prepare the request body
        contents = []
        
        if system_instruction:
            contents.append({
                "role": "user",
                "parts": [{"text": system_instruction}]
            })
        
        contents.append({
            "role": "user", 
            "parts": [{"text": prompt}]
        })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.8,
                "topK": 40
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        params = {
            "key": self.api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, 
                    json=payload, 
                    headers=headers, 
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._extract_generated_text(data)
                    else:
                        error_text = await response.text()
                        logger.error(f"Gemini API error {response.status}: {error_text}")
                        raise Exception(f"Gemini API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            raise
    
    def _extract_generated_text(self, response_data: Dict[str, Any]) -> str:
        """Extract generated text from Gemini response"""
        try:
            candidates = response_data.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    return parts[0].get("text", "")
            return ""
        except Exception as e:
            logger.error(f"Error extracting text from Gemini response: {str(e)}")
            return ""
    
    async def generate_product_description(
        self, 
        product_name: str, 
        features: List[str], 
        category: str = ""
    ) -> str:
        """Generate a compelling product description"""
        features_text = ", ".join(features)
        
        prompt = f"""
        Create a compelling and detailed product description for the following product:
        
        Product Name: {product_name}
        Category: {category}
        Key Features: {features_text}
        
        Write a description that:
        1. Highlights the main benefits and features
        2. Uses persuasive and engaging language
        3. Is suitable for e-commerce platforms
        4. Is between 100-300 words
        5. Includes relevant keywords for SEO
        
        Format the response as a single paragraph description.
        """
        
        return await self.generate_content(prompt, max_tokens=500, temperature=0.8)
    
    async def generate_tags_and_keywords(
        self, 
        product_name: str, 
        description: str, 
        category: str = ""
    ) -> List[str]:
        """Generate relevant tags and keywords for a product"""
        prompt = f"""
        Based on the following product information, generate relevant tags and keywords for e-commerce platforms:
        
        Product Name: {product_name}
        Category: {category}
        Description: {description}
        
        Generate 10-15 relevant tags/keywords that:
        1. Are commonly used in product searches
        2. Include the main product category
        3. Include descriptive attributes
        4. Include potential use cases
        5. Are suitable for platforms like eBay, Amazon, etc.
        
        Return the tags as a comma-separated list.
        """
        
        result = await self.generate_content(prompt, max_tokens=200, temperature=0.6)
        
        # Parse the comma-separated tags
        tags = [tag.strip() for tag in result.split(",") if tag.strip()]
        return tags[:15]  # Limit to 15 tags
    
    async def analyze_market_positioning(
        self, 
        product_name: str, 
        price_data: Dict[str, Any], 
        features: List[str]
    ) -> Dict[str, Any]:
        """Analyze market positioning and generate recommendations"""
        price_info = ""
        if price_data:
            price_info = f"""
            Current Market Prices:
            - Average Price: ${price_data.get('avg_price', 'N/A')}
            - Price Range: ${price_data.get('min_price', 'N/A')} - ${price_data.get('max_price', 'N/A')}
            - Total Results: {price_data.get('total_results', 0)}
            """
        
        features_text = ", ".join(features)
        
        prompt = f"""
        Analyze the market positioning for this product and provide strategic recommendations:
        
        Product: {product_name}
        Key Features: {features_text}
        {price_info}
        
        Provide analysis in JSON format with the following structure:
        {{
            "competitive_advantages": ["advantage1", "advantage2"],
            "target_market": "description of ideal customers",
            "positioning_strategy": "recommended market positioning",
            "pricing_recommendation": "pricing strategy advice",
            "marketing_angles": ["angle1", "angle2", "angle3"]
        }}
        
        Return only valid JSON.
        """
        
        result = await self.generate_content(prompt, max_tokens=800, temperature=0.7)
        
        try:
            # Try to parse as JSON
            return json.loads(result)
        except json.JSONDecodeError:
            # If JSON parsing fails, return a structured fallback
            logger.warning("Failed to parse Gemini JSON response")
            return {
                "competitive_advantages": ["Quality product", "Good value"],
                "target_market": "General consumers",
                "positioning_strategy": "Value-focused positioning",
                "pricing_recommendation": "Competitive pricing",
                "marketing_angles": ["Quality", "Value", "Reliability"]
            }
    
    async def generate_title_variants(self, product_name: str, features: List[str]) -> List[str]:
        """Generate multiple title variants for A/B testing"""
        features_text = ", ".join(features[:5])  # Limit features
        
        prompt = f"""
        Generate 5 different product title variants for e-commerce platforms based on:
        
        Original Product Name: {product_name}
        Key Features: {features_text}
        
        Each title should:
        1. Be under 80 characters
        2. Include key features/benefits
        3. Be optimized for search
        4. Appeal to potential buyers
        5. Follow e-commerce best practices
        
        Return the titles as a numbered list, one per line.
        """
        
        result = await self.generate_content(prompt, max_tokens=300, temperature=0.8)
        
        # Parse the numbered list
        titles = []
        for line in result.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering and clean up
                title = line.split('.', 1)[-1].strip()
                title = title.lstrip('- ').strip()
                if title and len(title) <= 80:
                    titles.append(title)
        
        return titles[:5]  # Return max 5 titles
