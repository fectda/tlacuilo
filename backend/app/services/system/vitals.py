import httpx
import asyncio
from typing import Dict, List, Any
from app.core.config import settings

class SystemVitalsService:
    async def get_all_vitals(self) -> Dict[str, Any]:
        """Consolidated health check for all services."""
        # Define services to check
        checks = [
            self.check_service(settings.OLLAMA_HOST, "Ollama (LLM)"),
            self.check_service(settings.COMFYUI_HOST, "ComfyUI Bridge")
        ]
        
        results = await asyncio.gather(*checks)
        
        return {
            "api": {"status": "ONLINE", "label": "Backend API"},
            "ollama": results[0],
            "comfyui": results[1]
        }

    async def check_service(self, url: str, name: str) -> Dict[str, str]:
        """Generic logic to check any external service status."""
        if not url:
            return {"status": "OFFLINE", "label": name}
        
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(url)
                # Any non-5xx response is considered 'online' or 'standby'
                status = "ONLINE" if response.status_code < 500 else "STANDBY"
                return {"status": status, "label": name}
        except Exception:
            return {"status": "OFFLINE", "label": name}
