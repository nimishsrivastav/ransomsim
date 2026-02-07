"""
Scenario Generation Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging

from app.models.schemas.scenario import (
    ScenarioCreate,
    Scenario,
)
from app.models.schemas.common import SuccessResponse, ErrorResponse
from app.services.gemini.scenario_generator import get_scenario_generator
from app.core.exceptions import GeminiAPIError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/generate",
    response_model=Scenario,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a new ransomware scenario",
    description="Creates a realistic ransomware breach scenario based on organization profile",
)
async def generate_scenario(
    scenario_request: ScenarioCreate,
    scenario_generator = Depends(get_scenario_generator),
) -> Scenario:
    """
    Generate a new ransomware scenario
    
    - **organization**: Organization profile (size, industry, data sensitivity)
    - **persona_type**: Threat actor type (professional, opportunist, script_kiddie)
    - **difficulty**: Scenario difficulty level (1-10)
    """
    try:
        logger.info(
            f"Generating scenario: {scenario_request.organization.industry}, "
            f"persona: {scenario_request.persona_type}"
        )
        
        scenario = await scenario_generator.generate_scenario(
            organization=scenario_request.organization,
            persona_type=scenario_request.persona_type,
            difficulty=scenario_request.difficulty,
        )
        
        logger.info(f"Scenario generated: {scenario.id}")
        return scenario
        
    except GeminiAPIError as e:
        logger.error(f"Gemini API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to generate scenario: {e.message}",
        )
    except Exception as e:
        logger.error(f"Unexpected error generating scenario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/{scenario_id}",
    response_model=Scenario,
    summary="Get scenario details",
    description="Retrieve a previously generated scenario by ID",
)
async def get_scenario(
    scenario_id: str,
    scenario_generator = Depends(get_scenario_generator),
) -> Scenario:
    """
    Get scenario by ID
    
    - **scenario_id**: Unique scenario identifier
    """
    try:
        scenario = await scenario_generator.get_scenario(scenario_id)
        
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario {scenario_id} not found",
            )
        
        return scenario
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving scenario {scenario_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )