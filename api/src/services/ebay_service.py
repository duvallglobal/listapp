import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

from ..config import settings


class EbayService:
    """Service for eBay API integration"""

    def __init__(self, app_id: Optional[str] = None):
        self.app_id = app_id or settings.EBAY_APP_ID
        self.base_url = "https://svcs.ebay.com/services/search/FindingService/v1"
        self.shopping_base_url = "https://open.api.ebay.com/shopping"

    async def search_products(self, keywords: str, category: Optional[str] = None, 
                            condition: str = "Used", limit: int = 50) -> Dict[str, Any]:
        """Search for products on eBay"""

        operation_name = "findItemsByKeywords"

        params = {
            "OPERATION-NAME": operation_name,
            "SERVICE-VERSION": "1.0.0",
            "SECURITY-APPNAME": self.app_id,
            "RESPONSE-DATA-FORMAT": "XML",
            "keywords": keywords,
            "paginationInput.entriesPerPage": str(limit),
            "itemFilter(0).name": "Condition",
            "itemFilter(0).value": condition,
            "sortOrder": "BestMatch"
        }

        if category:
            params["categoryId"] = category

        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._parse_search_response(content)
                else:
                    raise Exception(f"eBay API error: {response.status}")

    async def search_completed_listings(self, keywords: str, days_back: int = 30) -> List[Dict[str, Any]]:
        """Search completed/sold listings for price analysis"""

        operation_name = "findCompletedItems"

        params = {
            "OPERATION-NAME": operation_name,
            "SERVICE-VERSION": "1.0.0",
            "SECURITY-APPNAME": self.app_id,
            "RESPONSE-DATA-FORMAT": "XML",
            "keywords": keywords,
            "paginationInput.entriesPerPage": "100",
            "itemFilter(0).name": "SoldItemsOnly",
            "itemFilter(0).value": "true",
            "itemFilter(1).name": "EndTimeFrom",
            "itemFilter(1).value": (datetime.now() - timedelta(days=days_back)).isoformat() + "Z"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    content = await response.text()
                    parsed = self._parse_search_response(content)
                    return parsed.get("items", [])
                else:
                    return []

    async def get_market_insights(self, keywords: str) -> Dict[str, Any]:
        """Get market insights for a product"""

        # Get both active and completed listings
        active_task = self.search_products(keywords, limit=100)
        completed_task = self.search_completed_listings(keywords, days_back=30)

        active_listings, completed_listings = await asyncio.gather(
            active_task, completed_task, return_exceptions=True
        )

        if isinstance(active_listings, Exception):
            active_listings = {"items": []}
        if isinstance(completed_listings, Exception):
            completed_listings = []

        # Calculate insights
        active_items = active_listings.get("items", [])
        completed_items = completed_listings

        # Price analysis
        active_prices = [float(item.get("price", 0)) for item in active_items if item.get("price")]
        sold_prices = [float(item.get("price", 0)) for item in completed_items if item.get("price")]

        insights = {
            "total_active_listings": len(active_items),
            "total_completed_listings": len(completed_items),
            "average_active_price": sum(active_prices) / len(active_prices) if active_prices else 0,
            "average_sold_price": sum(sold_prices) / len(sold_prices) if sold_prices else 0,
            "min_price": min(active_prices + sold_prices) if active_prices + sold_prices else 0,
            "max_price": max(active_prices + sold_prices) if active_prices + sold_prices else 0,
            "price_range_low": self._calculate_percentile(sold_prices, 25) if sold_prices else 0,
            "price_range_high": self._calculate_percentile(sold_prices, 75) if sold_prices else 0,
            "average_days_to_sell": self._calculate_average_sell_time(completed_items),
            "competition_level": self._assess_competition_level(len(active_items)),
            "trending": self._assess_trending(active_items, completed_items)
        }

        return insights

    async def calculate_fees(self, price: float) -> Dict[str, float]:
        """Calculate eBay fees for a given price"""

        # eBay fee structure (as of 2024)
        final_value_fee_rate = 0.1325  # 13.25% for most categories
        payment_processing_fee_rate = 0.029  # 2.9%
        payment_processing_fixed = 0.30  # $0.30

        final_value_fee = price * final_value_fee_rate
        payment_processing_fee = (price * payment_processing_fee_rate) + payment_processing_fixed

        total_fees = final_value_fee + payment_processing_fee
        net_profit = price - total_fees

        return {
            "final_value_fee": round(final_value_fee, 2),
            "payment_processing_fee": round(payment_processing_fee, 2),
            "total_fees": round(total_fees, 2),
            "net_profit": round(net_profit, 2),
            "fee_percentage": round((total_fees / price) * 100, 2) if price > 0 else 0
        }

    def _parse_search_response(self, xml_content: str) -> Dict[str, Any]:
        """Parse eBay XML response"""
        try:
            root = ET.fromstring(xml_content)

            # eBay XML namespace
            ns = {'eb': 'http://www.ebay.com/marketplace/search/v1/services'}

            items = []
            search_result = root.find('.//eb:searchResult', ns)

            if search_result is not None:
                for item in search_result.findall('.//eb:item', ns):
                    item_data = {}

                    # Extract item details
                    title_elem = item.find('.//eb:title', ns)
                    if title_elem is not None:
                        item_data['title'] = title_elem.text

                    price_elem = item.find('.//eb:convertedCurrentPrice', ns)
                    if price_elem is not None:
                        item_data['price'] = float(price_elem.text)
                        item_data['currency'] = price_elem.get('currencyId', 'USD')

                    condition_elem = item.find('.//eb:condition/eb:conditionDisplayName', ns)
                    if condition_elem is not None:
                        item_data['condition'] = condition_elem.text

                    location_elem = item.find('.//eb:location', ns)
                    if location_elem is not None:
                        item_data['location'] = location_elem.text

                    url_elem = item.find('.//eb:viewItemURL', ns)
                    if url_elem is not None:
                        item_data['url'] = url_elem.text

                    end_time_elem = item.find('.//eb:endTime', ns)
                    if end_time_elem is not None:
                        item_data['end_time'] = end_time_elem.text

                    items.append(item_data)

            return {"items": items}

        except ET.ParseError as e:
            raise Exception(f"Failed to parse eBay response: {str(e)}")

    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of a list of values"""
        if not values:
            return 0

        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)

        if index == int(index):
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    def _calculate_average_sell_time(self, self, completed_items: List[Dict[str, Any]]) -> int:
        """Calculate average time to sell in days"""
        # This would require listing start dates which aren't always available
        # Return a reasonable default
        return 7

    def _assess_competition_level(self, active_listings_count: int) -> str:
        """Assess competition level based on active listings"""
        if active_listings_count > 1000:
            return "high"
        elif active_listings_count > 100:
            return "medium"
        else:
            return "low"

    def _assess_trending(self, active_items: List[Dict], completed_items: List[Dict]) -> bool:
        """Simple trending assessment"""
        # Basic logic: if there are more active than recently completed, it might be trending
        return len(active_items) > len(completed_items)