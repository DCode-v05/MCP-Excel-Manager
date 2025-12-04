# backend/services/gemini_service.py
from typing import List, Dict, Any, Optional
import json
import google.generativeai as genai


from backend.config import get_settings
from backend.utils.logger import get_logger


logger = get_logger(__name__)
settings = get_settings()


class GeminiService:
    """
    Wrapper around the Gemini API.

    Responsibilities:
    - Send chat messages
    - Handle function (tool) calls
    - Format result blocks for Gemini
    """

    def __init__(self, model: str = "gemini-2.5-flash"):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model)

    # ---------------------------------------------------------
    #  MESSAGE FORMATTING
    # ---------------------------------------------------------

    @staticmethod
    def to_gemini_messages(messages: List[Dict[str, Any]]):
        """
        Convert our internal message format to Gemini format.

        Expected:
        [
            {"role": "user", "parts": "..."},
            {"role": "model", "parts": "..."},
        ]
        """
        formatted = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")

            formatted.append({
                "role": role,
                "parts": [
                    {"text": content}
                ]
            })

        return formatted

    @staticmethod
    def extract_text(response):
        """
        Extract plain text from Gemini response
        """
        if hasattr(response, "candidates"):
            for cand in response.candidates:
                if not hasattr(cand, "content"):
                    continue

                parts = getattr(cand.content, "parts", [])
                for p in parts:
                    txt = getattr(p, "text", None)
                    if txt:
                        return txt

    # ---------------------------------------------------------
    #  MAIN CHAT CALL
    # ---------------------------------------------------------

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools_schema: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Send messages to Gemini.

        tools_schema:
            [
                {
                    "name": "tool_name",
                    "description": "...",
                    "parameters": {... JSONSchema ...}
                }
            ]

        Returns either:
           - normal model text
           - or model function calls
        """

        formatted_msgs = self.to_gemini_messages(messages)

        logger.info("Sending Gemini chat request...")
        res = self.model.generate_content(
            formatted_msgs,
            tools={"function_declarations": tools_schema})
        return res

    # ---------------------------------------------------------
    #  POST-TOOL CALL LOOP
    # ---------------------------------------------------------

    async def resume_with_tool_results(self,
        messages: List[Dict[str, Any]],
        tool_response: List[Dict[str, Any]],
        tools_schema: Optional[List[Dict[str, Any]]] = None):
        """
        Execute second step:
        - include tool results
        - ask Gemini to continue
        """
        formatted_msgs = self.to_gemini_messages(messages)
        
        # Add tool results as function response parts
        function_responses = []
        for tr in tool_response:
            function_responses.append({
                "function_response": {
                    "name": tr["tool_name"],
                    "response": {
                        "content": tr["content"]
                    }
                }
            })
        
        # Add all function responses as a single "function" role message
        formatted_msgs.append({
            "role": "function",
            "parts": function_responses
        })

        logger.info("Resuming Gemini chat with tool results...")
        res = self.model.generate_content(
            formatted_msgs,
            tools={"function_declarations": tools_schema}
        )
        return res