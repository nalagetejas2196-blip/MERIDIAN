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

# Serve compiled React frontend from backend/static
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        file_path = os.path.join(static_dir, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(static_dir, "index.html"))

