from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import uuid

class SignalVectorItem(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    signal_type: str
    severity: float = Field(..., ge=0, le=1)
    hour_of_day: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)
    count: int = Field(default=1, ge=1)

class IngestBatch(BaseModel):
    batch_id: uuid.UUID
    timestamp_utc: datetime
    vectors: List[SignalVectorItem]

class IngestResponse(BaseModel):
    status: str
    batch_id: uuid.UUID
    vectors_received: int
    task_id: str
    message: str
