
from typing import List, Dict, Any, Optional
from crewai_tools import BaseTool

from src.models.recommendation import PlatformRecommendation, PlatformFeatures, FeeStructure, AudienceInsights
from src.tools.fee_calculator import FeeCalculator


class PlatformRecommendationTool(BaseTool):
    name: str = "platform_recommendation"
    description: str = "Recommend the best selling platforms for products based on comprehensive analysis"
    
    def __init__(self, fee_calculator: FeeCalculator):
        super().__init__()
        self.fee_calculator = fee_calculator
        self.platform_profiles = self._initialize_platform_profiles()
    
    def _run(self, product_data: Dict[str, Any], market_data: Dict[str, Any], pricing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate platform recommendations
        """
        try:
            # Analyze each platform
            platform_recommendations = {}
            
            for platform in ["ebay", "amazon", "facebook_marketplace", "mercari", "poshmark"]:
                recommendation = self._analyze_platform(
                    platform, product_data, market_data, pricing_data
                )
                platform_recommendations[platform] = recommendation
            
            # Rank platforms
            ranked_platforms = self._rank_platforms(platform_recommendations)
            
            # Generate summary recommendations
            summary = self._generate_summary_recommendations(ranked_platforms, product_data)
            
            return {
                "platform_recommendations": platform_recommendations,
                "ranked_platforms": ranked_platforms,
                "summary": summary,
                "recommendation_confidence": self._calculate_overall_confidence(platform_recommendations)
            }
            
        except Exception as e:
            return {"error": f"Platform recommendation failed: {str(e)}"}
    
    def _initialize_platform_profiles(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize platform-specific profiles and characteristics
        """
        return {
            "ebay": {
                "audience_demographics": {
                    "age_range": "25-65",
                    "income_level": "middle_to_high",
                    "buying_behavior": "research_focused"
                },
                "platform_strengths": ["auction_format", "collectibles", "used_items", "global_reach"],
                "platform_weaknesses": ["complex_fees", "learning_curve", "competition"],
                "category_focus": ["electronics", "collectibles", "automotive", "fashion"],
                "fee_structure": {
                    "listing_fee": 0.0,
                    "final_value_fee": 10.0,
                    "payment_processing": 2.9,
                    "store_subscription": 21.95
                },
                "ease_of_use": "moderate",
                "time_to_list": 15
            },
            "amazon": {
                "audience_demographics": {
                    "age_range": "18-55",
                    "income_level": "all_levels",
                    "buying_behavior": "convenience_focused"
                },
                "platform_strengths": ["huge_audience", "trust", "fulfillment", "prime"],
                "platform_weaknesses": ["high_competition", "strict_policies", "fees"],
                "category_focus": ["books", "electronics", "home", "health"],
                "fee_structure": {
                    "listing_fee": 0.0,
                    "referral_fee": 15.0,
                    "fulfillment_fee": 3.0,
                    "storage_fee": 0.69
                },
                "ease_of_use": "difficult",
                "time_to_list": 30
            },
            "facebook_marketplace": {
                "audience_demographics": {
                    "age_range": "20-50",
                    "income_level": "all_levels",
                    "buying_behavior": "local_focused"
                },
                "platform_strengths": ["no_fees", "local_sales", "large_audience", "easy_communication"],
                "platform_weaknesses": ["local_only", "no_seller_protection", "casual_buyers"],
                "category_focus": ["furniture", "electronics", "vehicles", "home"],
                "fee_structure": {
                    "listing_fee": 0.0,
                    "final_value_fee": 0.0,
                    "payment_processing": 2.9
                },
                "ease_of_use": "easy",
                "time_to_list": 5
            },
            "mercari": {
                "audience_demographics": {
                    "age_range": "18-40",
                    "income_level": "low_to_middle",
                    "buying_behavior": "deal_focused"
                },
                "platform_strengths": ["simple_interface", "mobile_first", "fast_payments"],
                "platform_weaknesses": ["smaller_audience", "lower_prices", "limited_categories"],
                "category_focus": ["fashion", "electronics", "beauty", "toys"],
                "fee_structure": {
                    "listing_fee": 0.0,
                    "final_value_fee": 10.0,
                    "payment_processing": 2.9
                },
                "ease_of_use": "easy",
                "time_to_list": 8
            },
            "poshmark": {
                "audience_demographics": {
                    "age_range": "20-45",
                    "income_level": "middle_to_high",
                    "buying_behavior": "fashion_focused"
                },
                "platform_strengths": ["fashion_community", "social_features", "authentication"],
                "platform_weaknesses": ["fashion_only", "higher_fees", "social_requirements"],
                "category_focus": ["fashion", "accessories", "beauty"],
                "fee_structure": {
                    "listing_fee": 0.0,
                    "final_value_fee": 20.0,
                    "under_15_fee": 2.95
                },
                "ease_of_use": "easy",
                "time_to_list": 10
            }
        }
    
    def _analyze_platform(self, platform: str, product_data: Dict[str, Any], market_data: Dict[str, Any], pricing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a specific platform for the given product
        """
        profile = self.platform_profiles.get(platform, {})
        product_category = product_data.get("identification", {}).get("category", "other")
        
        # Calculate scores
        audience_match_score = self._calculate_audience_match(product_data, profile)
        category_fit_score = self._calculate_category_fit(product_category, profile)
        fee_competitiveness_score = self._calculate_fee_competitiveness(platform, pricing_data)
        ease_of_use_score = self._calculate_ease_of_use(profile)
        market_data_score = self._calculate_market_data_score(platform, market_data)
        
        # Calculate overall score
        overall_score = (
            audience_match_score * 0.25 +
            category_fit_score * 0.25 +
            fee_competitiveness_score * 0.20 +
            ease_of_use_score * 0.15 +
            market_data_score * 0.15
        )
        
        # Get financial projections
        financial_projections = self._calculate_financial_projections(platform, pricing_data)
        
        # Generate specific recommendations
        strengths, weaknesses, tips = self._generate_platform_specific_advice(
            platform, product_data, profile, overall_score
        )
        
        return {
            "platform_name": platform,
            "overall_score": round(overall_score, 1),
            "detailed_scores": {
                "audience_match": round(audience_match_score, 1),
                "category_fit": round(category_fit_score, 1),
                "fee_competitiveness": round(fee_competitiveness_score, 1),
                "ease_of_use": round(ease_of_use_score, 1),
                "market_presence": round(market_data_score, 1)
            },
            "financial_projections": financial_projections,
            "platform_features": self._extract_platform_features(profile),
            "audience_insights": self._extract_audience_insights(profile, product_data),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "optimization_tips": tips,
            "estimated_time_to_list": profile.get("time_to_list", 15),
            "estimated_time_to_sell": self._estimate_time_to_sell(platform, market_data, overall_score)
        }
    
    def _calculate_audience_match(self, product_data: Dict[str, Any], profile: Dict[str, Any]) -> float:
        """
        Calculate how well the product matches the platform's audience
        """
        base_score = 7.0
        
        # Product condition vs audience preferences
        condition = product_data.get("identification", {}).get("condition", "good")
        if condition in ["new", "like_new"] and "high_quality" in profile.get("audience_demographics", {}).get("buying_behavior", ""):
            base_score += 1.5
        elif condition in ["good", "very_good"]:
            base_score += 0.5
        
        # Price range considerations
        # This would be enhanced with actual price data
        
        return min(10.0, max(0.0, base_score))
    
    def _calculate_category_fit(self, product_category: str, profile: Dict[str, Any]) -> float:
        """
        Calculate how well the product category fits the platform
        """
        category_focus = profile.get("category_focus", [])
        
        if product_category in category_focus:
            return 9.0
        elif any(cat in product_category for cat in category_focus):
            return 7.0
        else:
            return 5.0
    
    def _calculate_fee_competitiveness(self, platform: str, pricing_data: Dict[str, Any]) -> float:
        """
        Calculate fee competitiveness score
        """
        platform_pricing = pricing_data.get("platform_specific", {}).get(platform, {})
        profit_margin = platform_pricing.get("profit_margin", 0)
        
        if profit_margin >= 80:
            return 10.0
        elif profit_margin >= 70:
            return 8.5
        elif profit_margin >= 60:
            return 7.0
        elif profit_margin >= 50:
            return 5.5
        elif profit_margin >= 40:
            return 4.0
        else:
            return 2.0
    
    def _calculate_ease_of_use(self, profile: Dict[str, Any]) -> float:
        """
        Calculate ease of use score
        """
        ease_mapping = {
            "easy": 9.0,
            "moderate": 7.0,
            "difficult": 4.0
        }
        return ease_mapping.get(profile.get("ease_of_use", "moderate"), 7.0)
    
    def _calculate_market_data_score(self, platform: str, market_data: Dict[str, Any]) -> float:
        """
        Calculate score based on market data availability and activity
        """
        platform_data = market_data.get("platform_data", {}).get(platform, {})
        
        if "error" in platform_data:
            return 5.0  # Neutral score for no data
        
        total_listings = platform_data.get("total_listings", 0)
        sold_listings = platform_data.get("sold_listings_count", 0)
        
        # Score based on market activity
        if total_listings > 100:
            activity_score = 9.0
        elif total_listings > 50:
            activity_score = 8.0
        elif total_listings > 20:
            activity_score = 6.5
        elif total_listings > 5:
            activity_score = 5.0
        else:
            activity_score = 3.0
        
        # Adjust based on sold ratio
        if sold_listings > 0 and total_listings > 0:
            sold_ratio = sold_listings / total_listings
            if sold_ratio > 0.5:
                activity_score += 1.0
            elif sold_ratio > 0.3:
                activity_score += 0.5
        
        return min(10.0, activity_score)
    
    def _calculate_financial_projections(self, platform: str, pricing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate financial projections for the platform
        """
        platform_pricing = pricing_data.get("platform_specific", {}).get(platform, {})
        
        optimal_price = platform_pricing.get("optimal_price", 0)
        estimated_fees = platform_pricing.get("estimated_fees", {})
        net_profit = platform_pricing.get("net_profit", 0)
        profit_margin = platform_pricing.get("profit_margin", 0)
        
        return {
            "estimated_gross_revenue": optimal_price,
            "estimated_fees": estimated_fees.get("total_fees", 0),
            "estimated_net_profit": net_profit,
            "profit_margin_percentage": profit_margin
        }
    
    def _extract_platform_features(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract platform features from profile
        """
        strengths = profile.get("platform_strengths", [])
        
        return {
            "auction_format": "auction_format" in strengths,
            "fixed_price": True,  # Most platforms support this
            "best_offer": "best_offer" in strengths,
            "local_pickup": "local_sales" in strengths,
            "international_shipping": "global_reach" in strengths,
            "promoted_listings": "promoted_listings" in strengths,
            "mobile_app_quality": "mobile_first" in strengths and "excellent" or "good",
            "seller_protection": "trust" in strengths and "premium" or "standard"
        }
    
    def _extract_audience_insights(self, profile: Dict[str, Any], product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract audience insights for the platform
        """
        demographics = profile.get("audience_demographics", {})
        category = product_data.get("identification", {}).get("category", "other")
        
        return {
            "primary_demographics": demographics,
            "buying_behavior": {"primary_motivation": demographics.get("buying_behavior", "value")},
            "price_sensitivity": demographics.get("income_level", "medium").replace("_to_", "/"),
            "category_popularity": self._get_category_popularity(category, profile)
        }
    
    def _get_category_popularity(self, category: str, profile: Dict[str, Any]) -> float:
        """
        Get category popularity score for the platform
        """
        category_focus = profile.get("category_focus", [])
        
        if category in category_focus:
            return 9.0
        elif any(cat in category for cat in category_focus):
            return 7.0
        else:
            return 5.0
    
    def _generate_platform_specific_advice(self, platform: str, product_data: Dict[str, Any], profile: Dict[str, Any], overall_score: float) -> tuple:
        """
        Generate platform-specific strengths, weaknesses, and tips
        """
        strengths = profile.get("platform_strengths", [])
        weaknesses = profile.get("platform_weaknesses", [])
        
        # Generate optimization tips
        tips = []
        
        if platform == "ebay":
            tips.extend([
                "Use high-quality photos with good lighting",
                "Write detailed descriptions with keywords",
                "Consider starting with auction format for rare items",
                "Offer fast shipping to compete effectively"
            ])
        elif platform == "facebook_marketplace":
            tips.extend([
                "Respond quickly to messages",
                "Offer local pickup to avoid shipping",
                "Use Facebook groups for additional exposure",
                "Price competitively for local market"
            ])
        elif platform == "mercari":
            tips.extend([
                "Use the mobile app for best experience",
                "Price items competitively",
                "Ship quickly to maintain ratings",
                "Cross-list on other platforms"
            ])
        
        # Add condition-based tips
        condition = product_data.get("identification", {}).get("condition", "good")
        if condition in ["new", "like_new"]:
            tips.append("Highlight the excellent condition in title and photos")
        elif condition in ["acceptable", "poor"]:
            tips.append("Be transparent about condition and price accordingly")
        
        return strengths, weaknesses, tips
    
    def _estimate_time_to_sell(self, platform: str, market_data: Dict[str, Any], overall_score: float) -> Optional[int]:
        """
        Estimate time to sell in days
        """
        platform_data = market_data.get("platform_data", {}).get(platform, {})
        market_activity = platform_data.get("market_demand", "medium")
        
        base_days = {
            "ebay": 7,
            "amazon": 3,
            "facebook_marketplace": 5,
            "mercari": 10,
            "poshmark": 14
        }.get(platform, 10)
        
        # Adjust based on market activity
        if market_activity == "high":
            base_days = int(base_days * 0.7)
        elif market_activity == "low":
            base_days = int(base_days * 1.5)
        
        # Adjust based on overall score
        if overall_score >= 8.0:
            base_days = int(base_days * 0.8)
        elif overall_score <= 5.0:
            base_days = int(base_days * 1.3)
        
        return base_days
    
    def _rank_platforms(self, platform_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Rank platforms by overall score
        """
        platforms = []
        
        for platform, recommendation in platform_recommendations.items():
            if "error" not in recommendation:
                platforms.append({
                    "platform": platform,
                    "score": recommendation["overall_score"],
                    "net_profit": recommendation["financial_projections"]["estimated_net_profit"],
                    "recommendation": recommendation
                })
        
        # Sort by score, then by net profit
        return sorted(platforms, key=lambda x: (x["score"], x["net_profit"]), reverse=True)
    
    def _generate_summary_recommendations(self, ranked_platforms: List[Dict[str, Any]], product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary recommendations
        """
        if not ranked_platforms:
            return {"message": "No suitable platforms found"}
        
        top_platform = ranked_platforms[0]
        category = product_data.get("identification", {}).get("category", "unknown")
        
        summary = {
            "primary_recommendation": {
                "platform": top_platform["platform"],
                "score": top_platform["score"],
                "reason": f"Best overall score ({top_platform['score']}/10) with highest projected profit"
            },
            "alternative_options": [],
            "category_specific_advice": self._get_category_advice(category),
            "general_tips": [
                "Always use high-quality photos",
                "Write clear, honest descriptions",
                "Price competitively based on market research",
                "Respond promptly to buyer inquiries"
            ]
        }
        
        # Add alternative options
        for platform_data in ranked_platforms[1:3]:  # Top 2 alternatives
            summary["alternative_options"].append({
                "platform": platform_data["platform"],
                "score": platform_data["score"],
                "reason": f"Alternative with score {platform_data['score']}/10"
            })
        
        return summary
    
    def _get_category_advice(self, category: str) -> List[str]:
        """
        Get category-specific advice
        """
        advice_map = {
            "electronics": [
                "Include model numbers and specifications",
                "Test functionality before listing",
                "Include original accessories if available"
            ],
            "clothing": [
                "Provide accurate measurements",
                "Show any wear or defects clearly",
                "Consider Poshmark for designer items"
            ],
            "collectibles": [
                "Research rarity and value thoroughly",
                "Consider eBay auctions for rare items",
                "Provide detailed condition assessment"
            ]
        }
        
        return advice_map.get(category, [
            "Research similar items before pricing",
            "Be honest about condition",
            "Use relevant keywords in title"
        ])
    
    def _calculate_overall_confidence(self, platform_recommendations: Dict[str, Any]) -> float:
        """
        Calculate overall confidence in recommendations
        """
        valid_scores = []
        
        for recommendation in platform_recommendations.values():
            if "error" not in recommendation:
                valid_scores.append(recommendation["overall_score"])
        
        if not valid_scores:
            return 0.0
        
        # Confidence based on score range and availability of data
        max_score = max(valid_scores)
        score_range = max(valid_scores) - min(valid_scores)
        
        # High confidence if there's a clear winner
        if max_score >= 8.0 and score_range >= 2.0:
            return 0.9
        elif max_score >= 7.0:
            return 0.8
        elif max_score >= 6.0:
            return 0.7
        else:
            return 0.6


class RecommendationAgent:
    def __init__(self):
        self.fee_calculator = FeeCalculator()
    
    def get_tools(self) -> List[BaseTool]:
        return [PlatformRecommendationTool(self.fee_calculator)]
    
    def recommend_platforms(self, product_data: Dict[str, Any], market_data: Dict[str, Any], pricing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to generate platform recommendations
        """
        tool = PlatformRecommendationTool(self.fee_calculator)
        return tool._run(product_data, market_data, pricing_data)
