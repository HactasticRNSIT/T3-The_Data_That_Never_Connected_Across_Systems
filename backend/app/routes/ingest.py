from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.ingest_schema import IngestBatch, IngestResponse
from app.schemas.auth_schema import UserResponse
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.signal_vector import SignalVector
from app.services.h3_engine import bin_to_hex
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
                batch_id=batch.batch_id
            )
        )
        
    if vectors_to_insert:
        db.add_all(vectors_to_insert)
        await db.commit()
        
    # Queue Celery task for computing risk
    from app.core.celery_app import celery_app
    task = celery_app.send_task("recompute_hex_risk", args=[list(hex_ids)])
    
    return IngestResponse(
        status="accepted",
        batch_id=batch.batch_id,
        vectors_received=len(vectors_to_insert),
        task_id=task.id,
        message="Batch queued for processing"
    )
