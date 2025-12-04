# backend/utils/error_handlers.py
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from backend.utils.logger import get_logger

logger = get_logger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Triggered when FastAPI cannot parse incoming request body.
    Example: missing "message" in ChatRequest.
    """
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Invalid request",
            "details": exc.errors(),
        },
    )


async def pydantic_exception_handler(request: Request, exc: ValidationError):
    """
    Schema validation errors raised internally.
    """
    logger.warning(f"Pydantic model error: {exc.errors()}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal validation error",
            "details": exc.errors(),
        },
    )


async def global_exception_handler(request: Request, exc: Exception):
    """
    Fallback for everything else:
    - MCP exceptions
    - Salesforce 5xx
    - Unexpected Python runtime failures
    """
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Unexpected server error",
            "details": "Please try again later."
        },
    )
