"""
Analysis Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from app.models.schemas.analysis import Analysis
from app.services.gemini.analysis_engine import get_analysis_engine
from app.services.session.session_manager import get_session_manager
from app.core.exceptions import SessionNotFoundError, GeminiAPIError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/{session_id}",
    response_model=Analysis,
    status_code=status.HTTP_200_OK,
    summary="Generate negotiation analysis",
    description="Analyze completed negotiation and provide feedback",
)
async def generate_analysis(
    session_id: str,
    session_manager = Depends(get_session_manager),
    analysis_engine = Depends(get_analysis_engine),
) -> Analysis:
    """
    Generate comprehensive negotiation analysis
    
    - **session_id**: Completed session ID to analyze
    """
    try:
        logger.info(f"Generating analysis for session {session_id}")
        
        # Get session
        session = await session_manager.get_session(session_id)
        
        if not session:
            raise SessionNotFoundError(session_id)
        
        # Check if session is completed
        if session.status == "active":
            # Auto-complete session for analysis
            await session_manager.complete_session(session_id)
        
        # Get full conversation history
        messages = await session_manager.get_messages(session_id)
        
        # Generate analysis
        analysis = await analysis_engine.analyze_negotiation(
            session_id=session_id,
            messages=messages,
            session_metadata=session.metadata,
        )
        
        logger.info(f"Analysis generated for session {session_id}")
        
        return analysis
        
    except SessionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except GeminiAPIError as e:
        logger.error(f"Gemini API error during analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to generate analysis",
        )
    except Exception as e:
        logger.error(f"Error generating analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/{session_id}",
    response_model=Analysis,
    summary="Get existing analysis",
    description="Retrieve previously generated analysis",
)
async def get_analysis(
    session_id: str,
    analysis_engine = Depends(get_analysis_engine),
) -> Analysis:
    """
    Get existing analysis
    
    - **session_id**: Session ID
    """
    try:
        analysis = await analysis_engine.get_analysis(session_id)
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis not found for session {session_id}",
            )
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analysis",
        )