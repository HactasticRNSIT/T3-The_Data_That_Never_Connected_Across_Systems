# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.auth_schema import UserLogin, Token, UserResponse
from app.models.user import User
from app.db.session import get_db
from app.core.security import verify_password, create_access_token, get_password_hash

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalars().first()
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        sector=user.sector,
        role=user.role
    )
    
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "sector": user.sector, "role": user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 3600,
        "user": user_response
    }

# For demo setup, an endpoint to seed users
@router.post("/seed", status_code=status.HTTP_201_CREATED)
async def seed_users(db: AsyncSession = Depends(get_db)):
    # Create default user if not exists
    result = await db.execute(select(User).where(User.email == "officer@police.gov"))
    if not result.scalars().first():
        user = User(
            email="officer@police.gov",
            password_hash=get_password_hash("securepassword123"),
            sector="police",
            role="department_user"
        )
        db.add(user)
        await db.commit()
    return {"message": "Users seeded"}
