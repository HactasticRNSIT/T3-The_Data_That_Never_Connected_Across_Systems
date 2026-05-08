import os

class Settings:
    PROJECT_NAME: str = "SafeGrid API"
    SECRET_KEY: str = os.getenv("JWT_SECRET", "super-secret-jwt-key-for-hackathon")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 1 day for hackathon
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://safegrid:safegrid@localhost:5432/safegrid_db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

settings = Settings()
