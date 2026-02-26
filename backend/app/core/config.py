import os
from pathlib import Path

class Config:
    PROJECTS_PATH = Path(os.getenv("PROJECTS_PATH", "/home/tlacuilo/projects"))
    PORTAFOLIO_PATH = Path(os.getenv("PORTAFOLIO_PATH", "/home/tlacuilo/portfolio"))
    PROMPTS_PATH = Path(os.getenv("PROMPTS_PATH", "/app/prompts"))
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
    VISION_MODEL = os.getenv("VISION_MODEL", "qwen3-vl:8b")
    COMFYUI_HOST = os.getenv("COMFYUI_HOST", "http://localhost:8188")
    DEBUG_LOGS_ENABLED = os.getenv("DEBUG_LOGS_ENABLED", "false").lower() == "true"

settings = Config()
