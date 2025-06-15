import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class GoogleShoppingService:
    """Service for fetching real-time product pricing data from Google Shopping via SerpApi"""

    def __init__(self):
        self.api_key = settings.SERPAPI_KEY
        self.base_url = "https://serpapi.com/search"

    async def search_products(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for products on Google Shopping and return pricing data

        Args:
            query: Product search query
            limit: Maximum number of results to return

        Returns:
            List of product data with pricing information
        """
        if not self.api_key:
            raise ValueError("SerpApi key not configured")

        params = {
            "engine": "google_shopping",
            "q": query,
            "api_key": self.api_key,
            "num": limit,
            "gl": "us",  # Country
            "hl": "en"   # Language
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_shopping_results(data)
                    else:
                        logger.error(f"SerpApi request failed with status {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching Google Shopping data: {str(e)}")
            return []

    def _parse_shopping_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse SerpApi response into standardized format"""
        products = []
        shopping_results = data.get("shopping_results", [])

        for item in shopping_results:
            try:
                product = {
                    "title": item.get("title", ""),
                    "price": self._extract_price(item.get("price")),
                    "currency": "USD",  # Default, could be extracted from price string
                    "source": item.get("source", ""),
                    "link": item.get("link", ""),
                    "rating": item.get("rating"),
                    "reviews": item.get("reviews"),
                    "delivery": item.get("delivery", ""),
                    "thumbnail": item.get("thumbnail"),
                    "product_id": item.get("product_id"),
                    "position": item.get("position")
                }
                products.append(product)
            except Exception as e:
                logger.warning(f"Error parsing product item: {str(e)}")
                continue

        return products

    def _extract_price(self, price_str: Optional[str]) -> Optional[float]:
        """Extract numeric price from price string"""
        if not price_str:
            return None

        try:
            # Remove currency symbols and commas, extract numbers
            import re
            price_match = re.search(r'[\d,]+\.?\d*', price_str.replace(',', ''))
            if price_match:
                return float(price_match.group())
        except Exception:
            pass
        return None

    async def get_price_statistics(self, query: str) -> Dict[str, Any]:
        """Get price statistics for a product query"""
        products = await self.search_products(query, limit=20)

        if not products:
            return {
                "min_price": None,
                "max_price": None,
                "avg_price": None,
                "median_price": None,
                "total_results": 0
            }

        prices = [p["price"] for p in products if p["price"] is not None]

        if not prices:
            return {
                "min_price": None,
                "max_price": None,
                "avg_price": None,
                "median_price": None,
                "total_results": len(products)
            }

        prices.sort()
        return {
            "min_price": min(prices),
            "max_price": max(prices),
            "avg_price": sum(prices) / len(prices),
            "median_price": prices[len(prices) // 2],
            "total_results": len(products),
            "price_range": max(prices) - min(prices)
        }