
from typing import List, Dict, Any, Optional
from crewai_tools import BaseTool
import asyncio
import aiohttp

from src.services.marketplace_service import MarketplaceService
from src.services.ebay_service import EbayService


class MarketplaceResearchTool(BaseTool):
    name: str = "marketplace_research"
    description: str = "Research product prices and market data across multiple marketplaces"
    
    def __init__(self, marketplace_service: MarketplaceService, ebay_service: EbayService):
        super().__init__()
        self.marketplace_service = marketplace_service
        self.ebay_service = ebay_service
    
    def _run(self, product_name: str, category: str, condition: str = "good") -> Dict[str, Any]:
        """
        Research market prices across multiple platforms
        """
        try:
            # Research on multiple platforms
            research_results = {
                "ebay": self._research_ebay(product_name, category, condition),
                "amazon": self._research_amazon(product_name, category),
                "facebook_marketplace": self._research_facebook(product_name, category),
                "mercari": self._research_mercari(product_name, category),
                "poshmark": self._research_poshmark(product_name, category)
            }
            
            # Aggregate results
            aggregated_data = self._aggregate_research_data(research_results)
            
            return {
                "platform_data": research_results,
                "market_summary": aggregated_data,
                "research_timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            return {"error": f"Marketplace research failed: {str(e)}"}
    
    def _research_ebay(self, product_name: str, category: str, condition: str) -> Dict[str, Any]:
        """
        Research eBay prices and listings
        """
        try:
            # Use eBay API to search for similar products
            search_results = self.ebay_service.search_products(
                keywords=product_name,
                category=category,
                condition=condition,
                limit=50
            )
            
            # Extract pricing data
            prices = []
            sold_listings = []
            active_listings = []
            
            for item in search_results.get("items", []):
                price = item.get("price", {}).get("value", 0)
                if price > 0:
                    prices.append(price)
                    
                    if item.get("selling_state") == "ENDED":
                        sold_listings.append(item)
                    else:
                        active_listings.append(item)
            
            # Calculate statistics
            if prices:
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)
                median_price = sorted(prices)[len(prices) // 2]
            else:
                avg_price = min_price = max_price = median_price = 0
            
            return {
                "platform": "ebay",
                "total_listings": len(search_results.get("items", [])),
                "sold_listings_count": len(sold_listings),
                "active_listings_count": len(active_listings),
                "price_statistics": {
                    "average": avg_price,
                    "minimum": min_price,
                    "maximum": max_price,
                    "median": median_price
                },
                "sample_listings": search_results.get("items", [])[:10],
                "market_demand": self._assess_demand(sold_listings, active_listings)
            }
            
        except Exception as e:
            return {"platform": "ebay", "error": str(e)}
    
    def _research_amazon(self, product_name: str, category: str) -> Dict[str, Any]:
        """
        Research Amazon prices (simulated - would need Amazon API)
        """
        # This would require Amazon API integration
        # For now, return simulated data structure
        return {
            "platform": "amazon",
            "note": "Amazon research requires API integration",
            "estimated_price_range": {
                "min": 0,
                "max": 0,
                "average": 0
            },
            "availability": "unknown"
        }
    
    def _research_facebook(self, product_name: str, category: str) -> Dict[str, Any]:
        """
        Research Facebook Marketplace (simulated)
        """
        return {
            "platform": "facebook_marketplace",
            "note": "Facebook Marketplace research requires web scraping",
            "local_market_indicator": True,
            "estimated_price_range": {
                "min": 0,
                "max": 0,
                "average": 0
            }
        }
    
    def _research_mercari(self, product_name: str, category: str) -> Dict[str, Any]:
        """
        Research Mercari prices (simulated)
        """
        return {
            "platform": "mercari",
            "note": "Mercari research requires API integration",
            "estimated_price_range": {
                "min": 0,
                "max": 0,
                "average": 0
            }
        }
    
    def _research_poshmark(self, product_name: str, category: str) -> Dict[str, Any]:
        """
        Research Poshmark prices (simulated)
        """
        return {
            "platform": "poshmark",
            "note": "Poshmark research requires API integration",
            "category_focus": "clothing_and_accessories",
            "estimated_price_range": {
                "min": 0,
                "max": 0,
                "average": 0
            }
        }
    
    def _aggregate_research_data(self, research_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate research data from all platforms
        """
        all_prices = []
        platform_count = 0
        total_listings = 0
        
        for platform, data in research_results.items():
            if "error" not in data and "price_statistics" in data:
                stats = data["price_statistics"]
                if stats["average"] > 0:
                    all_prices.extend([stats["minimum"], stats["average"], stats["maximum"]])
                    platform_count += 1
                    total_listings += data.get("total_listings", 0)
        
        if all_prices:
            market_summary = {
                "overall_price_range": {
                    "minimum": min(all_prices),
                    "maximum": max(all_prices),
                    "average": sum(all_prices) / len(all_prices)
                },
                "platforms_with_data": platform_count,
                "total_listings_found": total_listings,
                "market_activity": "high" if total_listings > 100 else "medium" if total_listings > 20 else "low"
            }
        else:
            market_summary = {
                "overall_price_range": {"minimum": 0, "maximum": 0, "average": 0},
                "platforms_with_data": 0,
                "total_listings_found": 0,
                "market_activity": "unknown"
            }
        
        return market_summary
    
    def _assess_demand(self, sold_listings: List[Dict], active_listings: List[Dict]) -> str:
        """
        Assess market demand based on sold vs active listings
        """
        if not sold_listings and not active_listings:
            return "unknown"
        
        total_listings = len(sold_listings) + len(active_listings)
        sold_ratio = len(sold_listings) / total_listings if total_listings > 0 else 0
        
        if sold_ratio > 0.7:
            return "high"
        elif sold_ratio > 0.4:
            return "medium"
        else:
            return "low"


class MarketplaceAgent:
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.marketplace_service = MarketplaceService()
        self.ebay_service = EbayService(api_keys.get("ebay"))
    
    def get_tools(self) -> List[BaseTool]:
        return [MarketplaceResearchTool(self.marketplace_service, self.ebay_service)]
    
    def research_product_market(self, product_name: str, category: str, condition: str = "good") -> Dict[str, Any]:
        """
        Main method to research product market data
        """
        tool = MarketplaceResearchTool(self.marketplace_service, self.ebay_service)
        return tool._run(product_name, category, condition)
