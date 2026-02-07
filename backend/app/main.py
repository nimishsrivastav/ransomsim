"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import logging

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import CustomException
from app.api.v1.router import api_router
from app.api.middleware.error_handler import ErrorHandlerMiddleware
from app.api.middleware.rate_limiter import RateLimiterMiddleware
from app.api.middleware.security_headers import SecurityHeadersMiddleware

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# API Tags metadata
tags_metadata = [
    {
        "name": "Health",
        "description": "Health check and status endpoints",
    },
    {
        "name": "Scenarios",
        "description": "Generate and manage ransomware breach scenarios. Scenarios define the context for negotiations including organization profile, systems affected, and ransom demands.",
    },
    {
        "name": "Negotiations",
        "description": "Manage negotiation sessions with AI threat actors. Send messages, receive responses, and track conversation history.",
    },
    {
        "name": "Analysis",
        "description": "Get AI-powered analysis of completed negotiations. Includes performance scoring, tactical insights, and recommendations.",
    },
]

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## RansomSim: AI‑Driven Ransomware Negotiation Training API

An AI-powered training platform for practicing ransomware negotiation scenarios.

### Features
- **Scenario Generation**: Create realistic breach scenarios tailored to different industries and organization sizes
- **AI Threat Actors**: Negotiate with AI personas that adapt to your tactics (Professional, Opportunist, Script Kiddie)
- **Real-time Chat**: Send messages and receive contextual responses from the AI threat actor
- **Performance Analysis**: Get detailed feedback on your negotiation performance

### Getting Started
1. Generate a scenario using `POST /api/v1/scenarios/generate`
2. Start a negotiation with `POST /api/v1/negotiations/start`
3. Send messages with `POST /api/v1/negotiations/{session_id}/message`
4. End and analyze with `POST /api/v1/negotiations/{session_id}/complete` then `POST /api/v1/analysis/{session_id}/generate`

### Important Notice
This is a **training simulation only**. Not for real incident response.
    """,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    openapi_tags=tags_metadata,
    contact={
        "name": "RansomSim: AI‑Driven Ransomware Negotiation Training",
        "url": "https://github.com/your-repo/ransomware-negotiator-simulator",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# CORS Middleware - restrict methods and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Only methods we actually use
    allow_headers=["Content-Type", "Authorization", "X-Request-ID", "X-Client-Token"],  # Only headers we need
    expose_headers=["X-Request-ID"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Custom Middleware (order matters - first added = last executed)
app.add_middleware(SecurityHeadersMiddleware)  # Add security headers to all responses
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RateLimiterMiddleware)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Storage type: {settings.STORAGE_TYPE}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")


@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    """Handle custom exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_type,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint - returns minimal info to avoid information disclosure"""
    return {
        "status": "healthy",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )