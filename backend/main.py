# backend/main.py
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.core.ui_chat import UIChat
from backend.services.gemini_service import GeminiService
from backend.utils.logger import get_logger

from backend.mcp.mcp_client import MCPExcelClient
from backend.api.routes import router

logger = get_logger(__name__)
settings = get_settings()

# global singletons
excel_mcp_client = MCPExcelClient()
gemini = GeminiService()
chat_agent = UIChat(gemini_service=gemini, mcp_clients={"excel": excel_mcp_client})


def create_app() -> FastAPI:
    """
    Creates FastAPI app and attaches:
    - CORS
    - routers
    - lifecycle events
    """
    app = FastAPI(
        title="Salesforce MCP API",
        version="1.0",
        description="CRM + Excel AI Assistant using Gemini + MCP"
    )

    # ---------------------------
    # CORS for React frontend
    # ---------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---------------------------
    # REST routes
    # ---------------------------
    app.include_router(router, prefix=settings.API_PREFIX)

    # ---------------------------
    # Lifecycle events
    # ---------------------------

    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting application...")
        app.state.chat_agent = chat_agent
        await _connect_mcp()

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down application...")
        await _close_mcp()

    return app


async def _connect_mcp():
    """
    Spawns MCP Excel server over stdio.
    """
    try:
        logger.info("Connecting MCP Excel server...")
        await excel_mcp_client.connect()
        logger.info("Excel MCP connected")
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")


async def _close_mcp():
    """
    Graceful shutdown.
    """
    try:
        await excel_mcp_client.close()
        logger.info("MCP Excel client closed")
    except Exception as e:
        logger.error(f"Error closing MCP Excel: {e}")


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
