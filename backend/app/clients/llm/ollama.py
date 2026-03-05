import httpx
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from app.clients.llm.base import LLMClient
from app.core.config import settings

logger = logging.getLogger(__name__)

class OllamaClient(LLMClient):
    def __init__(self):
        self.host = settings.OLLAMA_HOST
        self.model = settings.LLM_MODEL

    async def chat(self, messages: List[Dict[str, Any]], model_override: str = None, debug_path: Any = None) -> str:
        # Sanitizer Protocol: Remove internal metadata (timestamp, system_only, is_note)
        ollama_messages = [{"role": m["role"], "content": m["content"], **({"images": m["images"]} if "images" in m else {})} for m in messages]
        
        payload = {
            "model": model_override or self.model,
            "messages": ollama_messages,
            "stream": False
        }

        try:
            # VLM generations can take several minutes to process on local GPUs
            async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
                response = await client.post(f"{self.host}/api/chat", json=payload)
                response.raise_for_status()
                res_content = response.json()["message"]["content"]

                if settings.DEBUG_LOGS_ENABLED and debug_path:
                    self._save_debug_log(ollama_messages, res_content, debug_path)

                return res_content
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP Error: {e.response.text}")
            raise Exception(f"IA Service Error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            raise Exception(f"Connection error with IA service: {str(e)}")

    def _save_debug_log(self, messages: List[Dict], response: str, debug_path: Any):
        """Saves a clean snapshot of the conversation (Point 1 & 4)"""
        try:
            p = Path(debug_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            
            # Simplified history generation: cleaning images and adding response in one flow
            history = [
                {**m, "images": [f"[IMG_DATA_{len(img)}] " for img in m["images"]]} if "images" in m else m 
                for m in messages
            ]
            history.append({"role": "assistant", "content": response})
            
            p.write_text(json.dumps(history, indent=2), encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to save debug log: {e}")
