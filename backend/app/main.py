from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.db.session import engine, Base, SessionLocal
from app.db.seed_questions import seed_questions_if_empty
import app.models  # Ensures all models are registered for table creation

# Auto-create tables & seed question bank on startup
try:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_questions_if_empty(db)
    finally:
        db.close()
except Exception as e:
    print(f"Warning on startup initialization: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="SkillForge AI - Adaptive Placement Preparation Platform Backend"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to SkillForge AI API",
        "health_check": f"{settings.API_V1_STR}/health",
        "docs": "/docs"
    }
