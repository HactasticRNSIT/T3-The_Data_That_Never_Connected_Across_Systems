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
    # In a real app we'd use Alembic. For demo, we can optionally create tables here if they don't exist.
    # Note: Creating tables via metadata.create_all() does not easily handle TimescaleDB hypertables 
    # or PostGIS geometry columns automatically without specific setup.
    # We rely on docker/alembic setup for true schemas.
    pass

@app.get("/")
def root():
    return {"message": "SafeGrid API is running"}
