from app.core.celery_app import celery_app
from app.db.session import async_sessionmaker, engine, AsyncSessionLocal
from sqlalchemy import text
import asyncio
from datetime import datetime, timedelta

async def async_apply_temporal_decay():
    async with AsyncSessionLocal() as session:
        stale_threshold = datetime.utcnow() - timedelta(hours=6)
        
        await session.execute(
            text("""
            UPDATE hex_risk_scores
            SET risk_score = risk_score * 0.80,
                risk_tier = CASE
                    WHEN risk_score * 0.80 <= 2.5 THEN 'LOW'
                    WHEN risk_score * 0.80 <= 5.0 THEN 'MODERATE'
                    WHEN risk_score * 0.80 <= 7.5 THEN 'HIGH'
                    ELSE 'CRITICAL'
                END
            WHERE last_signal_at < :stale_threshold
              AND risk_score > 0.5
            """),
            {"stale_threshold": stale_threshold}
        )
        await session.commit()

@celery_app.task
def apply_temporal_decay():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_apply_temporal_decay())
