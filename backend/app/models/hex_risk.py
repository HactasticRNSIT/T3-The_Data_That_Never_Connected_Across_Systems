from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime, Text
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.db.session import Base

class HexRiskScore(Base):
    __tablename__ = "hex_risk_scores"

    hex_id = Column(String(20), primary_key=True)
    geom = Column(Geometry('POLYGON', srid=4326), nullable=False, index=True)
    risk_score = Column(Numeric(5, 2), nullable=False, default=0.0, index=True)
    risk_tier = Column(String(20), nullable=False, default='LOW', index=True)
    signal_count = Column(Integer, nullable=False, default=0)
    top_sector = Column(String(50))
    top_signal_type = Column(String(100))
    alert_narrative = Column(Text)
    last_signal_at = Column(DateTime(timezone=True))
    computed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_stale = Column(Boolean, default=False)
