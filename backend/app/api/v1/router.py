from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, meals, integrations, dashboard

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(meals.router)
api_router.include_router(integrations.router)
api_router.include_router(dashboard.router)

__all__ = ["api_router"]
