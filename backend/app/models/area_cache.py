from sqlalchemy import Column, String, Float, Numeric, DateTime
from sqlalchemy.sql import func
import uuid
from app.db.session import Base

class AreaRiskCache(Base):
    __tablename__ = "area_risk_cache"

    area_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Store center point instead of PostGIS geometry
    center_lat = Column(Float, nullable=False, default=0.0)
    center_lon = Column(Float, nullable=False, default=0.0)
    public_score = Column(Numeric(3, 1), nullable=False)
    safety_status = Column(String(10), nullable=False)
    cached_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
