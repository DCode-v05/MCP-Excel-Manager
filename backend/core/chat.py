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
        final_text_response = ""

        await self._process_user_query(query)

        while True:
            # 1) Collect all available tools (from MCP servers)
            tools_schema = await ToolManager.get_all_tools_schema(self.mcp_clients)
            
            # 2) Call Gemini with history + tool schemas
            response = await self.gemini_service.chat(
                messages=self.messages,
                tools_schema=tools_schema,
            )
            
            # 3) Inspect Gemini response for tool calls
            tool_calls = ToolManager.extract_tool_calls(response)

            # -------- 1️⃣ NO tool calls → Model is done
            if not tool_calls:
                reply = self.gemini_service.extract_text(response)
                self.messages.append({"role": "model", "content": reply})
                return reply

            logger.info(f"Gemini requested tools: {tool_calls}")

            # 4) Execute tools with MCP clients
            tool_results = await ToolManager.execute_tool_calls(
                self.mcp_clients,
                tool_calls,
            )
            # 5) Add tool results into history as if "function" role
            for result in tool_results:
                self.messages.append({
                    "role": "user",
                    "content": json.dumps(result["content"])
                })
            # 6) Ask Gemini to continue, now with tool results
            response = await self.gemini_service.resume_with_tool_results(
                messages=self.messages,
                tool_response=tool_results,
                tools_schema=tools_schema,
            )

            # Check if Gemini again wants tools
            second_round_tool_calls = ToolManager.extract_tool_calls(response)

            if not second_round_tool_calls:
                final_text_response = self.gemini_service.extract_text(response)
                self.messages.append(
                    {"role": "model", "content": final_text_response}
                )
                break

            # Otherwise, loop again with more tools
            logger.info(f"Gemini requested additional tools: {second_round_tool_calls}")
            # prepare history to include that intermediate assistant response, too
            self.messages.append(
                {
                    "role": "model",
                    "content": self.gemini_service.extract_text(response),
                }
            )
            # by overwriting tool_calls
            tool_calls = second_round_tool_calls

        return final_text_response
