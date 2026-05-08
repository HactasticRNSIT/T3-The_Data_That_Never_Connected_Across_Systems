from sqlalchemy import Column, String, Numeric, DateTime, Text, ForeignKey, Index
from sqlalchemy.sql import func
import uuid
from app.db.session import Base

class DepartmentAlert(Base):
    __tablename__ = "department_alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hex_id = Column(String(20), ForeignKey('hex_risk_scores.hex_id'), nullable=False, index=True)
    triggered_by = Column(String(50), nullable=False)
    old_tier = Column(String(20), nullable=False)
    new_tier = Column(String(20), nullable=False)
    risk_score = Column(Numeric(5, 2), nullable=False)
    narrative = Column(Text)
    notified_sectors = Column(String(200))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index('idx_alerts_tier', 'new_tier', 'created_at'),
    )
