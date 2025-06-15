from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from src.config import Settings, get_settings
from src.services.cache_service import CacheService
from src.services.vision_service import VisionService
from src.services.marketplace_service import MarketplaceService
from src.services.ebay_service import EbayService
from src.agents.crew import ProductAnalysisCrew


@lru_cache()
def get_cache_service(settings: Annotated[Settings, Depends(get_settings)]) -> CacheService:
    return CacheService(settings.redis_url)


@lru_cache()
def get_vision_service(settings: Annotated[Settings, Depends(get_settings)]) -> VisionService:
    return VisionService(settings.google_vision_api_key)


@lru_cache()
def get_marketplace_service(settings: Annotated[Settings, Depends(get_settings)]) -> MarketplaceService:
    return MarketplaceService()


@lru_cache()
def get_ebay_service(settings: Annotated[Settings, Depends(get_settings)]) -> EbayService:
    return EbayService(settings.ebay_app_id)


def get_analysis_crew(
    settings: Annotated[Settings, Depends(get_settings)],
    cache_service: Annotated[CacheService, Depends(get_cache_service)]
) -> ProductAnalysisCrew:
    api_keys = {
        "openai": settings.openai_api_key,
        "google_vision": settings.google_vision_api_key,
        "ebay": settings.ebay_app_id
    }
    return ProductAnalysisCrew(api_keys, cache_service)