from fastapi import APIRouter
import httpx
import asyncio
from typing import Dict, Any
from app.core.config import settings

router = APIRouter()

async def check_service(url: str, name: str) -> Dict[str, str]:
    """Check a service's availability by making a GET request."""
    if not url:
        return {"status": "OFFLINE", "label": name}
    
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            # For Ollama, we might want to check /api/tags or just the root
            response = await client.get(url)
            if response.status_code < 500:
                return {"status": "ONLINE", "label": name}
            else:
                return {"status": "STANDBY", "label": name}
    except Exception:
        return {"status": "OFFLINE", "label": name}

@router.get("/vitals")
async def get_vitals():
    """
    Standardized health check for all core services.
    Checks Backend API, Ollama, and ComfyUI.
    """
    # Run checks in parallel
    # Note: COMFYUI_HOST is not in settings yet, adding it or using default
    import os
    comfyui_host = os.getenv("COMFYUI_HOST", "http://localhost:8188")
    
    ollama_task = check_service(settings.OLLAMA_HOST, "Ollama (LLM)")
    comfyui_task = check_service(comfyui_host, "ComfyUI Bridge")
    
    ollama_res, comfyui_res = await asyncio.gather(ollama_task, comfyui_task)

    return {
        "api": {"status": "ONLINE", "label": "Backend API"},
        "ollama": ollama_res,
        "comfyui": comfyui_res
    }
