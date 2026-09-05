from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    auth,
    users,
    profile,
    assessments,
    study_plans,
    progress,
    adaptive,
    placement,
    coach,
    achievements,
)


api_router = APIRouter()


api_router.include_router(
    health.router,
    tags=["Health"],
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth"],
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)

api_router.include_router(
    profile.router,
    prefix="/profile",
    tags=["Profile"],
)

api_router.include_router(
    assessments.router,
    prefix="/assessments",
    tags=["Assessments"],
)

api_router.include_router(
    study_plans.router,
    prefix="/study-plans",
    tags=["Study Plans"],
)

api_router.include_router(
    progress.router,
    prefix="/progress",
    tags=["Progress"],
)

api_router.include_router(
    adaptive.router,
    prefix="/adaptive",
    tags=["Adaptive Intelligence"],
)

api_router.include_router(
    placement.router,
    prefix="/placement",
    tags=["Placement Alignment"],
)

api_router.include_router(
    coach.router,
    prefix="/coach",
    tags=["AI Study Coach"],
)

api_router.include_router(
    achievements.router,
    prefix="/achievements",
    tags=["Achievements"],
)
