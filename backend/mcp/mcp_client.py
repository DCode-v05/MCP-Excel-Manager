# backend/mcp/mcp_client.py
import json
import sys
import asyncio
from typing import Any, Optional, Dict, List
from contextlib import AsyncExitStack

from pydantic import AnyUrl
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters, types

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class MCPExcelClient:
    """
    Wrapper for interacting with the Excel MCP server.

    Responsibilities:
    🔹 Start MCP server via stdio
    🔹 Call tools (read_sheet, append_row, etc)
    🔹 Read structured results
    🔹 Handle cleanup safely
    """

    def __init__(
        self,
        command: str = "python",
        args: list[str] = ["backend/mcp/excel_mcp_server.py"],
        env: Optional[dict] = None,
    ):
        self._command = command
        self._args = args
        self._env = env

        self._session: Optional[ClientSession] = None
        self._exit_stack = AsyncExitStack()

    # ------------------------------
    # Init + Connect
    # ------------------------------
    async def connect(self):
        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )

        logger.info("Starting Excel MCP server...")
        _stdio, _write = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(_stdio, _write)
        )
        await self._session.initialize()
        print("Initializing MCP session...")

        logger.info("Excel MCP connected")

    def session(self) -> ClientSession:
        if not self._session:
            raise RuntimeError("MCP session not initialized")
        return self._session

    # ------------------------------
    # TOOL WRAPPERS
    # ------------------------------

    async def list_tools(self):
        result = await self.session().list_tools()
        return result.tools

    async def call_tool(self, name: str, input_data: dict):
        result = await self.session().call_tool(name, input_data)
        return result

    # ------------------------------
    # EXCEL-SPECIFIC HELPERS
    # ------------------------------

    async def list_excel_files(self) -> List[str]:
        res = await self.call_tool("list_excel_files", {})
        return [c.text for c in res.content if isinstance(c, types.TextContent)]

    async def read_sheet(self, file_name: str, sheet: Optional[str] = None) -> list[dict]:
        payload = {"file_name": file_name}
        if sheet:
            payload["sheet_name"] = sheet

        res = await self.call_tool("read_sheet", payload)
        return json.loads(res.content[0].text)

    async def read_range(
        self,
        file: str,
        sheet: str,
        start: int,
        end: int,
    ) -> list[dict]:
        payload = {
            "file_name": file,
            "sheet_name": sheet,
            "start_row": start,
            "end_row": end,
        }

        res = await self.call_tool("read_range", payload)
        return json.loads(res.content[0].text)

    async def write_cell(self, file, sheet, row, col, value):
        input_data = {
            "file_name": file,
            "sheet_name": sheet,
            "row": row,
            "col": col,
            "value": value,
        }

        res = await self.call_tool("write_cell", input_data)
        return res.content[0].text

    async def append_row(self, file, sheet, row_data):
        input_data = {
            "file_name": file,
            "sheet_name": sheet,
            "row_data": row_data,
        }
        res = await self.call_tool("append_row", input_data)
        return res.content[0].text

    # ------------------------------
    # Resource Reading (rare)
    # ------------------------------

    async def read_resource(self, uri: str) -> Any:
        result = await self.session().read_resource(AnyUrl(uri))
        resource = result.contents[0]
        if isinstance(resource, types.TextResourceContents):
            return json.loads(resource.text)
        return resource.text

    # ------------------------------
    # Cleanup
    # ------------------------------

    async def close(self):
        logger.info("Closing MCP session...")
        await self._exit_stack.aclose()
        self._session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.close()


# Quick test
async def test():
    async with MCPExcelClient() as c:
        files = await c.list_excel_files()
        print("Files:", files)

        data = await c.read_sheet(files[0])
        print("Sheet sample:", data[:3])


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(test())
