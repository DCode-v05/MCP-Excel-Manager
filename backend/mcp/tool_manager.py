# backend/mcp/tool_manager.py
from typing import Dict, List, Any
from mcp.types import Tool
from backend.utils.logger import get_logger


logger = get_logger(__name__)


class ToolManager:
    """
    Converts MCP tools to Gemini-compatible schemas,
    detects Gemini tool calls, and executes them.
    """

    # ----------------------------------------
    # 1) DISCOVER TOOLS
    # ----------------------------------------

    @staticmethod
    def _clean_schema(schema):
        if not isinstance(schema, dict):
            return schema

        cleaned = {}
        for k, v in schema.items():
            # REMOVE INVALID FIELDS
            if k in ("title", "$schema", "description", "default", "anyOf", "additionalProperties"):
                continue

            if isinstance(v, dict):
                cleaned[k] = ToolManager._clean_schema(v)
            elif isinstance(v, list):
                cleaned[k] = [ToolManager._clean_schema(x) for x in v]
            else:
                cleaned[k] = v

        return cleaned

    @classmethod
    async def get_all_tools_schema(
        cls,
        clients: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Collect tool metadata from all MCP clients and translate
        to Gemini tool schema format.
        """
        schemas = []

        for name, client in clients.items():
            try:
                tools: List[Tool] = await client.list_tools()
            except Exception as e:
                logger.error(f"Failed to list tools from {name}: {e}")
                continue

            for t in tools:
                cleaned = cls._clean_schema(t.inputSchema)
                schemas.append({
                    "name": t.name,
                    "description": t.description,
                    "parameters": cleaned
                })

        return schemas

    # ----------------------------------------
    # 2) EXTRACT GEMINI TOOL CALLS
    # ----------------------------------------
    @staticmethod
    def _proto_to_dict(proto_obj):
        """
        Recursively convert protobuf objects to native Python types.
        """
        from proto.marshal.collections.maps import MapComposite
        from proto.marshal.collections.repeated import RepeatedComposite
        
        if isinstance(proto_obj, MapComposite):
            # Convert protobuf map to regular dict
            return {k: ToolManager._proto_to_dict(v) for k, v in proto_obj.items()}
        elif isinstance(proto_obj, RepeatedComposite):
            # Convert protobuf repeated field to list
            return [ToolManager._proto_to_dict(item) for item in proto_obj]
        elif isinstance(proto_obj, dict):
            return {k: ToolManager._proto_to_dict(v) for k, v in proto_obj.items()}
        elif isinstance(proto_obj, (list, tuple)):
            return [ToolManager._proto_to_dict(item) for item in proto_obj]
        else:
            # Return primitive types as-is
            return proto_obj
        
    @classmethod
    def extract_tool_calls(cls, response):
        calls = []
        if not hasattr(response, "candidates"):
            return calls
        
        for cand in response.candidates:
            if not hasattr(cand, "content"):
                continue

            for part in getattr(cand.content, "parts", []):
                fc = getattr(part, "function_call", None)
                if not fc:
                    continue

                calls.append({
                    "name": fc.name,
                    "arguments": cls._proto_to_dict(fc.args) if fc.args else {}
                })
        return calls    

    # ----------------------------------------
    # 3) EXECUTE TOOLS
    # ----------------------------------------
    @classmethod
    async def execute_tool_calls(
        cls,
        clients: Dict[str, Any],
        tool_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Executes requested tools against the correct MCP client.
        Returns list of tool result objects.

        Output format example:
        [
          {
            "tool_name": "read_sheet",
            "content": [... rows ...]
          }
        ]
        """

        tool_results: List[Dict[str, Any]] = []

        for call in tool_calls:
            name = call["name"]
            input_args = call["arguments"]
            
            client = await cls._find_client_with_tool(clients, name)
            if not client:
                logger.error(f"Tool not found: {name}")
                tool_results.append(
                    {
                        "tool_name": name,
                        "error": f"MCP tool '{name}' not available",
                    }
                )
                continue

            try:
                res = await client.call_tool(name, input_args)

                # Extract content (usually list-of-dict JSON as text)
                items = []
                if res and res.content:
                    for c in res.content:
                        if hasattr(c, "text"):
                            items.append(c.text)

                tool_results.append(
                    {
                        "tool_name": name,
                        "content": items,
                    }
                )

            except Exception as e:
                msg = f"Error executing tool '{name}': {e}"
                logger.error(msg)

                tool_results.append(
                    {
                        "tool_name": name,
                        "error": msg,
                    }
                )

        return tool_results

    # ----------------------------------------
    # Utility: find MCP client for tool
    # ----------------------------------------
    @classmethod
    async def _find_client_with_tool(cls, clients, tool_name: str):
        for client in clients.values():
            try:
                tools = getattr(client, "cached_tools", None)
                if not tools:
                    tools = await client.list_tools()
                for t in tools:
                    if t.name == tool_name:
                        return client
            except:
                continue
        return None
