from fastapi import APIRouter, Response, status
from sqlalchemy import text
from datetime import datetime, timezone
from app.db.session import engine

router = APIRouter()


@router.get("/health", summary="Verify system health and PostgreSQL connectivity")
def check_health(response: Response):
    """
    Health check endpoint that verifies API service status and PostgreSQL connectivity.
    Strictly uses PostgreSQL with no fallbacks.
    """
    current_time = datetime.now(timezone.utc).isoformat()
    db_status = "disconnected"
    db_error = None

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()
            if result == 1:
                db_status = "connected"
    except Exception as exc:
        db_status = "disconnected"
        db_error = str(exc)
        # Set HTTP 503 Service Unavailable when DB connection fails
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    health_response = {
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": current_time,
        "database": {
            "type": "PostgreSQL",
            "status": db_status,
            "error": db_error
        },
        "version": "1.0.0"
    }

    return health_response
