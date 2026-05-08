from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.hex_risk import HexRiskScore
from app.schemas.public_schema import PublicSafetyResponse, AreaInfo, AreaCenter
from datetime import datetime
import math

router = APIRouter()

def haversine_distance_m(lat1, lon1, lat2, lon2):
    """Calculate approximate distance in meters between two points."""
    R = 6371000  # Earth radius in meters
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

@router.get("/area-safety", response_model=PublicSafetyResponse)
async def get_area_safety(
    request: Request,
    lat: float = Query(...),
    lon: float = Query(...),
    radius_m: int = Query(500),
    db: AsyncSession = Depends(get_db)
):
    # Approximate bounding box to narrow down candidates
    delta_lat = radius_m / 111000.0
    delta_lon = radius_m / (111000.0 * max(math.cos(math.radians(lat)), 0.01))
    
    query = select(HexRiskScore).where(
        HexRiskScore.center_lat >= lat - delta_lat,
        HexRiskScore.center_lat <= lat + delta_lat,
        HexRiskScore.center_lon >= lon - delta_lon,
        HexRiskScore.center_lon <= lon + delta_lon,
        HexRiskScore.is_stale == False
    )
    
    result = await db.execute(query)
    rows = result.scalars().all()
    
    # Further filter by actual distance
    nearby = [r for r in rows if haversine_distance_m(lat, lon, r.center_lat, r.center_lon) <= radius_m]
    
    if nearby:
        avg_score = sum(float(r.risk_score) for r in nearby) / len(nearby)
    else:
        avg_score = 0.0
    
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
