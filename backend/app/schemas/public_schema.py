from pydantic import BaseModel
from datetime import datetime

class AreaCenter(BaseModel):
    lat: float
    lon: float

class AreaInfo(BaseModel):
    center: AreaCenter
    radius_m: int

class PublicSafetyResponse(BaseModel):
    area: AreaInfo
    safety_score: float
    safety_status: str
    last_updated: datetime
