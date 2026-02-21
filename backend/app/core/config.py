import os
from pathlib import Path

class Config:
    PROJECTS_PATH = Path(os.getenv("PROJECTS_PATH", "/home/tlacuilo/projects"))
    PORTAFOLIO_PATH = Path(os.getenv("PORTAFOLIO_PATH", "/home/tlacuilo/portfolio"))
    PROMPTS_PATH = Path(os.getenv("PROMPTS_PATH", "/app/prompts"))
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    LLM_MODEL = os.getenv("LLM_MODEL", "mistral")

settings = Config()
