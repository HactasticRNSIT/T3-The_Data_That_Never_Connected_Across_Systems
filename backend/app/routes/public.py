from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
from app.schemas.public_schema import PublicSafetyResponse, AreaInfo, AreaCenter
from datetime import datetime

router = APIRouter()

@router.get("/area-safety", response_model=PublicSafetyResponse)
async def get_area_safety(
    request: Request,
    lat: float = Query(...),
    lon: float = Query(...),
    radius_m: int = Query(500),
    db: AsyncSession = Depends(get_db)
):
    # In a full impl, we'd check area_risk_cache first.
    # For demo, compute on the fly using ST_DWithin
    
    query = text("""
        SELECT COALESCE(AVG(risk_score), 0) as avg_score
        FROM hex_risk_scores
        WHERE ST_DWithin(
            geom::geography, 
            ST_MakePoint(:lon, :lat)::geography, 
            :radius_m
        )
        AND is_stale = FALSE
    """)
    
    result = await db.execute(query, {
        "lon": lon, "lat": lat, "radius_m": radius_m
    })
    
    avg_score = float(result.scalar() or 0.0)
    status = "UNSAFE" if avg_score > 5.0 else "SAFE"
    
    return PublicSafetyResponse(
        area=AreaInfo(
            center=AreaCenter(lat=lat, lon=lon),
            radius_m=radius_m
        ),
        safety_score=round(avg_score, 1),
        safety_status=status,
        last_updated=datetime.utcnow()
    )
