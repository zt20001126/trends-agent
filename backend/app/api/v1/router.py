from fastapi import APIRouter

from app.api.v1.routes.frontend import router as frontend_router
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.selection import router as selection_router

api_router = APIRouter()
api_router.include_router(frontend_router, tags=["frontend"])
api_router.include_router(health_router, tags=["health"])
api_router.include_router(selection_router, tags=["selection"])
