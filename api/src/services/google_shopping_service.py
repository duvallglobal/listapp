
import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from ..config import settings


class GoogleShoppingService:
    """Service for Google Shopping API integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_SHOPPING_API_KEY
        self.base_url = "https://www.googleapis.com/shopping/v1"
        self.search_url = f"{self.base_url}/products"
        
    async def search_products(self, query: str, category: Optional[str] = None, 
                            max_results: int = 50) -> Dict[str, Any]:
        """Search for products on Google Shopping"""
        
        params = {
            "key": self.api_key,
            "q": query,
            "maxResults": max_results,
            "country": "US",
            "currency": "USD"
        }
        
        if category:
            params["categoryId"] = category
            
        async with aiohttp.ClientSession() as session:
            async with session.get(self.search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_shopping_results(data)
                else:
                    error_text = await response.text()
                    raise Exception(f"Google Shopping API error: {response.status} - {error_text}")
    
    async def get_product_offers(self, product_id: str) -> List[Dict[str, Any]]:
        """Get offers for a specific product"""
        
        url = f"{self.base_url}/products/{product_id}/offers"
        params = {
            "key": self.api_key,
            "country": "US",
            "currency": "USD"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("offers", [])
                else:
                    return []
    
    async def get_price_insights(self, query: str) -> Dict[str, Any]:
        """Get price insights for a product query"""
        
        # Search for products
        search_results = await self.search_products(query, max_results=100)
        products = search_results.get("products", [])
        
        if not products:
            return {
                "query": query,
                "total_products": 0,
                "price_range": {"min": 0, "max": 0, "average": 0},
                "merchants": [],
                "categories": []
            }
        
        # Extract prices
        prices = []
        merchants = set()
        categories = set()
        
        for product in products:
            price = product.get("price", 0)
            if price > 0:
                prices.append(price)
            
            merchant = product.get("merchant", "")
            if merchant:
                merchants.add(merchant)
            
            category = product.get("category", "")
            if category:
                categories.add(category)
        
        # Calculate statistics
        if prices:
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)
            median_price = sorted(prices)[len(prices) // 2]
        else:
            min_price = max_price = avg_price = median_price = 0
        
        return {
            "query": query,
            "total_products": len(products),
            "price_range": {
                "min": round(min_price, 2),
                "max": round(max_price, 2),
                "average": round(avg_price, 2),
                "median": round(median_price, 2)
            },
            "merchants": list(merchants)[:10],  # Top 10 merchants
            "categories": list(categories)[:5],  # Top 5 categories
            "sample_products": products[:5]  # First 5 products as samples
        }
    
    async def get_trending_products(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get trending products (simulation using popular search terms)"""
        
        # Popular search terms by category
        trending_queries = {
            "electronics": ["iPhone", "Samsung Galaxy", "MacBook", "AirPods", "PlayStation"],
            "clothing": ["Nike shoes", "Adidas", "Levi's jeans", "designer handbags", "winter coats"],
            "home": ["coffee maker", "air fryer", "robot vacuum", "smart thermostat", "mattress"],
            "beauty": ["skincare routine", "makeup palette", "hair dryer", "perfume", "face mask"],
            "sports": ["fitness tracker", "yoga mat", "dumbbells", "running shoes", "protein powder"]
        }
        
        queries = trending_queries.get(category, trending_queries["electronics"])
        
        trending_products = []
        for query in queries[:3]:  # Limit to 3 queries to avoid rate limits
            try:
                results = await self.search_products(query, max_results=10)
                products = results.get("products", [])[:2]  # Top 2 from each query
                trending_products.extend(products)
            except Exception:
                continue
        
        return trending_products[:10]  # Return top 10 trending products
    
    def _process_shopping_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Google Shopping API response"""
        
        products = []
        raw_products = data.get("items", [])
        
        for item in raw_products:
            product = item.get("product", {})
            
            # Extract price
            price = 0
            price_data = product.get("inventories", [{}])[0] if product.get("inventories") else {}
            if price_data.get("price"):
                price = float(price_data["price"].get("value", 0))
            
            # Build product data
            product_data = {
                "id": product.get("googleId", ""),
                "title": product.get("title", ""),
                "description": product.get("description", ""),
                "price": price,
                "currency": price_data.get("price", {}).get("currency", "USD"),
                "brand": product.get("brand", ""),
                "mpn": product.get("mpn", ""),
                "gtin": product.get("gtins", [""])[0] if product.get("gtins") else "",
                "category": product.get("googleProductCategory", ""),
                "condition": price_data.get("condition", "new"),
                "availability": price_data.get("availability", "unknown"),
                "merchant": price_data.get("channel", ""),
                "image_url": product.get("images", [{}])[0].get("link", "") if product.get("images") else "",
                "product_url": product.get("link", "")
            }
            
            products.append(product_data)
        
        return {
            "products": products,
            "total_results": len(products),
            "search_metadata": {
                "query_time": datetime.now().isoformat(),
                "api_source": "google_shopping"
            }
        }
    
    async def get_product_reviews(self, product_id: str) -> Dict[str, Any]:
        """Get reviews for a specific product (if available)"""
        
        # Google Shopping API doesn't provide reviews directly
        # This would need to be implemented with a different service
        # or web scraping approach
        
        return {
            "product_id": product_id,
            "reviews": [],
            "average_rating": 0,
            "total_reviews": 0,
            "note": "Review data requires additional API integration"
        }
    
    async def compare_prices(self, query: str, merchants: List[str] = None) -> Dict[str, Any]:
        """Compare prices across different merchants"""
        
        search_results = await self.search_products(query, max_results=100)
        products = search_results.get("products", [])
        
        if merchants:
            # Filter by specified merchants
            products = [p for p in products if p.get("merchant", "").lower() in [m.lower() for m in merchants]]
        
        # Group by merchant
        merchant_prices = {}
        for product in products:
            merchant = product.get("merchant", "Unknown")
            price = product.get("price", 0)
            
            if price > 0:
                if merchant not in merchant_prices:
                    merchant_prices[merchant] = []
                merchant_prices[merchant].append({
                    "price": price,
                    "title": product.get("title", ""),
                    "url": product.get("product_url", "")
                })
        
        # Calculate averages per merchant
        merchant_comparison = []
        for merchant, price_data in merchant_prices.items():
            prices = [item["price"] for item in price_data]
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            
            merchant_comparison.append({
                "merchant": merchant,
                "average_price": round(avg_price, 2),
                "lowest_price": round(min_price, 2),
                "product_count": len(price_data),
                "sample_products": price_data[:3]  # Show 3 sample products
            })
        
        # Sort by average price
        merchant_comparison.sort(key=lambda x: x["average_price"])
        
        return {
            "query": query,
            "merchant_comparison": merchant_comparison,
            "best_deal": merchant_comparison[0] if merchant_comparison else None,
            "price_spread": {
                "lowest": merchant_comparison[0]["lowest_price"] if merchant_comparison else 0,
                "highest": merchant_comparison[-1]["average_price"] if merchant_comparison else 0
            }
        }
