"""
Health Check Endpoints
"""
from fastapi import APIRouter, Depends
from app.core.config import settings
from app.services.gemini.client import get_gemini_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get("/detailed")
async def detailed_health_check(
    gemini_service = Depends(get_gemini_service)
):
    """Detailed health check with service status"""
    gemini_healthy = False
    
    try:
        # Test Gemini connection
        await gemini_service.test_connection()
        gemini_healthy = True
    except Exception as e:
        logger.error(f"Gemini health check failed: {e}")
    
    return {
        "status": "healthy" if gemini_healthy else "degraded",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "checks": {
            "gemini_api": "healthy" if gemini_healthy else "unhealthy",
            "storage": "healthy",  # Add actual storage check
        },
    }