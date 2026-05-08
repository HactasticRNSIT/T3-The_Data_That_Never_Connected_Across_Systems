from sqlalchemy import Column, BigInteger, String, Numeric, SmallInteger, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.session import Base

class SignalVector(Base):
    __tablename__ = "signal_vectors"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    hex_id = Column(String(20), nullable=False)
    sector = Column(String(50), nullable=False, index=True)
    signal_type = Column(String(100), nullable=False)
    severity = Column(Numeric(4, 3), nullable=False)
    lat = Column(Numeric(10, 6), nullable=False)
    lon = Column(Numeric(10, 6), nullable=False)
    hour_of_day = Column(SmallInteger, nullable=False)
    day_of_week = Column(SmallInteger, nullable=False)
    batch_id = Column(UUID(as_uuid=True), nullable=False)
    received_at = Column(DateTime(timezone=True), primary_key=True, server_default=func.now())

    __table_args__ = (
        Index('idx_signal_hex_time', 'hex_id', 'received_at', postgresql_ops={'received_at': 'DESC'}),
    )
