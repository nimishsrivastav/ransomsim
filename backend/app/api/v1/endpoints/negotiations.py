"""
Negotiation Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Header
from typing import Dict, List, Optional
import logging
import json

from app.models.schemas.negotiation import (
    NegotiationStart,
    NegotiationStartResponse,
    SendMessage,
    SendMessageResponse,
    ConversationHistory,
    Message,
)
from app.services.session.session_manager import get_session_manager
from app.services.gemini.conversation_manager import get_conversation_manager
from app.services.gemini.scenario_generator import get_scenario_generator
from app.core.exceptions import (
    SessionNotFoundError,
    SessionExpiredError,
    InvalidMessageError,
    GeminiAPIError,
)
from app.services.validation.message_validator import get_message_validator

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/start",
    response_model=NegotiationStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new negotiation session",
    description="Initialize a new negotiation with AI threat actor",
)
async def start_negotiation(
    request: NegotiationStart,
    session_manager = Depends(get_session_manager),
    conversation_manager = Depends(get_conversation_manager),
    scenario_generator = Depends(get_scenario_generator),
) -> NegotiationStartResponse:
    """
    Start a new negotiation session
    
    - **scenario_id**: Previously generated scenario ID
    - **persona_type**: Threat actor persona to use
    """
    try:
        logger.info(
            f"Starting negotiation for scenario {request.scenario_id} "
            f"with persona {request.persona_type}"
        )
        
        # Create session
        session = await session_manager.create_session(
            scenario_id=request.scenario_id,
            persona_type=request.persona_type,
        )
        
        # Fetch scenario context for initial message
        scenario = await scenario_generator.get_scenario(request.scenario_id)
        scenario_dict = scenario.model_dump() if scenario else None

        # Generate initial AI message
        initial_message = await conversation_manager.generate_initial_message(
            session_id=session.id,
            persona_type=request.persona_type,
            scenario=scenario_dict,
        )
        
        # Add initial message to session
        await session_manager.add_message(
            session_id=session.id,
            message=initial_message,
        )
        
        logger.info(f"Negotiation started: session {session.id}")

        return NegotiationStartResponse(
            session_id=session.id,
            initial_message=initial_message,
            deadline=session.deadline,
            client_token=session.client_token,
        )
        
    except Exception as e:
        logger.error(f"Error starting negotiation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start negotiation: {str(e)}",
        )


@router.post(
    "/{session_id}/message",
    response_model=SendMessageResponse,
    summary="Send a message in negotiation",
    description="Send user message and receive AI response",
)
async def send_message(
    session_id: str,
    message: SendMessage,
    session_manager = Depends(get_session_manager),
    conversation_manager = Depends(get_conversation_manager),
    scenario_generator = Depends(get_scenario_generator),
    x_client_token: Optional[str] = Header(None, description="Client token for session ownership validation"),
) -> SendMessageResponse:
    """
    Send a message in active negotiation

    - **session_id**: Active session ID
    - **content**: Message content (1-5000 characters)
    - **X-Client-Token**: (Header) Client token returned from /start endpoint
    """
    try:
        # Validate session exists and is active
        session = await session_manager.get_session(session_id)

        if not session:
            raise SessionNotFoundError(session_id)

        # Validate session ownership if token is provided or required
        if session.client_token and not session_manager.validate_session_ownership(session, x_client_token):
            logger.warning(f"Session ownership validation failed for {session_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid client token - you don't have access to this session",
            )
        
        if session.status == "expired":
            raise SessionExpiredError(session_id)
        
        if session.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session already completed",
            )

        # Validate and sanitize user message for prompt injection
        validator = get_message_validator(strict_mode=False)
        validation_result = validator.validate(message.content)

        if not validation_result.is_valid:
            logger.warning(
                f"Message validation failed for session {session_id}: {validation_result.blocked_reason}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_result.blocked_reason or "Invalid message content",
            )

        if validation_result.warnings:
            logger.warning(
                f"Message validation warnings for session {session_id}: {validation_result.warnings}"
            )

        # Use sanitized message
        sanitized_content = validation_result.sanitized_message

        logger.info(f"Processing message for session {session_id}")

        # Add user message to session
        user_message = await session_manager.add_user_message(
            session_id=session_id,
            content=sanitized_content,
        )

        # Get conversation history for AI response
        conversation_history = await session_manager.get_messages(session_id)

        # Get scenario context
        scenario = await scenario_generator.get_scenario(session.scenario_id)
        scenario_dict = scenario.model_dump() if scenario else None

        # Generate AI response with full context (using sanitized message)
        ai_response = await conversation_manager.generate_response(
            session_id=session_id,
            user_message=sanitized_content,
            conversation_history=conversation_history,
            persona_type=session.persona_type,
            scenario=scenario_dict,
        )
        
        # Add AI message to session
        await session_manager.add_message(
            session_id=session_id,
            message=ai_response,
        )
        
        # Update session metadata
        session_meta = await session_manager.update_session_metadata(
            session_id=session_id,
        )
        
        return SendMessageResponse(
            message_id=ai_response.id,
            ai_response=ai_response,
            session_status=session.status,
            pressure_level=session_meta.get("pressure_level", 5),
        )
        
    except (SessionNotFoundError, SessionExpiredError) as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
        )
    except InvalidMessageError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except HTTPException:
        raise
    except GeminiAPIError as e:
        logger.error(f"Gemini API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable. Please try again in a moment.",
        )
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message",
        )


@router.get(
    "/{session_id}/history",
    response_model=ConversationHistory,
    summary="Get conversation history",
    description="Retrieve full conversation history for a session",
)
async def get_conversation_history(
    session_id: str,
    session_manager = Depends(get_session_manager),
) -> ConversationHistory:
    """
    Get conversation history
    
    - **session_id**: Session ID
    """
    try:
        session = await session_manager.get_session(session_id)
        
        if not session:
            raise SessionNotFoundError(session_id)
        
        messages = await session_manager.get_messages(session_id)
        
        return ConversationHistory(
            session_id=session_id,
            messages=messages,
            total_messages=len(messages),
            session_status=session.status,
        )
        
    except SessionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation history",
        )


@router.post(
    "/{session_id}/complete",
    summary="Complete negotiation session",
    description="Mark session as completed",
)
async def complete_negotiation(
    session_id: str,
    session_manager = Depends(get_session_manager),
) -> Dict[str, str]:
    """
    Complete a negotiation session
    
    - **session_id**: Session ID to complete
    """
    try:
        await session_manager.complete_session(session_id)
        
        return {
            "message": "Session completed successfully",
            "session_id": session_id,
        }
        
    except SessionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except Exception as e:
        logger.error(f"Error completing session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete session",
        )


@router.websocket("/{session_id}/ws")
async def websocket_negotiation(
    websocket: WebSocket,
    session_id: str,
    session_manager = Depends(get_session_manager),
    conversation_manager = Depends(get_conversation_manager),
):
    """
    WebSocket endpoint for real-time negotiation
    
    Optional: For more interactive experience
    """
    await websocket.accept()
    
    try:
        # Verify session exists
        session = await session_manager.get_session(session_id)
        if not session:
            await websocket.send_json({
                "error": "Session not found",
                "session_id": session_id,
            })
            await websocket.close()
            return
        
        # Send initial session state
        await websocket.send_json({
            "type": "session_info",
            "session_id": session_id,
            "status": session.status,
            "deadline": session.deadline.isoformat(),
        })
        
        # Message loop
        validator = get_message_validator(strict_mode=False)

        while True:
            # Receive user message
            data = await websocket.receive_text()

            # Validate JSON parsing
            try:
                message_data = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "error": "Invalid JSON format",
                })
                continue

            if message_data.get("type") == "message":
                user_content = message_data.get("content", "")

                # Validate message content
                validation_result = validator.validate(user_content)
                if not validation_result.is_valid:
                    await websocket.send_json({
                        "type": "error",
                        "error": validation_result.blocked_reason or "Invalid message",
                    })
                    continue

                # Use sanitized content
                sanitized_content = validation_result.sanitized_message

                # Add user message
                user_msg = await session_manager.add_user_message(
                    session_id=session_id,
                    content=sanitized_content,
                )
                
                # Send user message confirmation
                await websocket.send_json({
                    "type": "user_message",
                    "message": user_msg.dict(),
                })
                
                # Generate AI response (using sanitized content)
                ai_response = await conversation_manager.generate_response(
                    session_id=session_id,
                    user_message=sanitized_content,
                )
                
                # Add AI message
                await session_manager.add_message(
                    session_id=session_id,
                    message=ai_response,
                )
                
                # Send AI response
                await websocket.send_json({
                    "type": "ai_message",
                    "message": ai_response.dict(),
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({
            "error": "Internal server error",
            "message": str(e),
        })
        await websocket.close()