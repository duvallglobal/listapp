import requests
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import quote
import xml.etree.ElementTree as ET

from ..config import settings
from ..models.product import ProductListing, PriceRange

class EbayService:
    """Service for interacting with eBay APIs"""
    
    def __init__(self):
        self.app_id = settings.EBAY_APP_ID
        self.cert_id = settings.EBAY_CERT_ID
        self.dev_id = settings.EBAY_DEV_ID
        self.base_url = "https://svcs.ebay.com/services/search/FindingService/v1"
        self.shopping_url = "https://open.api.ebay.com/shopping"
    
    async def search_completed_listings(self, query: str, category_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for completed/sold listings on eBay"""
        if not self.app_id:
            return await self._mock_ebay_data(query)
        
        try:
            params = {
                'OPERATION-NAME': 'findCompletedItems',
                'SERVICE-VERSION': '1.0.0',
                'SECURITY-APPNAME': self.app_id,
                'RESPONSE-DATA-FORMAT': 'JSON',
                'keywords': query,
                'itemFilter(0).name': 'SoldItemsOnly',
                'itemFilter(0).value': 'true',
                'itemFilter(1).name': 'EndTimeFrom',
                'itemFilter(1).value': (datetime.now() - timedelta(days=90)).isoformat(),
                'sortOrder': 'EndTimeSoonest',
                'paginationInput.entriesPerPage': '100'
            }
            
            if category_id:
                params['categoryId'] = category_id
            
            response = await self._make_request(self.base_url, params)
            return self._parse_finding_response(response)
            
        except Exception as e:
            print(f"eBay API error: {e}")
            return await self._mock_ebay_data(query)
    
    async def search_active_listings(self, query: str, category_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for active listings on eBay"""
        if not self.app_id:
            return await self._mock_ebay_data(query, active=True)
        
        try:
            params = {
                'OPERATION-NAME': 'findItemsByKeywords',
                'SERVICE-VERSION': '1.0.0',
                'SECURITY-APPNAME': self.app_id,
                'RESPONSE-DATA-FORMAT': 'JSON',
                'keywords': query,
                'sortOrder': 'BestMatch',
                'paginationInput.entriesPerPage': '100'
            }
            
            if category_id:
                params['categoryId'] = category_id
            
            response = await self._make_request(self.base_url, params)
            return self._parse_finding_response(response)
            
        except Exception as e:
            print(f"eBay API error: {e}")
            return await self._mock_ebay_data(query, active=True)
    
    async def get_category_suggestions(self, query: str) -> List[Dict[str, Any]]:
        """Get category suggestions for a product query"""
        if not self.app_id:
            return self._mock_category_data()
        
        try:
            # Use eBay's category suggestion API
            url = "https://api.ebay.com/commerce/taxonomy/v1/category_tree/0/get_category_suggestions"
            
            headers = {
                'Authorization': f'Bearer {self._get_oauth_token()}',
                'Content-Type': 'application/json'
            }
            
            params = {'q': query}
            
            response = await self._make_request(url, params, headers=headers)
            return self._parse_category_response(response)
            
        except Exception as e:
            print(f"eBay category API error: {e}")
            return self._mock_category_data()
    
    async def calculate_fees(self, price: float, category_id: Optional[str] = None) -> Dict[str, float]:
        """Calculate eBay selling fees"""
        # eBay fee structure (simplified)
        insertion_fee = 0.0  # Free for most categories
        
        # Final value fee (varies by category)
        if category_id and category_id in ['9355', '1249']:  # Electronics categories
            final_value_fee_rate = 0.1275  # 12.75%
        else:
            final_value_fee_rate = 0.1325  # 13.25% standard
        
        final_value_fee = price * final_value_fee_rate
        
        # PayPal/Managed Payments fee
        payment_fee = price * 0.029 + 0.30  # 2.9% + $0.30
        
        total_fees = insertion_fee + final_value_fee + payment_fee
        net_profit = price - total_fees
        
        return {
            'insertion_fee': insertion_fee,
            'final_value_fee': final_value_fee,
            'payment_processing_fee': payment_fee,
            'total_fees': total_fees,
            'net_profit': net_profit,
            'fee_percentage': (total_fees / price) * 100 if price > 0 else 0
        }
    
    async def get_market_insights(self, query: str) -> Dict[str, Any]:
        """Get market insights for a product"""
        # Get both completed and active listings
        completed_listings = await self.search_completed_listings(query)
        active_listings = await self.search_active_listings(query)
        
        # Calculate market statistics
        insights = {
            'total_completed_listings': len(completed_listings),
            'total_active_listings': len(active_listings),
            'average_sold_price': 0,
            'price_range': {'min': 0, 'max': 0},
            'average_days_to_sell': 0,
            'competition_level': 'medium',
            'trending': False
        }
        
        if completed_listings:
            prices = [float(item.get('price', 0)) for item in completed_listings if item.get('price')]
            if prices:
                insights['average_sold_price'] = sum(prices) / len(prices)
                insights['price_range'] = {'min': min(prices), 'max': max(prices)}
        
        # Determine competition level
        if len(active_listings) > 100:
            insights['competition_level'] = 'high'
        elif len(active_listings) < 20:
            insights['competition_level'] = 'low'
        
        return insights
    
    async def _make_request(self, url: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make HTTP request to eBay API"""
        loop = asyncio.get_event_loop()
        
        def make_sync_request():
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        
        return await loop.run_in_executor(None, make_sync_request)
    
    def _parse_finding_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse eBay Finding API response"""
        items = []
        
        try:
            search_result = response.get('findCompletedItemsResponse', response.get('findItemsByKeywordsResponse', [{}]))[0]
            
            if 'searchResult' in search_result and search_result['searchResult'][0].get('item'):
                for item_data in search_result['searchResult'][0]['item']:
                    item = {
                        'title': item_data.get('title', [''])[0],
                        'price': float(item_data.get('sellingStatus', [{}])[0].get('currentPrice', [{'__value__': '0'}])[0]['__value__']),
                        'currency': item_data.get('sellingStatus', [{}])[0].get('currentPrice', [{'@currencyId': 'USD'}])[0].get('@currencyId', 'USD'),
                        'condition': item_data.get('condition', [{'conditionDisplayName': ['Unknown']}])[0].get('conditionDisplayName', ['Unknown'])[0],
                        'listing_type': item_data.get('listingInfo', [{}])[0].get('listingType', ['Unknown'])[0],
                        'end_time': item_data.get('listingInfo', [{}])[0].get('endTime', [''])[0],
                        'item_id': item_data.get('itemId', [''])[0],
                        'view_item_url': item_data.get('viewItemURL', [''])[0],
                        'location': item_data.get('location', [''])[0],
                        'shipping_cost': 0  # Would need additional API call
                    }
                    items.append(item)
        
        except Exception as e:
            print(f"Error parsing eBay response: {e}")
        
        return items
    
    def _parse_category_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse eBay category suggestion response"""
        categories = []
        
        try:
            if 'categorySuggestions' in response:
                for cat in response['categorySuggestions']:
                    categories.append({
                        'category_id': cat.get('categoryId'),
                        'category_name': cat.get('categoryName'),
                        'relevancy': cat.get('relevancy', 0)
                    })
        except Exception as e:
            print(f"Error parsing category response: {e}")
        
        return categories
    
    def _get_oauth_token(self) -> str:
        """Get OAuth token for eBay API (simplified)"""
        # In a real implementation, you'd implement OAuth flow
        return "mock_token"
    
    async def _mock_ebay_data(self, query: str, active: bool = False) -> List[Dict[str, Any]]:
        """Generate mock eBay data for testing"""
        import random
        
        # Generate realistic mock data based on query
        base_price = random.uniform(20, 200)
        
        items = []
        for i in range(random.randint(5, 25)):
            price_variation = random.uniform(0.7, 1.3)
            price = base_price * price_variation
            
            item = {
                'title': f"{query} - Item {i+1}",
                'price': round(price, 2),
                'currency': 'USD',
                'condition': random.choice(['New', 'Used', 'Refurbished']),
                'listing_type': random.choice(['FixedPrice', 'Auction']),
                'end_time': datetime.now().isoformat() if not active else (datetime.now() + timedelta(days=random.randint(1, 7))).isoformat(),
                'item_id': f"mock_{i+1}",
                'view_item_url': f"https://ebay.com/itm/mock_{i+1}",
                'location': random.choice(['United States', 'Canada', 'United Kingdom']),
                'shipping_cost': random.uniform(0, 15)
            }
            items.append(item)
        
        return items
    
    def _mock_category_data(self) -> List[Dict[str, Any]]:
        """Generate mock category data"""
        return [
            {'category_id': '9355', 'category_name': 'Electronics', 'relevancy': 0.9},
            {'category_id': '1249', 'category_name': 'Consumer Electronics', 'relevancy': 0.8},
            {'category_id': '293', 'category_name': 'Computers/Tablets & Networking', 'relevancy': 0.7}
        ]
