from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import auth, ingest, map, alerts, public
from app.db.session import engine, Base

app = FastAPI(title=settings.PROJECT_NAME)

# CORS Middleware (allow all for hackathon)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(map.router, prefix="/map", tags=["map"])
app.include_router(alerts.router, prefix="/department/alerts", tags=["alerts"])
app.include_router(public.router, prefix="/public", tags=["public"])

@app.on_event("startup")
async def startup():
    from app.db.session import engine, Base
    import app.models.user
    import app.models.signal_vector
    import app.models.hex_risk
    import app.models.alert
    import app.models.area_cache
    
    # Create all tables (SQLite - no extensions needed)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Auto-seed demo user
    from app.db.session import AsyncSessionLocal
    from sqlalchemy.future import select
    from app.models.user import User
    from app.core.security import get_password_hash
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == "officer@police.gov"))
        if not result.scalars().first():
            import uuid
            user = User(
                id=str(uuid.uuid4()),
                email="officer@police.gov",
                password_hash=get_password_hash("securepassword123"),
                sector="police",
                role="department_user"
            )
            session.add(user)
            await session.commit()
            print("[OK] Demo user seeded: officer@police.gov / securepassword123")
        else:
            print("[OK] Demo user already exists")

@app.get("/")
def root():
    return {"message": "SafeGrid API is running"}
