from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.security import get_current_user
from app.schemas.auth_schema import UserResponse
from app.db.session import get_db
from app.models.alert import DepartmentAlert
from app.services.rbac_service import get_allowed_sectors_for_user

router = APIRouter()

@router.get("/")
async def get_alerts(
    limit: int = 20,
    tier: str = None,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    allowed_sectors = get_allowed_sectors_for_user(current_user.sector, current_user.role)
    
    query = select(DepartmentAlert)
    
    if current_user.role != 'admin':
        # Simple filter for demo: if triggered_by is in allowed_sectors
        query = query.where(DepartmentAlert.triggered_by.in_(allowed_sectors))
        
    if tier:
        query = query.where(DepartmentAlert.new_tier == tier)
        
    query = query.order_by(DepartmentAlert.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    return {
        "alerts": alerts,
        "total": len(alerts)
    }
