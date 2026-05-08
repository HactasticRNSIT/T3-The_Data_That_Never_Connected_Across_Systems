from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class HeatmapMeta(BaseModel):
    hex_count: int
    generated_at: datetime
    bbox: List[float]

class HeatmapProperties(BaseModel):
    hex_id: str
    risk_score: float
    risk_tier: str
    signal_count: int
    top_signal: Optional[str] = None
    top_sector: Optional[str] = None
    alert_narrative: Optional[str] = None
    computed_at: datetime

class HeatmapFeature(BaseModel):
    type: str = "Feature"
    geometry: Any
    properties: HeatmapProperties

class HeatmapFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    meta: HeatmapMeta
    features: List[HeatmapFeature]
