
from typing import List, Dict, Any, Optional
from crewai_tools import BaseTool
import statistics

from src.tools.fee_calculator import FeeCalculator


class PricingStrategyTool(BaseTool):
    name: str = "pricing_strategy"
    description: str = "Determine optimal pricing strategies for maximum profit across platforms"
    
    def __init__(self, fee_calculator: FeeCalculator):
        super().__init__()
        self.fee_calculator = fee_calculator
    
    def _run(self, product_data: Dict[str, Any], market_data: Dict[str, Any], user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculate optimal pricing strategy
        """
        try:
            # Extract market price data
            market_prices = self._extract_market_prices(market_data)
            
            # Calculate pricing strategies
            strategies = {
                "competitive": self._calculate_competitive_pricing(market_prices),
                "quick_sale": self._calculate_quick_sale_pricing(market_prices),
                "premium": self._calculate_premium_pricing(market_prices),
                "auction_start": self._calculate_auction_pricing(market_prices)
            }
            
            # Calculate platform-specific pricing
            platform_pricing = self._calculate_platform_pricing(strategies, market_data)
            
            # Generate recommendations
            recommendations = self._generate_pricing_recommendations(
                strategies, platform_pricing, product_data, user_preferences
            )
            
            return {
                "pricing_strategies": strategies,
                "platform_specific": platform_pricing,
                "recommendations": recommendations,
                "market_analysis": self._analyze_market_position(market_prices, strategies)
            }
            
        except Exception as e:
            return {"error": f"Pricing analysis failed: {str(e)}"}
    
    def _extract_market_prices(self, market_data: Dict[str, Any]) -> List[float]:
        """
        Extract all price points from market research data
        """
        prices = []
        
        platform_data = market_data.get("platform_data", {})
        for platform, data in platform_data.items():
            if "price_statistics" in data:
                stats = data["price_statistics"]
                if stats.get("average", 0) > 0:
                    prices.extend([
                        stats.get("minimum", 0),
                        stats.get("average", 0),
                        stats.get("maximum", 0)
                    ])
        
        # Remove zeros and sort
        return sorted([p for p in prices if p > 0])
    
    def _calculate_competitive_pricing(self, market_prices: List[float]) -> Dict[str, Any]:
        """
        Calculate competitive pricing strategy
        """
        if not market_prices:
            return {"price": 0, "strategy": "no_market_data"}
        
        median_price = statistics.median(market_prices)
        avg_price = statistics.mean(market_prices)
        
        # Competitive price is slightly below median
        competitive_price = median_price * 0.95
        
        return {
            "price": round(competitive_price, 2),
            "strategy": "competitive",
            "market_position": "slightly_below_median",
            "expected_sale_speed": "medium",
            "confidence": 0.8
        }
    
    def _calculate_quick_sale_pricing(self, market_prices: List[float]) -> Dict[str, Any]:
        """
        Calculate quick sale pricing strategy
        """
        if not market_prices:
            return {"price": 0, "strategy": "no_market_data"}
        
        # Quick sale at 75-80% of median
        median_price = statistics.median(market_prices)
        quick_sale_price = median_price * 0.78
        
        return {
            "price": round(quick_sale_price, 2),
            "strategy": "quick_sale",
            "market_position": "below_market",
            "expected_sale_speed": "fast",
            "confidence": 0.9
        }
    
    def _calculate_premium_pricing(self, market_prices: List[float]) -> Dict[str, Any]:
        """
        Calculate premium pricing strategy
        """
        if not market_prices:
            return {"price": 0, "strategy": "no_market_data"}
        
        # Premium pricing at 110-115% of median
        median_price = statistics.median(market_prices)
        premium_price = median_price * 1.12
        
        return {
            "price": round(premium_price, 2),
            "strategy": "premium",
            "market_position": "above_market",
            "expected_sale_speed": "slow",
            "confidence": 0.6
        }
    
    def _calculate_auction_pricing(self, market_prices: List[float]) -> Dict[str, Any]:
        """
        Calculate auction starting price
        """
        if not market_prices:
            return {"price": 0, "strategy": "no_market_data"}
        
        # Auction start at 60-70% of median to encourage bidding
        median_price = statistics.median(market_prices)
        auction_start = median_price * 0.65
        
        return {
            "price": round(auction_start, 2),
            "strategy": "auction_start",
            "market_position": "well_below_market",
            "expected_final_price": round(median_price * 0.95, 2),
            "confidence": 0.7
        }
    
    def _calculate_platform_pricing(self, strategies: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate optimal pricing for each platform
        """
        platform_pricing = {}
        
        platforms = ["ebay", "amazon", "facebook_marketplace", "mercari", "poshmark"]
        
        for platform in platforms:
            # Get platform-specific data
            platform_data = market_data.get("platform_data", {}).get(platform, {})
            
            # Calculate fees
            base_price = strategies["competitive"]["price"]
            fees = self.fee_calculator.calculate_platform_fees(platform, base_price)
            
            # Adjust pricing based on fees
            optimal_price = self._adjust_price_for_fees(base_price, fees)
            
            platform_pricing[platform] = {
                "optimal_price": round(optimal_price, 2),
                "estimated_fees": fees,
                "net_profit": round(optimal_price - fees["total_fees"], 2),
                "profit_margin": round(((optimal_price - fees["total_fees"]) / optimal_price) * 100, 1) if optimal_price > 0 else 0,
                "platform_suitability": self._assess_platform_suitability(platform, platform_data)
            }
        
        return platform_pricing
    
    def _adjust_price_for_fees(self, base_price: float, fees: Dict[str, Any]) -> float:
        """
        Adjust price to account for platform fees
        """
        total_fee_rate = fees.get("total_fee_percentage", 0)
        fixed_fees = fees.get("fixed_fees", 0)
        
        # Adjust price to maintain desired profit margin
        if total_fee_rate > 0:
            adjusted_price = (base_price + fixed_fees) / (1 - total_fee_rate / 100)
        else:
            adjusted_price = base_price + fixed_fees
        
        return adjusted_price
    
    def _assess_platform_suitability(self, platform: str, platform_data: Dict[str, Any]) -> str:
        """
        Assess how suitable a platform is for this product
        """
        if "error" in platform_data:
            return "unknown"
        
        listings_count = platform_data.get("total_listings", 0)
        
        if listings_count > 50:
            return "excellent"
        elif listings_count > 20:
            return "good"
        elif listings_count > 5:
            return "fair"
        else:
            return "poor"
    
    def _generate_pricing_recommendations(
        self, 
        strategies: Dict[str, Any], 
        platform_pricing: Dict[str, Any], 
        product_data: Dict[str, Any], 
        user_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive pricing recommendations
        """
        user_prefs = user_preferences or {}
        priority = user_prefs.get("priority", "balanced")  # quick_sale, max_profit, balanced
        
        # Determine best strategy based on user preferences
        if priority == "quick_sale":
            recommended_strategy = "quick_sale"
        elif priority == "max_profit":
            recommended_strategy = "premium"
        else:
            recommended_strategy = "competitive"
        
        # Find best platform
        best_platform = max(
            platform_pricing.items(),
            key=lambda x: x[1]["net_profit"] if x[1]["platform_suitability"] != "poor" else 0
        )
        
        return {
            "recommended_strategy": recommended_strategy,
            "recommended_price": strategies[recommended_strategy]["price"],
            "best_platform": best_platform[0],
            "best_platform_details": best_platform[1],
            "alternative_strategies": [
                {
                    "strategy": strategy,
                    "price": data["price"],
                    "pros": self._get_strategy_pros(strategy),
                    "cons": self._get_strategy_cons(strategy)
                }
                for strategy, data in strategies.items()
                if strategy != recommended_strategy and data["price"] > 0
            ],
            "pricing_tips": self._generate_pricing_tips(strategies, platform_pricing)
        }
    
    def _get_strategy_pros(self, strategy: str) -> List[str]:
        """
        Get pros for each pricing strategy
        """
        pros_map = {
            "competitive": ["Balanced approach", "Good sale probability", "Market-aligned pricing"],
            "quick_sale": ["Fast turnover", "High sale probability", "Quick cash flow"],
            "premium": ["Maximum profit potential", "Higher perceived value"],
            "auction_start": ["Potential for bidding wars", "Market-driven pricing"]
        }
        return pros_map.get(strategy, [])
    
    def _get_strategy_cons(self, strategy: str) -> List[str]:
        """
        Get cons for each pricing strategy
        """
        cons_map = {
            "competitive": ["Average profits", "High competition"],
            "quick_sale": ["Lower profit margins", "May signal quality issues"],
            "premium": ["Slower sales", "Limited buyer pool", "Higher risk"],
            "auction_start": ["Unpredictable final price", "Time investment required"]
        }
        return cons_map.get(strategy, [])
    
    def _generate_pricing_tips(self, strategies: Dict[str, Any], platform_pricing: Dict[str, Any]) -> List[str]:
        """
        Generate helpful pricing tips
        """
        tips = []
        
        # General tips
        tips.append("Monitor competitor prices regularly and adjust accordingly")
        tips.append("Consider seasonal demand patterns for your product category")
        
        # Platform-specific tips
        best_platforms = sorted(
            platform_pricing.items(),
            key=lambda x: x[1]["net_profit"],
            reverse=True
        )[:2]
        
        if best_platforms:
            tips.append(f"Consider listing on {best_platforms[0][0]} for maximum profit")
        
        # Strategy-specific tips
        price_range = [s["price"] for s in strategies.values() if s["price"] > 0]
        if price_range:
            price_spread = max(price_range) - min(price_range)
            if price_spread > min(price_range) * 0.5:
                tips.append("Wide price range suggests volatile market - consider starting with competitive pricing")
        
        return tips
    
    def _analyze_market_position(self, market_prices: List[float], strategies: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market position for each strategy
        """
        if not market_prices:
            return {"analysis": "insufficient_market_data"}
        
        median_price = statistics.median(market_prices)
        
        analysis = {}
        for strategy, data in strategies.items():
            if data["price"] > 0:
                position_ratio = data["price"] / median_price
                
                if position_ratio < 0.8:
                    position = "well_below_market"
                elif position_ratio < 0.95:
                    position = "below_market"
                elif position_ratio < 1.05:
                    position = "at_market"
                elif position_ratio < 1.2:
                    position = "above_market"
                else:
                    position = "well_above_market"
                
                analysis[strategy] = {
                    "market_position": position,
                    "price_ratio": round(position_ratio, 2),
                    "competitive_advantage": self._assess_competitive_advantage(position)
                }
        
        return analysis
    
    def _assess_competitive_advantage(self, position: str) -> str:
        """
        Assess competitive advantage based on market position
        """
        advantage_map = {
            "well_below_market": "high_price_advantage",
            "below_market": "moderate_price_advantage",
            "at_market": "neutral",
            "above_market": "quality_positioning_needed",
            "well_above_market": "premium_justification_required"
        }
        return advantage_map.get(position, "unknown")


class PricingAgent:
    def __init__(self):
        self.fee_calculator = FeeCalculator()
    
    def get_tools(self) -> List[BaseTool]:
        return [PricingStrategyTool(self.fee_calculator)]
    
    def analyze_pricing(self, product_data: Dict[str, Any], market_data: Dict[str, Any], user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main method to analyze pricing strategies
        """
        tool = PricingStrategyTool(self.fee_calculator)
        return tool._run(product_data, market_data, user_preferences)
