
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional

from ..dependencies import get_current_user, get_supabase_client, require_subscription
from ..models.user import UserProfile, UserUpdate
from ..config import settings

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/profile")
async def get_user_profile(
    user = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Get current user profile"""
    
    try:
        # Get user profile from database
        result = supabase.table("profiles").select("*").eq("id", user.id).execute()
        
        if not result.data:
            # Create profile if doesn't exist
            profile_data = {
                "id": user.id,
                "email": user.email,
                "full_name": user.user_metadata.get("full_name", ""),
                "created_at": user.created_at
            }
            
            supabase.table("profiles").insert(profile_data).execute()
            return profile_data
        
        return result.data[0]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch user profile"
        )

@router.put("/profile")
async def update_user_profile(
    profile_update: UserUpdate,
    user = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Update user profile"""
    
    try:
        update_data = profile_update.dict(exclude_unset=True)
        update_data["updated_at"] = "now()"
        
        result = supabase.table("profiles").update(update_data).eq("id", user.id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return result.data[0]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update profile"
        )

@router.get("/subscription")
async def get_subscription_status(
    user = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Get user subscription status"""
    
    try:
        result = supabase.table("subscriptions").select("*").eq("user_id", user.id).execute()
        
        if not result.data:
            return {
                "status": "none",
                "tier": "free_trial",
                "usage": {"analyses_used": 0, "analyses_limit": 2}
            }
        
        subscription = result.data[0]
        
        # Get usage stats
        usage_result = supabase.table("analysis_history")\
            .select("*", count="exact")\
            .eq("user_id", user.id)\
            .gte("created_at", subscription.get("current_period_start"))\
            .execute()
        
        tier_config = settings.SUBSCRIPTION_TIERS.get(subscription["tier"], settings.SUBSCRIPTION_TIERS["free_trial"])
        
        return {
            "status": subscription["status"],
            "tier": subscription["tier"],
            "current_period_start": subscription["current_period_start"],
            "current_period_end": subscription["current_period_end"],
            "usage": {
                "analyses_used": usage_result.count,
                "analyses_limit": tier_config["analysis_limit"]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch subscription status"
        )

@router.delete("/account")
async def delete_user_account(
    user = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Delete user account and all associated data"""
    
    try:
        # Delete user data in correct order (respecting foreign keys)
        tables_to_clear = [
            "analysis_history",
            "subscriptions", 
            "profiles"
        ]
        
        for table in tables_to_clear:
            supabase.table(table).delete().eq("user_id", user.id).execute()
        
        # Delete auth user
        supabase.auth.admin.delete_user(user.id)
        
        return {"message": "Account successfully deleted"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete account"
        )
