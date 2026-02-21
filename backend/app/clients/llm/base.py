from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMClient(ABC):
    @abstractmethod
    async def chat(self, messages: List[Dict[str, Any]]) -> str:
        """Sends a list of messages to the LLM and returns the response content."""
        pass
