
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta

from ..dependencies import get_current_user, get_supabase_client
from ..models.analysis import AnalysisHistoryItem

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/analyses")
async def get_analysis_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Get paginated analysis history for user"""
    
    try:
        query = supabase.table("analysis_history")\
            .select("*")\
            .eq("user_id", user.id)\
            .order("created_at", desc=True)
        
        if start_date:
            query = query.gte("created_at", start_date.isoformat())
        
        if end_date:
            query = query.lte("created_at", end_date.isoformat())
        
        # Get total count
        count_result = query.execute(count="exact")
        total_count = count_result.count
        
        # Get paginated results
        result = query.range(offset, offset + limit - 1).execute()
        
        return {
            "analyses": result.data,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not fetch analysis history")

@router.get("/analyses/{analysis_id}")
async def get_analysis_details(
    analysis_id: str,
    user = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Get detailed analysis results"""
    
    try:
        result = supabase.table("analysis_history")\
            .select("*")\
            .eq("id", analysis_id)\
            .eq("user_id", user.id)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not fetch analysis details")

@router.delete("/analyses/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    user = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Delete a specific analysis"""
    
    try:
        result = supabase.table("analysis_history")\
            .delete()\
            .eq("id", analysis_id)\
            .eq("user_id", user.id)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {"message": "Analysis deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not delete analysis")

@router.get("/stats")
async def get_user_stats(
    days: int = Query(30, ge=1, le=365),
    user = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
):
    """Get user analytics and usage statistics"""
    
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get analysis count by day
        result = supabase.table("analysis_history")\
            .select("created_at")\
            .eq("user_id", user.id)\
            .gte("created_at", start_date.isoformat())\
            .execute()
        
        # Process data for charts
        daily_stats = {}
        total_analyses = len(result.data)
        
        for analysis in result.data:
            date = analysis["created_at"][:10]  # Extract date part
            daily_stats[date] = daily_stats.get(date, 0) + 1
        
        return {
            "total_analyses": total_analyses,
            "period_days": days,
            "daily_breakdown": daily_stats,
            "average_per_day": total_analyses / days if days > 0 else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not fetch user statistics")
