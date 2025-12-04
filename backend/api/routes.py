# backend/api/routes.py
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi import status

from backend.config import get_settings
from backend.utils.logger import get_logger


from backend.api.models import (
    AuthUrlResponse,
    AuthCallbackResponse,
    ChatRequest,
    ChatResponse,
)

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter()

# ----------------------------------------------------
# Service singletons (wired in main.py startup)
# ----------------------------------------------------

# In a more advanced setup you'd inject these via dependencies or app.state,
# but for this project-level structure, simple singletons are ok.

# ----------------------------------------------------
# Health check
# ----------------------------------------------------
@router.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}


# ----------------------------------------------------
# Chat Endpoint (Gemini + MCP + Salesforce context)
# ----------------------------------------------------
@router.post(
    "/chat",
    response_model=ChatResponse,
    tags=["chat"],
)
async def chat_endpoint(request: Request, payload: ChatRequest):
    """
    Main chat API:
    - Accepts user message string
    - Uses Gemini + MCP + Salesforce where needed
    - Returns final text answer
    """
    user_message = payload.message.strip()
    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )
    chat_agent = request.app.state.chat_agent
    reply = await chat_agent.run(user_message)
    return ChatResponse(reply=reply)
