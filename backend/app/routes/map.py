from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.map_schema import HeatmapFeatureCollection, HeatmapFeature, HeatmapProperties, HeatmapMeta
from app.core.security import get_current_user
from app.schemas.auth_schema import UserResponse
from app.db.session import get_db
from app.models.hex_risk import HexRiskScore
import json
from datetime import datetime
import h3

router = APIRouter()

def hex_to_geojson_polygon(hex_id):
    """Convert an H3 hex ID to a GeoJSON polygon geometry."""
    try:
        boundary = h3.cell_to_boundary(hex_id)
        # h3 v4 returns (lat, lon) tuples; GeoJSON needs [lon, lat]
        coords = [[lon, lat] for lat, lon in boundary]
        coords.append(coords[0])  # Close the polygon
        return {
            "type": "Polygon",
            "coordinates": [coords]
        }
    except Exception:
        return {"type": "Polygon", "coordinates": []}

@router.get("/heatmap", response_model=HeatmapFeatureCollection)
async def get_heatmap(
    bbox: str = Query(..., description="comma separated min_lon,min_lat,max_lon,max_lat"),
    min_tier: str = Query("LOW"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        coords = [float(c) for c in bbox.split(",")]
        if len(coords) != 4:
            raise ValueError()
    except:
        return HeatmapFeatureCollection(meta=HeatmapMeta(hex_count=0, generated_at=datetime.utcnow(), bbox=[]), features=[])

    min_lon, min_lat, max_lon, max_lat = coords
    
    # Simple bounding box query using lat/lon columns (replaces PostGIS ST_Intersects)
    query = select(HexRiskScore).where(
        HexRiskScore.center_lat >= min_lat,
        HexRiskScore.center_lat <= max_lat,
        HexRiskScore.center_lon >= min_lon,
        HexRiskScore.center_lon <= max_lon,
        HexRiskScore.is_stale == False
    )
    
    result = await db.execute(query)
    rows = result.scalars().all()
    
    features = []
    for row in rows:
        # RBAC: Only department users see narrative and top_sector
        narrative = row.alert_narrative if current_user.role in ['department_user', 'coordinator', 'admin'] else None
        sector = row.top_sector if current_user.role in ['department_user', 'coordinator', 'admin'] else None
        
        feature = HeatmapFeature(
            geometry=hex_to_geojson_polygon(row.hex_id),
            properties=HeatmapProperties(
                hex_id=row.hex_id,
                risk_score=float(row.risk_score),
                risk_tier=row.risk_tier,
                signal_count=row.signal_count,
                top_signal=row.top_signal_type,
                top_sector=sector,
                alert_narrative=narrative,
                computed_at=row.computed_at
            )
        )
        features.append(feature)
        
    return HeatmapFeatureCollection(
        meta=HeatmapMeta(
            hex_count=len(features),
            generated_at=datetime.utcnow(),
            bbox=coords
        ),
        features=features
    )

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@router.websocket("/ws/live-risk")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    # Basic token validation (in prod, decode JWT properly here)
    if not token:
        await websocket.close(code=1008)
        return
        
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
