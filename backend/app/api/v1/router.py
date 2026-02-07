"""
Main API Router - Aggregates all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import scenarios, negotiations, analysis, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"],
)

api_router.include_router(
    scenarios.router,
    prefix="/scenarios",
    tags=["Scenarios"],
)

api_router.include_router(
    negotiations.router,
    prefix="/negotiations",
    tags=["Negotiations"],
)

api_router.include_router(
    analysis.router,
    prefix="/analysis",
    tags=["Analysis"],
)