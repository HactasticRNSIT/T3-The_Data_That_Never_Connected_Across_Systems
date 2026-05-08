from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.ingest_schema import IngestBatch, IngestResponse
from app.schemas.auth_schema import UserResponse
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.signal_vector import SignalVector
from app.models.hex_risk import HexRiskScore
from app.services.h3_engine import bin_to_hex, compute_risk_score, classify_tier
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/{sector}", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_signals(
    sector: str,
    batch: IngestBatch,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.sector != sector and current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Token sector '{current_user.sector}' cannot submit to sector '{sector}'"
        )
        
    hex_ids = set()
    vectors_to_insert = []
    
    for vector in batch.vectors:
        hex_id = bin_to_hex(vector.lat, vector.lon)
        hex_ids.add(hex_id)
        
        vectors_to_insert.append(
            SignalVector(
                hex_id=hex_id,
                sector=sector,
                signal_type=vector.signal_type,
                severity=vector.severity,
                lat=vector.lat,
                lon=vector.lon,
                hour_of_day=vector.hour_of_day,
                day_of_week=vector.day_of_week,
                batch_id=str(batch.batch_id)
            )
        )
        
    if vectors_to_insert:
        db.add_all(vectors_to_insert)
        await db.commit()
    
    # Process risk scores inline (no Celery needed)
    for hex_id in hex_ids:
        result = await db.execute(
            select(SignalVector).where(SignalVector.hex_id == hex_id)
        )
        signals = result.scalars().all()
        signal_dicts = [
            {"severity": float(s.severity), "sector": s.sector, "received_at": s.received_at or datetime.utcnow()}
            for s in signals
        ]
        
        risk_score = compute_risk_score(signal_dicts)
        risk_tier = classify_tier(risk_score)
        
        # Upsert hex risk score
        existing = await db.execute(
            select(HexRiskScore).where(HexRiskScore.hex_id == hex_id)
        )
        hex_risk = existing.scalars().first()
        
        if hex_risk:
            hex_risk.risk_score = risk_score
            hex_risk.risk_tier = risk_tier
            hex_risk.signal_count = len(signals)
            hex_risk.top_sector = sector
            hex_risk.top_signal_type = signals[0].signal_type if signals else None
            hex_risk.computed_at = datetime.utcnow()
            hex_risk.last_signal_at = datetime.utcnow()
        else:
            import h3 as h3lib
            lat, lon = h3lib.cell_to_latlng(hex_id)
            new_hex = HexRiskScore(
                hex_id=hex_id,
                center_lat=lat,
                center_lon=lon,
                risk_score=risk_score,
                risk_tier=risk_tier,
                signal_count=len(signals),
                top_sector=sector,
                top_signal_type=signals[0].signal_type if signals else None,
                last_signal_at=datetime.utcnow()
            )
            db.add(new_hex)
        
        await db.commit()
    
    return IngestResponse(
        status="accepted",
        batch_id=batch.batch_id,
        vectors_received=len(vectors_to_insert),
        task_id=str(uuid.uuid4()),
        message="Batch processed inline (no Celery)"
    )
