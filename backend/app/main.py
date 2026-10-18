import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.api.endpoints import router as api_router
from app.services.seed_service import seed_database_data

# Initialize DB tables
Base.metadata.create_all(bind=engine)

# Seed initial synthetic records
db = SessionLocal()
try:
    seed_database_data(db)
finally:
    db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=f"{settings.PROJECT_NAME} — {settings.PROJECT_TAGLINE}. Competition-grade AI Lab project with zero mandatory cost.",
    version=settings.PROJECT_VERSION,
    docs_url=f"{settings.API_V1_STR}/docs",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["System Health"])
def health_check():
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "tagline": settings.PROJECT_TAGLINE,
        "database": "sqlite_connected",
        "ollama_target_model": settings.OLLAMA_MODEL,
        "cost_policy": "Zero mandatory cost (Local offline inference)"
    }
