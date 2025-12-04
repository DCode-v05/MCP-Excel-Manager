# backend/core/chat.py
from typing import Dict, List, Any
import json

from backend.services.gemini_service import GeminiService
from backend.mcp.mcp_client import MCPExcelClient  # and/or other MCP clients later
from backend.mcp.tool_manager import ToolManager   # will be implemented next
from backend.utils.logger import get_logger


logger = get_logger(__name__)


class Chat:
    """
    Core chat orchestrator.

    Responsibilities:
    - Maintain message history
    - Call Gemini with tool schemas
    - Detect when Gemini wants to use tools
    - Call ToolManager to execute MCP tools
    - Feed tool results back to Gemini
    """

    def __init__(
        self,
        gemini_service: GeminiService,
        mcp_clients: Dict[str, MCPExcelClient],
    ):
        self.gemini_service = gemini_service
        self.mcp_clients = mcp_clients  # e.g. {"excel": MCPExcelClient(...)}
        self.messages: List[Dict[str, Any]] = []

    # ---------------------------------------
    # Internal helpers
    # ---------------------------------------

    async def _process_user_query(self, query: str):
        """
        Add user query into history. Higher layers (UI/HTTP)
        call .run(query) which uses this.
        """
        self.messages.append({"role": "user", "content": query})

    # ---------------------------------------
    # Main public entry point
    # ---------------------------------------

    async def run(self, query: str) -> str:
        """
        Main chat loop:
        1. Add user message
        2. Ask Gemini with available tools
        3. If Gemini wants tools -> execute via ToolManager
        4. Resume chat with tool results
        5. Repeat until final text reply
        """
        await self._process_user_query(query)

        while True:
            # 1) Collect all available tools
            tools_schema = await ToolManager.get_all_tools_schema(self.mcp_clients)
            
            # 2) Call Gemini with history + tool schemas
            response = await self.gemini_service.chat(
                messages=self.messages,
                tools_schema=tools_schema,
            )
            
            # 3) Inspect Gemini response for tool calls
            tool_calls = ToolManager.extract_tool_calls(response)

            # If NO tool calls → Model is done, extract final text
            if not tool_calls:
                reply = self.gemini_service.extract_text(response)
                if reply:  # Only add if there's actual text
                    self.messages.append({"role": "model", "content": reply})
                return reply if reply else "Task completed successfully."

            logger.info(f"Gemini requested tools: {tool_calls}")

            # 4) Execute tools with MCP clients
            tool_results = await ToolManager.execute_tool_calls(
                self.mcp_clients,
                tool_calls,
            )
            
            # 5) Resume with tool results
            response = await self.gemini_service.resume_with_tool_results(
                messages=self.messages,
                tool_response=tool_results,
                tools_schema=tools_schema,
            )
            
            # 6) Extract text if any and add to history
            reply = self.gemini_service.extract_text(response)
            if reply:
                self.messages.append({"role": "model", "content": reply})
                
            # Note: We don't return here even if there's text,
            # because there might be more tool calls in the response.
            # The loop will check at the top and handle accordingly.