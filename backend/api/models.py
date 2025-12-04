# backend/api/models.py
from typing import List, Dict, Optional
from pydantic import BaseModel


# -------------------------------------------
# AUTH
# -------------------------------------------

class AuthUrlResponse(BaseModel):
    auth_url: str


class AuthCallbackResponse(BaseModel):
    """
    Returned after successful Salesforce OAuth callback.
    Token persistence happens in TokenManager, not in this response.
    """
    success: bool
    instance_url: Optional[str] = None

# -------------------------------------------
# CHAT
# -------------------------------------------

class ChatRequest(BaseModel):
    """
    Input payload for /chat endpoint.
    """
    message: str


class ChatResponse(BaseModel):
    """
    Output payload.
    """
    reply: str
