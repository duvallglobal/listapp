
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class MarketplacePlatform(Enum):
    EBAY = "ebay"
    AMAZON = "amazon"
    ETSY = "etsy"
    FACEBOOK_MARKETPLACE = "facebook_marketplace"
    MERCARI = "mercari"
    POSHMARK = "poshmark"
    DEPOP = "depop"
    VINTED = "vinted"

class FeeService:
    """Service for calculating marketplace fees and profit margins"""
    
    def __init__(self):
        # Platform fee structure based on the unified fee table
        self.fee_structure = {
            MarketplacePlatform.EBAY: {
                "listing_fee": 0.0,  # Free for most categories
                "final_value_fee": 0.1295,  # 12.95% for most categories
                "payment_processing_fee": 0.0295,  # 2.95%
                "international_fee": 0.015,  # 1.5% for international sales
                "store_subscription": {
                    "basic": 7.95,
                    "premium": 27.95,
                    "anchor": 349.95,
                    "enterprise": 2999.95
                },
                "insertion_fee_after_limit": 0.35,
                "category_exceptions": {
                    "motors": 0.10,  # 10% for motor vehicles
                    "real_estate": 35.0,  # Flat fee for real estate
                }
            },
            MarketplacePlatform.AMAZON: {
                "referral_fee": 0.15,  # 15% average (varies by category)
                "fulfillment_fee": 3.00,  # Average FBA fee
                "storage_fee": 0.75,  # Monthly storage fee per cubic foot
                "long_term_storage_fee": 6.90,  # Per cubic foot after 365 days
                "category_fees": {
                    "electronics": 0.08,  # 8%
                    "clothing": 0.17,  # 17%
                    "books": 0.15,  # 15%
                    "home_garden": 0.15,  # 15%
                    "toys_games": 0.15,  # 15%
                }
            },
            MarketplacePlatform.ETSY: {
                "listing_fee": 0.20,  # $0.20 per listing
                "transaction_fee": 0.065,  # 6.5%
                "payment_processing_fee": 0.03,  # 3% + $0.25
                "payment_processing_fixed": 0.25,
                "advertising_fee": 0.15,  # 15% of ad spend (optional)
                "currency_conversion_fee": 0.025,  # 2.5% for international
            },
            MarketplacePlatform.FACEBOOK_MARKETPLACE: {
                "selling_fee": 0.05,  # 5% for shipped items
                "payment_processing_fee": 0.029,  # 2.9% + $0.30
                "payment_processing_fixed": 0.30,
                "local_pickup_fee": 0.0,  # No fee for local pickup
            },
            MarketplacePlatform.MERCARI: {
                "selling_fee": 0.10,  # 10%
                "payment_processing_fee": 0.029,  # 2.9% + $0.30
                "payment_processing_fixed": 0.30,
                "authentication_fee": 5.00,  # For luxury items
            },
            MarketplacePlatform.POSHMARK: {
                "commission_under_15": 2.95,  # Flat $2.95 for sales under $15
                "commission_over_15": 0.20,  # 20% for sales $15 and over
                "expedited_shipping": 7.97,  # Optional expedited shipping
            },
            MarketplacePlatform.DEPOP: {
                "selling_fee": 0.10,  # 10%
                "paypal_fee": 0.029,  # 2.9% + $0.30 (if using PayPal)
                "paypal_fixed": 0.30,
                "depop_payments_fee": 0.029,  # 2.9% + $0.30
            },
            MarketplacePlatform.VINTED: {
                "selling_fee": 0.0,  # No selling fee for sellers
                "buyer_protection_fee": 0.05,  # 5% paid by buyer
                "payment_processing_fee": 0.03,  # 3% + €0.70 (paid by buyer)
            }
        }
    
    def calculate_fees(
        self, 
        platform: MarketplacePlatform, 
        sale_price: float, 
        shipping_cost: float = 0.0,
        item_cost: float = 0.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate all fees for a given platform and sale
        
        Args:
            platform: The marketplace platform
            sale_price: The sale price of the item
            shipping_cost: Shipping cost (if applicable)
            item_cost: Cost of the item to seller
            **kwargs: Additional platform-specific parameters
            
        Returns:
            Dictionary with fee breakdown and profit calculation
        """
        if platform not in self.fee_structure:
            raise ValueError(f"Platform {platform} not supported")
        
        fees = self.fee_structure[platform]
        total_fees = 0.0
        fee_breakdown = {}
        
        if platform == MarketplacePlatform.EBAY:
            total_fees, fee_breakdown = self._calculate_ebay_fees(sale_price, shipping_cost, fees, **kwargs)
        
        elif platform == MarketplacePlatform.AMAZON:
            total_fees, fee_breakdown = self._calculate_amazon_fees(sale_price, shipping_cost, fees, **kwargs)
        
        elif platform == MarketplacePlatform.ETSY:
            total_fees, fee_breakdown = self._calculate_etsy_fees(sale_price, shipping_cost, fees, **kwargs)
        
        elif platform == MarketplacePlatform.FACEBOOK_MARKETPLACE:
            total_fees, fee_breakdown = self._calculate_facebook_fees(sale_price, shipping_cost, fees, **kwargs)
        
        elif platform == MarketplacePlatform.MERCARI:
            total_fees, fee_breakdown = self._calculate_mercari_fees(sale_price, shipping_cost, fees, **kwargs)
        
        elif platform == MarketplacePlatform.POSHMARK:
            total_fees, fee_breakdown = self._calculate_poshmark_fees(sale_price, shipping_cost, fees, **kwargs)
        
        elif platform == MarketplacePlatform.DEPOP:
            total_fees, fee_breakdown = self._calculate_depop_fees(sale_price, shipping_cost, fees, **kwargs)
        
        elif platform == MarketplacePlatform.VINTED:
            total_fees, fee_breakdown = self._calculate_vinted_fees(sale_price, shipping_cost, fees, **kwargs)
        
        # Calculate profit
        gross_revenue = sale_price + shipping_cost
        net_revenue = gross_revenue - total_fees
        profit = net_revenue - item_cost
        profit_margin = (profit / gross_revenue) * 100 if gross_revenue > 0 else 0
        
        return {
            "platform": platform.value,
            "sale_price": sale_price,
            "shipping_cost": shipping_cost,
            "gross_revenue": gross_revenue,
            "total_fees": total_fees,
            "net_revenue": net_revenue,
            "item_cost": item_cost,
            "profit": profit,
            "profit_margin_percent": profit_margin,
            "fee_breakdown": fee_breakdown
        }
    
    def _calculate_ebay_fees(self, sale_price: float, shipping_cost: float, fees: Dict, **kwargs) -> tuple:
        """Calculate eBay specific fees"""
        total_fees = 0.0
        breakdown = {}
        
        # Final value fee (on item price + shipping)
        total_transaction = sale_price + shipping_cost
        final_value_fee = total_transaction * fees["final_value_fee"]
        breakdown["final_value_fee"] = final_value_fee
        total_fees += final_value_fee
        
        # Payment processing fee
        payment_fee = total_transaction * fees["payment_processing_fee"]
        breakdown["payment_processing_fee"] = payment_fee
        total_fees += payment_fee
        
        # International fee (if applicable)
        if kwargs.get("international", False):
            intl_fee = total_transaction * fees["international_fee"]
            breakdown["international_fee"] = intl_fee
            total_fees += intl_fee
        
        # Store subscription (monthly, prorated if needed)
        store_type = kwargs.get("store_subscription")
        if store_type and store_type in fees["store_subscription"]:
            breakdown["store_subscription"] = fees["store_subscription"][store_type]
        
        return total_fees, breakdown
    
    def _calculate_amazon_fees(self, sale_price: float, shipping_cost: float, fees: Dict, **kwargs) -> tuple:
        """Calculate Amazon specific fees"""
        total_fees = 0.0
        breakdown = {}
        
        # Referral fee
        category = kwargs.get("category", "default")
        referral_rate = fees["category_fees"].get(category, fees["referral_fee"])
        referral_fee = sale_price * referral_rate
        breakdown["referral_fee"] = referral_fee
        total_fees += referral_fee
        
        # FBA fulfillment fee (if using FBA)
        if kwargs.get("fba", False):
            breakdown["fulfillment_fee"] = fees["fulfillment_fee"]
            total_fees += fees["fulfillment_fee"]
            
            # Storage fees (if provided)
            storage_months = kwargs.get("storage_months", 1)
            cubic_feet = kwargs.get("cubic_feet", 1)
            storage_fee = fees["storage_fee"] * cubic_feet * storage_months
            breakdown["storage_fee"] = storage_fee
            total_fees += storage_fee
        
        return total_fees, breakdown
    
    def _calculate_etsy_fees(self, sale_price: float, shipping_cost: float, fees: Dict, **kwargs) -> tuple:
        """Calculate Etsy specific fees"""
        total_fees = 0.0
        breakdown = {}
        
        # Listing fee
        breakdown["listing_fee"] = fees["listing_fee"]
        total_fees += fees["listing_fee"]
        
        # Transaction fee
        transaction_fee = sale_price * fees["transaction_fee"]
        breakdown["transaction_fee"] = transaction_fee
        total_fees += transaction_fee
        
        # Payment processing fee
        total_transaction = sale_price + shipping_cost
        payment_fee = (total_transaction * fees["payment_processing_fee"]) + fees["payment_processing_fixed"]
        breakdown["payment_processing_fee"] = payment_fee
        total_fees += payment_fee
        
        return total_fees, breakdown
    
    def _calculate_facebook_fees(self, sale_price: float, shipping_cost: float, fees: Dict, **kwargs) -> tuple:
        """Calculate Facebook Marketplace fees"""
        total_fees = 0.0
        breakdown = {}
        
        # Selling fee (only for shipped items)
        if kwargs.get("shipped", True):
            selling_fee = sale_price * fees["selling_fee"]
            breakdown["selling_fee"] = selling_fee
            total_fees += selling_fee
            
            # Payment processing fee
            total_transaction = sale_price + shipping_cost
            payment_fee = (total_transaction * fees["payment_processing_fee"]) + fees["payment_processing_fixed"]
            breakdown["payment_processing_fee"] = payment_fee
            total_fees += payment_fee
        
        return total_fees, breakdown
    
    def _calculate_mercari_fees(self, sale_price: float, shipping_cost: float, fees: Dict, **kwargs) -> tuple:
        """Calculate Mercari fees"""
        total_fees = 0.0
        breakdown = {}
        
        # Selling fee
        selling_fee = sale_price * fees["selling_fee"]
        breakdown["selling_fee"] = selling_fee
        total_fees += selling_fee
        
        # Payment processing fee
        total_transaction = sale_price + shipping_cost
        payment_fee = (total_transaction * fees["payment_processing_fee"]) + fees["payment_processing_fixed"]
        breakdown["payment_processing_fee"] = payment_fee
        total_fees += payment_fee
        
        # Authentication fee (for luxury items)
        if kwargs.get("luxury_authentication", False):
            breakdown["authentication_fee"] = fees["authentication_fee"]
            total_fees += fees["authentication_fee"]
        
        return total_fees, breakdown
    
    def _calculate_poshmark_fees(self, sale_price: float, shipping_cost: float, fees: Dict, **kwargs) -> tuple:
        """Calculate Poshmark fees"""
        total_fees = 0.0
        breakdown = {}
        
        # Commission structure
        if sale_price < 15.0:
            commission = fees["commission_under_15"]
        else:
            commission = sale_price * fees["commission_over_15"]
        
        breakdown["commission"] = commission
        total_fees += commission
        
        return total_fees, breakdown
    
    def _calculate_depop_fees(self, sale_price: float, shipping_cost: float, fees: Dict, **kwargs) -> tuple:
        """Calculate Depop fees"""
        total_fees = 0.0
        breakdown = {}
        
        # Selling fee
        selling_fee = sale_price * fees["selling_fee"]
        breakdown["selling_fee"] = selling_fee
        total_fees += selling_fee
        
        # Payment processing fee
        total_transaction = sale_price + shipping_cost
        payment_method = kwargs.get("payment_method", "depop_payments")
        
        if payment_method == "paypal":
            payment_fee = (total_transaction * fees["paypal_fee"]) + fees["paypal_fixed"]
        else:
            payment_fee = (total_transaction * fees["depop_payments_fee"]) + fees["paypal_fixed"]
        
        breakdown["payment_processing_fee"] = payment_fee
        total_fees += payment_fee
        
        return total_fees, breakdown
    
    def _calculate_vinted_fees(self, sale_price: float, shipping_cost: float, fees: Dict, **kwargs) -> tuple:
        """Calculate Vinted fees (seller pays no fees)"""
        total_fees = 0.0
        breakdown = {}
        
        # Vinted charges buyers, not sellers
        breakdown["seller_fee"] = 0.0
        breakdown["note"] = "Fees paid by buyer"
        
        return total_fees, breakdown
    
    def compare_platforms(
        self, 
        sale_price: float, 
        item_cost: float = 0.0, 
        shipping_cost: float = 0.0,
        platforms: Optional[List[MarketplacePlatform]] = None
    ) -> List[Dict[str, Any]]:
        """
        Compare profitability across multiple platforms
        
        Args:
            sale_price: The sale price of the item
            item_cost: Cost of the item to seller
            shipping_cost: Shipping cost
            platforms: List of platforms to compare (defaults to all)
            
        Returns:
            List of platform comparisons sorted by profit
        """
        if platforms is None:
            platforms = list(MarketplacePlatform)
        
        comparisons = []
        
        for platform in platforms:
            try:
                result = self.calculate_fees(platform, sale_price, shipping_cost, item_cost)
                comparisons.append(result)
            except Exception as e:
                logger.warning(f"Failed to calculate fees for {platform}: {str(e)}")
                continue
        
        # Sort by profit (highest first)
        comparisons.sort(key=lambda x: x["profit"], reverse=True)
        
        return comparisons
    
    def get_recommended_platform(
        self, 
        sale_price: float, 
        item_cost: float = 0.0,
        category: str = "",
        shipping_cost: float = 0.0
    ) -> Dict[str, Any]:
        """
        Get the recommended platform based on highest profit
        
        Returns:
            Platform recommendation with rationale
        """
        comparisons = self.compare_platforms(sale_price, item_cost, shipping_cost)
        
        if not comparisons:
            return {
                "recommended_platform": None,
                "reason": "No platforms available for comparison"
            }
        
        best_platform = comparisons[0]
        
        # Add rationale
        profit_difference = 0
        if len(comparisons) > 1:
            second_best = comparisons[1]
            profit_difference = best_platform["profit"] - second_best["profit"]
        
        return {
            "recommended_platform": best_platform["platform"],
            "expected_profit": best_platform["profit"],
            "profit_margin": best_platform["profit_margin_percent"],
            "total_fees": best_platform["total_fees"],
            "net_revenue": best_platform["net_revenue"],
            "profit_advantage": profit_difference,
            "fee_breakdown": best_platform["fee_breakdown"],
            "all_comparisons": comparisons
        }
