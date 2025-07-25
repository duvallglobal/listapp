import asyncio
from typing import List, Dict, Any, Optional
import statistics
from datetime import datetime, timedelta
import random

from ..config import settings
from ..models.product import ProductListing, PriceRange
from ..models.analysis import MarketplaceAnalysis
from .ebay_service import EbayService


class MarketplaceService:

    PLATFORM_FEES = {
        "ebay": {
            "selling_fee": 0.1325,  # 13.25%
            "payment_fee": 0.0299,  # 2.99%
            "listing_fee": 0.30,
            "name": "eBay"
        },
        "facebook": {
            "selling_fee": 0.05,   # 5%
            "payment_fee": 0.0299, # 2.99%
            "listing_fee": 0.0,
            "name": "Facebook Marketplace"
        },
        "poshmark": {
            "selling_fee": 0.20,   # 20%
            "payment_fee": 0.0,    # Included
            "listing_fee": 0.0,
            "name": "Poshmark"
        },
        "mercari": {
            "selling_fee": 0.10,   # 10%
            "payment_fee": 0.0299, # 2.99%
            "listing_fee": 0.0,
            "name": "Mercari"
        },
        "amazon": {
            "selling_fee": 0.15,   # 15% average
            "payment_fee": 0.0299, # 2.99%
            "listing_fee": 0.99,   # Monthly
            "name": "Amazon"
        }
    }

    def __init__(self):
        self.ebay_service = EbayService()
        self.supported_platforms = settings.SUPPORTED_MARKETPLACES
        self.fee_structures = settings.MARKETPLACE_FEES

    async def analyze_all_marketplaces(self, query: str, product_category: Optional[str] = None) -> List[MarketplaceAnalysis]:
        """Analyze product across all supported marketplaces"""
        analyses = []

        # Create tasks for each marketplace
        tasks = []
        for platform in self.supported_platforms:
            task = self._analyze_single_marketplace(platform, query, product_category)
            tasks.append(task)

        # Execute all analyses in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Error analyzing {self.supported_platforms[i]}: {result}")
                continue

            if result:
                analyses.append(result)

        return analyses

    async def _analyze_single_marketplace(self, platform: str, query: str, category: Optional[str] = None) -> Optional[MarketplaceAnalysis]:
        """Analyze a single marketplace"""
        try:
            if platform == "ebay":
                return await self._analyze_ebay(query, category)
            elif platform == "amazon":
                return await self._analyze_amazon(query, category)
            elif platform == "facebook_marketplace":
                return await self._analyze_facebook_marketplace(query, category)
            elif platform == "poshmark":
                return await self._analyze_poshmark(query, category)
            elif platform == "mercari":
                return await self._analyze_mercari(query, category)
            elif platform == "depop":
                return await self._analyze_depop(query, category)
            elif platform == "vinted":
                return await self._analyze_vinted(query, category)
            else:
                return await self._mock_marketplace_analysis(platform, query)

        except Exception as e:
            print(f"Error analyzing {platform}: {e}")
            return None

    async def _analyze_ebay(self, query: str, category: Optional[str] = None) -> MarketplaceAnalysis:
        """Analyze eBay marketplace"""
        # Get market insights from eBay service
        insights = await self.ebay_service.get_market_insights(query)

        # Get completed listings for price analysis
        completed_listings = await self.ebay_service.search_completed_listings(query)

        # Calculate price range
        prices = [item['price'] for item in completed_listings if item.get('price', 0) > 0]
        price_range = None

        if prices:
            price_range = PriceRange(
                low=min(prices),
                median=sorted(prices)[len(prices)//2] if prices else 0,
                high=max(prices)
            )

        return MarketplaceAnalysis(
            platform="ebay",
            average_price=insights.get('average_sold_price'),
            price_range=price_range,
            total_active_listings=insights.get('total_active_listings'),
            sold_listings_30d=insights.get('total_completed_listings'),
            average_sell_time_days=insights.get('average_days_to_sell', 7),
            competition_level=insights.get('competition_level', 'medium'),
            trending=insights.get('trending', False),
            sample_listings=completed_listings[:5]
        )

    async def _analyze_amazon(self, query: str, category: Optional[str] = None) -> MarketplaceAnalysis:
        """Analyze Amazon marketplace (mock implementation)"""
        # Amazon doesn't provide public APIs for this type of analysis
        # This would require web scraping or third-party services
        return await self._mock_marketplace_analysis("amazon", query)

    async def _analyze_facebook_marketplace(self, query: str, category: Optional[str] = None) -> MarketplaceAnalysis:
        """Analyze Facebook Marketplace (mock implementation)"""
        # Facebook Marketplace doesn't have public APIs
        # This would require web scraping
        return await self._mock_marketplace_analysis("facebook_marketplace", query)

    async def _analyze_poshmark(self, query: str, category: Optional[str] = None) -> MarketplaceAnalysis:
        """Analyze Poshmark (mock implementation)"""
        return await self._mock_marketplace_analysis("poshmark", query)

    async def _analyze_mercari(self, query: str, category: Optional[str] = None) -> MarketplaceAnalysis:
        """Analyze Mercari (mock implementation)"""
        return await self._mock_marketplace_analysis("mercari", query)

    async def _analyze_depop(self, query: str, category: Optional[str] = None) -> MarketplaceAnalysis:
        """Analyze Depop (mock implementation)"""
        return await self._mock_marketplace_analysis("depop", query)

    async def _analyze_vinted(self, query: str, category: Optional[str] = None) -> MarketplaceAnalysis:
        """Analyze Vinted (mock implementation)"""
        return await self._mock_marketplace_analysis("vinted", query)

    async def _mock_marketplace_analysis(self, platform: str, query: str) -> MarketplaceAnalysis:
        """Generate mock marketplace analysis data"""
        # Generate realistic mock data
        base_price = random.uniform(25, 150)
        price_variation = 0.3

        low_price = base_price * (1 - price_variation)
        high_price = base_price * (1 + price_variation)
        median_price = base_price

        # Platform-specific adjustments
        platform_multipliers = {
            "amazon": 1.2,  # Generally higher prices
            "facebook_marketplace": 0.8,  # Generally lower prices
            "poshmark": 1.1,  # Fashion focus, slightly higher
            "mercari": 0.9,  # Competitive pricing
            "depop": 1.0,  # Vintage/unique items
            "vinted": 0.85,  # Budget-conscious buyers
            "ebay": 1.0  # Baseline
        }

        multiplier = platform_multipliers.get(platform, 1.0)

        price_range = PriceRange(
            low=round(low_price * multiplier, 2),
            median=round(median_price * multiplier, 2),
            high=round(high_price * multiplier, 2)
        )

        # Generate mock sample listings
        sample_listings = []
        for i in range(3):
            listing_price = random.uniform(price_range.low, price_range.high)
            sample_listings.append({
                "title": f"{query} - Sample Listing {i+1}",
                "price": round(listing_price, 2),
                "condition": random.choice(["New", "Like New", "Good", "Fair"]),
                "days_listed": random.randint(1, 30),
                "seller_rating": random.uniform(4.0, 5.0)
            })

        return MarketplaceAnalysis(
            platform=platform,
            average_price=price_range.median,
            price_range=price_range,
            total_active_listings=random.randint(10, 200),
            sold_listings_30d=random.randint(5, 50),
            average_sell_time_days=random.randint(3, 21),
            competition_level=random.choice(["low", "medium", "high"]),
            trending=random.choice([True, False]),
            seasonal_factor=random.uniform(0.8, 1.2),
            sample_listings=sample_listings
        )

    async def get_platform_fees(self, platform: str, price: float) -> Dict[str, float]:
        """Calculate fees for a specific platform"""
        if platform == "ebay":
            return await self.ebay_service.calculate_fees(price)

        # Use configured fee percentages for other platforms
        fee_percentage = self.fee_structures.get(platform, 0.10)  # Default 10%

        if platform == "amazon":
            # Amazon has more complex fee structure
            referral_fee = price * 0.15  # 15% referral fee
            fulfillment_fee = 3.00  # Estimated fulfillment fee
            total_fees = referral_fee + fulfillment_fee
        elif platform == "facebook_marketplace":
            # Facebook Marketplace fees
            total_fees = price * 0.05  # 5% selling fee
        elif platform == "poshmark":
            # Poshmark takes 20% commission
            total_fees = price * 0.20
        else:
            # Generic fee calculation
            total_fees = price * fee_percentage

        return {
            'platform_fee': total_fees,
            'payment_processing_fee': price * 0.029 + 0.30,  # Standard payment processing
            'total_fees': total_fees + (price * 0.029 + 0.30),
            'net_profit': price - total_fees - (price * 0.029 + 0.30),
            'fee_percentage': ((total_fees + (price * 0.029 + 0.30)) / price) * 100 if price > 0 else 0
        }

    async def get_best_platforms_for_category(self, category: str, price_range: PriceRange) -> List[str]:
        """Get best platforms for a specific category and price range"""
        platform_suitability = {
            "electronics": ["ebay", "amazon", "mercari", "facebook_marketplace"],
            "clothing": ["poshmark", "depop", "vinted", "mercari", "ebay"],
            "home_garden": ["facebook_marketplace", "ebay", "mercari"],
            "collectibles": ["ebay", "mercari", "depop"],
            "books_media": ["amazon", "ebay", "mercari"],
            "toys_games": ["ebay", "mercari", "facebook_marketplace"],
            "sports_outdoors": ["ebay", "facebook_marketplace", "mercari"]
        }

        # Adjust recommendations based on price range
        if price_range.median > 100:
            # Higher value items - platforms with better buyer protection
            preferred = ["ebay", "amazon", "poshmark"]
        elif price_range.median < 25:
            # Lower value items - platforms with lower fees
            preferred = ["facebook_marketplace", "mercari", "vinted"]
        else:
            # Medium value items - balanced approach
            preferred = ["ebay", "mercari", "poshmark"]

        category_platforms = platform_suitability.get(category.lower(), ["ebay", "mercari"])

        # Combine and prioritize
        combined = list(set(preferred + category_platforms))

        # Sort by preference (preferred platforms first)
        sorted_platforms = []
        for platform in preferred:
            if platform in combined:
                sorted_platforms.append(platform)

        for platform in category_platforms:
            if platform not in sorted_platforms:
                sorted_platforms.append(platform)

        return sorted_platforms[:5]  # Return top 5 recommendations

    async def get_market_trends(self, query: str, days: int = 30) -> Dict[str, Any]:
        """Get market trends for a product across platforms"""
        # This would analyze historical data to identify trends
        # For now, return mock trend data

        trend_direction = random.choice(["increasing", "decreasing", "stable"])
        trend_strength = random.uniform(0.1, 0.3)

        return {
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "price_volatility": random.uniform(0.05, 0.25),
            "demand_level": random.choice(["low", "medium", "high"]),
            "supply_level": random.choice(["low", "medium", "high"]),
            "seasonal_factor": random.uniform(0.8, 1.2),
            "recommendation": self._generate_trend_recommendation(trend_direction, trend_strength)
        }

    def _generate_trend_recommendation(self, direction: str, strength: float) -> str:
        """Generate recommendation based on trend analysis"""
        if direction == "increasing" and strength > 0.2:
            return "Strong upward trend - consider listing soon to capitalize on rising prices"
        elif direction == "decreasing" and strength > 0.2:
            return "Declining trend - consider competitive pricing or wait for market recovery"
        elif direction == "stable":
            return "Stable market - good time to list at market price"
        else:
            return "Moderate trend - monitor market conditions and adjust pricing accordingly"

    def analyze_pricing(self, market_data: Dict[str, Any], condition: str) -> Dict[str, Any]:
        """Analyze pricing data and generate recommendations"""

        try:
            # Extract prices from market data
            prices = []
            if "products" in market_data:
                for product in market_data["products"]:
                    if "price" in product and product["price"]:
                        try:
                            # Clean price string and convert to float
                            price_str = str(product["price"]).replace("$", "").replace(",", "")
                            price = float(price_str)
                            if 0 < price < 10000:  # Reasonable price range
                                prices.append(price)
                        except (ValueError, TypeError):
                            continue

            if not prices:
                # Fallback pricing if no market data
                base_prices = {
                    "new": 100,
                    "like_new": 85,
                    "excellent": 70,
                    "good": 55,
                    "fair": 40,
                    "poor": 25
                }
                estimated_price = base_prices.get(condition, 50)
                return {
                    "estimated_price": estimated_price,
                    "price_range": {
                        "min": estimated_price * 0.8,
                        "max": estimated_price * 1.2
                    },
                    "confidence": 0.3,
                    "data_points": 0,
                    "condition_adjustment": self._get_condition_multiplier(condition)
                }

            # Calculate statistics
            avg_price = statistics.mean(prices)
            median_price = statistics.median(prices)
            min_price = min(prices)
            max_price = max(prices)

            # Apply condition adjustment
            condition_multiplier = self._get_condition_multiplier(condition)
            estimated_price = median_price * condition_multiplier

            # Calculate confidence based on data points and price variance
            confidence = min(0.95, 0.5 + (len(prices) * 0.05))
            if len(prices) > 1:
                price_std = statistics.stdev(prices)
                coefficient_of_variation = price_std / avg_price if avg_price > 0 else 1
                confidence *= max(0.3, 1 - coefficient_of_variation)

            return {
                "estimated_price": round(estimated_price, 2),
                "price_range": {
                    "min": round(min_price * condition_multiplier, 2),
                    "max": round(max_price * condition_multiplier, 2)
                },
                "market_average": round(avg_price, 2),
                "market_median": round(median_price, 2),
                "confidence": round(confidence, 2),
                "data_points": len(prices),
                "condition_adjustment": condition_multiplier
            }

        except Exception as e:
            return {
                "estimated_price": 0,
                "price_range": {"min": 0, "max": 0},
                "confidence": 0.0,
                "error": str(e),
                "data_points": 0
            }

    def _get_condition_multiplier(self, condition: str) -> float:
        """Get price multiplier based on condition"""
        multipliers = {
            "new": 1.0,
            "like_new": 0.85,
            "excellent": 0.75,
            "good": 0.65,
            "fair": 0.50,
            "poor": 0.35
        }
        return multipliers.get(condition.lower(), 0.65)

    def calculate_platform_profits(self, selling_price: float) -> List[Dict[str, Any]]:
        """Calculate net profits for each platform"""

        recommendations = []

        for platform_id, fee_info in self.PLATFORM_FEES.items():
            # Calculate fees
            selling_fee = selling_price * fee_info["selling_fee"]
            payment_fee = selling_price * fee_info["payment_fee"]
            listing_fee = fee_info["listing_fee"]

            total_fees = selling_fee + payment_fee + listing_fee
            net_profit = selling_price - total_fees

            # Calculate suitability score (higher net profit = higher score)
            max_possible_profit = selling_price * 0.9  # 90% is ideal
            suitability = min(10, (net_profit / max_possible_profit) * 10) if max_possible_profit > 0 else 0

            recommendations.append({
                "platform": fee_info["name"],
                "platform_id": platform_id,
                "selling_price": selling_price,
                "fees": {
                    "selling_fee": round(selling_fee, 2),
                    "payment_fee": round(payment_fee, 2),
                    "listing_fee": round(listing_fee, 2),
                    "total": round(total_fees, 2)
                },
                "net_profit": round(net_profit, 2),
                "profit_margin": round((net_profit / selling_price) * 100, 1) if selling_price > 0 else 0,
                "suitability_score": round(suitability, 1)
            })

        # Sort by net profit descending
        recommendations.sort(key=lambda x: x["net_profit"], reverse=True)

        return recommendations