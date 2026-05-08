from sqlalchemy import Column, String, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from geoalchemy2 import Geometry
from app.db.session import Base

class AreaRiskCache(Base):
    __tablename__ = "area_risk_cache"

    area_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    geom = Column(Geometry('POLYGON', srid=4326), nullable=False, index=True)
    public_score = Column(Numeric(3, 1), nullable=False)
    safety_status = Column(String(10), nullable=False)
    cached_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
