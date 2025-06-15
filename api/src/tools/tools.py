
from langchain.tools import BaseTool
from typing import Dict, Any, List, Optional
import asyncio
import json
import logging
from pydantic import Field, BaseModel

from ..services.google_shopping_service import GoogleShoppingService
from ..services.vision_service import VisionService
from ..services.gemini_service import GeminiService
from ..services.fee_service import FeeService, MarketplacePlatform

logger = logging.getLogger(__name__)

class GoogleShoppingSearchInput(BaseModel):
    query: str = Field(description="Product search query")
    limit: int = Field(default=10, description="Maximum number of results")

class GoogleShoppingSearchTool(BaseTool):
    name = "google_shopping_search"
    description = "Search for products on Google Shopping to get pricing and market data"
    args_schema = GoogleShoppingSearchInput
    
    def __init__(self):
        super().__init__()
        self.service = GoogleShoppingService()
    
    def _run(self, query: str, limit: int = 10) -> str:
        """Synchronous run method (required by LangChain)"""
        try:
            # Run the async method in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.service.search_products(query, limit))
            loop.close()
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in Google Shopping search: {str(e)}")
            return json.dumps({"error": str(e)})
    
    async def _arun(self, query: str, limit: int = 10) -> str:
        """Asynchronous run method"""
        try:
            result = await self.service.search_products(query, limit)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in Google Shopping search: {str(e)}")
            return json.dumps({"error": str(e)})

class PriceStatisticsInput(BaseModel):
    query: str = Field(description="Product search query for price analysis")

class PriceStatisticsTool(BaseTool):
    name = "price_statistics"
    description = "Get price statistics and market analysis for a product"
    args_schema = PriceStatisticsInput
    
    def __init__(self):
        super().__init__()
        self.service = GoogleShoppingService()
    
    def _run(self, query: str) -> str:
        """Synchronous run method"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.service.get_price_statistics(query))
            loop.close()
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in price statistics: {str(e)}")
            return json.dumps({"error": str(e)})
    
    async def _arun(self, query: str) -> str:
        """Asynchronous run method"""
        try:
            result = await self.service.get_price_statistics(query)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in price statistics: {str(e)}")
            return json.dumps({"error": str(e)})

class VisionAnalysisInput(BaseModel):
    image_data: str = Field(description="Base64 encoded image data")

class MultiVisionAnalysisTool(BaseTool):
    name = "multi_vision_analysis"
    description = "Analyze images using multiple vision APIs (Google Vision + Azure Computer Vision)"
    args_schema = VisionAnalysisInput
    
    def __init__(self):
        super().__init__()
        self.service = VisionService()
    
    def _run(self, image_data: str) -> str:
        """Synchronous run method"""
        try:
            import base64
            image_bytes = base64.b64decode(image_data)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.service.analyze_image(image_bytes))
            loop.close()
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in vision analysis: {str(e)}")
            return json.dumps({"error": str(e)})
    
    async def _arun(self, image_data: str) -> str:
        """Asynchronous run method"""
        try:
            import base64
            image_bytes = base64.b64decode(image_data)
            result = await self.service.analyze_image(image_bytes)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in vision analysis: {str(e)}")
            return json.dumps({"error": str(e)})

class ContentGenerationInput(BaseModel):
    prompt: str = Field(description="Prompt for content generation")
    max_tokens: int = Field(default=1000, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, description="Creativity level (0.0 to 1.0)")

class ContentGenerationTool(BaseTool):
    name = "content_generation"
    description = "Generate content using Google Gemini Pro for product descriptions, titles, etc."
    args_schema = ContentGenerationInput
    
    def __init__(self):
        super().__init__()
        self.service = GeminiService()
    
    def _run(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Synchronous run method"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.service.generate_content(prompt, max_tokens, temperature)
            )
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error in content generation: {str(e)}")
            return f"Error: {str(e)}"
    
    async def _arun(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Asynchronous run method"""
        try:
            result = await self.service.generate_content(prompt, max_tokens, temperature)
            return result
        except Exception as e:
            logger.error(f"Error in content generation: {str(e)}")
            return f"Error: {str(e)}"

class ProductDescriptionInput(BaseModel):
    product_name: str = Field(description="Product name")
    features: List[str] = Field(description="List of product features")
    category: str = Field(default="", description="Product category")

class ProductDescriptionTool(BaseTool):
    name = "product_description_generator"
    description = "Generate compelling product descriptions for e-commerce platforms"
    args_schema = ProductDescriptionInput
    
    def __init__(self):
        super().__init__()
        self.service = GeminiService()
    
    def _run(self, product_name: str, features: List[str], category: str = "") -> str:
        """Synchronous run method"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.service.generate_product_description(product_name, features, category)
            )
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error generating product description: {str(e)}")
            return f"Error: {str(e)}"
    
    async def _arun(self, product_name: str, features: List[str], category: str = "") -> str:
        """Asynchronous run method"""
        try:
            result = await self.service.generate_product_description(product_name, features, category)
            return result
        except Exception as e:
            logger.error(f"Error generating product description: {str(e)}")
            return f"Error: {str(e)}"

class TagsKeywordsInput(BaseModel):
    product_name: str = Field(description="Product name")
    description: str = Field(description="Product description")
    category: str = Field(default="", description="Product category")

class TagsKeywordsTool(BaseTool):
    name = "tags_keywords_generator"
    description = "Generate relevant tags and keywords for e-commerce platforms"
    args_schema = TagsKeywordsInput
    
    def __init__(self):
        super().__init__()
        self.service = GeminiService()
    
    def _run(self, product_name: str, description: str, category: str = "") -> str:
        """Synchronous run method"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.service.generate_tags_and_keywords(product_name, description, category)
            )
            loop.close()
            return json.dumps(result)
        except Exception as e:
            logger.error(f"Error generating tags: {str(e)}")
            return json.dumps([])
    
    async def _arun(self, product_name: str, description: str, category: str = "") -> str:
        """Asynchronous run method"""
        try:
            result = await self.service.generate_tags_and_keywords(product_name, description, category)
            return json.dumps(result)
        except Exception as e:
            logger.error(f"Error generating tags: {str(e)}")
            return json.dumps([])

class FeeCalculationInput(BaseModel):
    platform: str = Field(description="Marketplace platform (ebay, amazon, etsy, etc.)")
    sale_price: float = Field(description="Sale price of the item")
    shipping_cost: float = Field(default=0.0, description="Shipping cost")
    item_cost: float = Field(default=0.0, description="Cost of the item to seller")

class FeeCalculationTool(BaseTool):
    name = "fee_calculation"
    description = "Calculate marketplace fees and profit margins for different platforms"
    args_schema = FeeCalculationInput
    
    def __init__(self):
        super().__init__()
        self.service = FeeService()
    
    def _run(self, platform: str, sale_price: float, shipping_cost: float = 0.0, item_cost: float = 0.0) -> str:
        """Synchronous run method"""
        try:
            # Convert string to enum
            platform_enum = MarketplacePlatform(platform.lower())
            result = self.service.calculate_fees(platform_enum, sale_price, shipping_cost, item_cost)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error calculating fees: {str(e)}")
            return json.dumps({"error": str(e)})
    
    async def _arun(self, platform: str, sale_price: float, shipping_cost: float = 0.0, item_cost: float = 0.0) -> str:
        """Asynchronous run method"""
        try:
            platform_enum = MarketplacePlatform(platform.lower())
            result = self.service.calculate_fees(platform_enum, sale_price, shipping_cost, item_cost)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error calculating fees: {str(e)}")
            return json.dumps({"error": str(e)})

class PlatformComparisonInput(BaseModel):
    sale_price: float = Field(description="Sale price of the item")
    item_cost: float = Field(default=0.0, description="Cost of the item to seller")
    shipping_cost: float = Field(default=0.0, description="Shipping cost")

class PlatformComparisonTool(BaseTool):
    name = "platform_comparison"
    description = "Compare profitability across multiple marketplace platforms"
    args_schema = PlatformComparisonInput
    
    def __init__(self):
        super().__init__()
        self.service = FeeService()
    
    def _run(self, sale_price: float, item_cost: float = 0.0, shipping_cost: float = 0.0) -> str:
        """Synchronous run method"""
        try:
            result = self.service.compare_platforms(sale_price, item_cost, shipping_cost)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error comparing platforms: {str(e)}")
            return json.dumps({"error": str(e)})
    
    async def _arun(self, sale_price: float, item_cost: float = 0.0, shipping_cost: float = 0.0) -> str:
        """Asynchronous run method"""
        try:
            result = self.service.compare_platforms(sale_price, item_cost, shipping_cost)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error comparing platforms: {str(e)}")
            return json.dumps({"error": str(e)})

class RecommendationInput(BaseModel):
    sale_price: float = Field(description="Sale price of the item")
    item_cost: float = Field(default=0.0, description="Cost of the item to seller")
    category: str = Field(default="", description="Product category")
    shipping_cost: float = Field(default=0.0, description="Shipping cost")

class PlatformRecommendationTool(BaseTool):
    name = "platform_recommendation"
    description = "Get the recommended marketplace platform based on highest profit"
    args_schema = RecommendationInput
    
    def __init__(self):
        super().__init__()
        self.service = FeeService()
    
    def _run(self, sale_price: float, item_cost: float = 0.0, category: str = "", shipping_cost: float = 0.0) -> str:
        """Synchronous run method"""
        try:
            result = self.service.get_recommended_platform(sale_price, item_cost, category, shipping_cost)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error getting platform recommendation: {str(e)}")
            return json.dumps({"error": str(e)})
    
    async def _arun(self, sale_price: float, item_cost: float = 0.0, category: str = "", shipping_cost: float = 0.0) -> str:
        """Asynchronous run method"""
        try:
            result = self.service.get_recommended_platform(sale_price, item_cost, category, shipping_cost)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error getting platform recommendation: {str(e)}")
            return json.dumps({"error": str(e)})

# Create tool instances for easy import
google_shopping_search_tool = GoogleShoppingSearchTool()
price_statistics_tool = PriceStatisticsTool()
multi_vision_analysis_tool = MultiVisionAnalysisTool()
content_generation_tool = ContentGenerationTool()
product_description_tool = ProductDescriptionTool()
tags_keywords_tool = TagsKeywordsTool()
fee_calculation_tool = FeeCalculationTool()
platform_comparison_tool = PlatformComparisonTool()
platform_recommendation_tool = PlatformRecommendationTool()

# List of all available tools
ALL_TOOLS = [
    google_shopping_search_tool,
    price_statistics_tool,
    multi_vision_analysis_tool,
    content_generation_tool,
    product_description_tool,
    tags_keywords_tool,
    fee_calculation_tool,
    platform_comparison_tool,
    platform_recommendation_tool
]
