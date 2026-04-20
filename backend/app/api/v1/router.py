from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, meals, integrations, dashboard, stats, water, weekly

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(meals.router)
api_router.include_router(integrations.router)
api_router.include_router(dashboard.router)
api_router.include_router(stats.router)
api_router.include_router(water.router)
api_router.include_router(weekly.router)

__all__ = ["api_router"]
