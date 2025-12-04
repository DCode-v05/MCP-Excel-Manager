# backend/core/ui_chat.py
from typing import Dict, List, Any, Tuple

from backend.core.chat import Chat
from backend.mcp.mcp_client import MCPExcelClient
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class UIChat(Chat):
    """
    High-level user chat layer.

    Extra UX features:
    - @file.xlsx mentions
    - contextual document injection
    - prompt formatting
    """

    def __init__(
        self,
        gemini_service,
        mcp_clients: Dict[str, MCPExcelClient],
    ):
        super().__init__(gemini_service, mcp_clients)
        self.excel_client: MCPExcelClient = mcp_clients.get("excel")

    # ----------------------------------------------------
    # Extract context via @mentions
    # ----------------------------------------------------
    async def _extract_resources(self, query: str) -> str:
        """
        If user types: "Compare @accounts.xlsx with @opportunities.xlsx"
        We detect file names and load their content.
        """

        if not self.excel_client:
            return ""

        mentioned = [
            word[1:]
            for word in query.split()
            if word.startswith("@")
        ]

        if not mentioned:
            return ""

        found = []
        file_list = await self.excel_client.list_excel_files()

        for file in file_list:
            if file in mentioned:
                sheet_data = await self.excel_client.read_sheet(file)
                found.append((file, sheet_data))

        # Format for LLM-friendly context
        blocks = []
        for file, data in found:
            blocks.append(
                f'<excel file="{file}">\n{data}\n</excel>'
            )
        return "\n".join(blocks)

    # ----------------------------------------------------
    # Override: preprocessing user messages
    # ----------------------------------------------------
    async def _process_user_query(self, query: str):
        """
        Inject contextual sheet data automatically,
        then treat the whole thing as a single user prompt.
        """
        context = await self._extract_resources(query)

        prompt = f"""
You are a Salesforce CRM and Excel analysis assistant.

User query:
<user>{query}</user>

If useful, use the MCP tools to fetch or edit Excel data.
Only use tools when necessary.

Context (if provided):
<context>
{context}
</context>

Rules:
- NEVER mention having a context field.
- Answer clearly and professionally.
- Do not hallucinate missing sheet names.
"""

        self.messages.append({"role": "user", "content": prompt})
