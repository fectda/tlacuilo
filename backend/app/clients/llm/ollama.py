import httpx
import logging
from typing import List, Dict, Any
from app.clients.llm.base import LLMClient
from app.core.config import settings

logger = logging.getLogger(__name__)

class OllamaClient(LLMClient):
    def __init__(self):
        self.host = settings.OLLAMA_HOST
        self.model = settings.LLM_MODEL

    async def chat(self, messages: List[Dict[str, Any]], model_override: str = None) -> str:
        # Sanitizer Protocol: Remove internal metadata (timestamp, system_only)
        ollama_messages = []
        for msg in messages:
            clean_msg = {"role": msg["role"], "content": msg["content"]}
            if "images" in msg:
                clean_msg["images"] = msg["images"]
            ollama_messages.append(clean_msg)
        
        payload = {
            "model": model_override or self.model,
            "messages": ollama_messages,
            "stream": False
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(f"{self.host}/api/chat", json=payload)
                response.raise_for_status()
                return response.json()["message"]["content"]
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP Error: {e.response.text}")
            raise Exception(f"IA Service Error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            raise Exception(f"Connection error with IA service: {str(e)}")
