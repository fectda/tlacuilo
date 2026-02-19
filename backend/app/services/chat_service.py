import os
import json
import httpx
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.projects_path = Path(os.getenv("PROJECTS_PATH", "/home/tlacuilo/projects"))
        self.portfolio_path = Path(os.getenv("PORTAFOLIO_PATH", "/home/tlacuilo/portfolio"))
        self.prompts_path = Path("/app/prompts") 
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        # Try to use a sensible default, but allow override
        self.model = os.getenv("LLM_MODEL", "mistral") 

    def _get_project_dir(self, collection: str, slug: str) -> Path:
        return self.projects_path / collection / slug

    def _read_prompt(self, path: Path) -> str:
        if path.exists():
            return path.read_text()
        logger.warning(f"Prompt file not found: {path}")
        return ""

    async def start_interview(self, collection: str, slug: str) -> List[Dict[str, Any]]:
        project_dir = self._get_project_dir(collection, slug)
        if not project_dir.exists():
            project_dir.mkdir(parents=True, exist_ok=True)

        # Choose strategy
        strategy = "forense" if collection in ["atoms", "bits"] else "manifesto"
        
        # Load prompts
        system_base = self._read_prompt(self.prompts_path / "system" / "tlacuilo.md")
        strategy_prompt = self._read_prompt(self.prompts_path / "strategies" / f"{strategy}.md")
        
        full_system_prompt = f"{system_base}\n\n{strategy_prompt}"
        
        # Reset history
        history = [
            {
                "role": "system", 
                "content": full_system_prompt, 
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        # First message
        first_message = {
            "role": "assistant",
            "content": "Hola, soy Tlacuilo. Empecemos definiendo el contexto del proyecto. ¿Me puedes contar un poco sobre el desafío que intentas resolver?",
            "timestamp": datetime.now().isoformat()
        }
        history.append(first_message)
        
        self._save_history(project_dir, history)
        return history

    async def send_message(self, collection: str, slug: str, message_text: str, mode: str = "interview") -> List[Dict[str, Any]]:
        project_dir = self._get_project_dir(collection, slug)
        history = self._load_history(project_dir)
        
        # If history is empty or missing system prompt, re-initialize (safety)
        if not history or history[0]["role"] != "system":
            strategy = "forense" if collection in ["atoms", "bits"] else "manifesto"
            system_base = self._read_prompt(self.prompts_path / "system" / "tlacuilo.md")
            strategy_prompt = self._read_prompt(self.prompts_path / "strategies" / f"{strategy}.md")
            full_system_prompt = f"{system_base}\n\n{strategy_prompt}"
            if not history:
                history = [{"role": "system", "content": full_system_prompt, "timestamp": datetime.now().isoformat()}]
            else:
                history.insert(0, {"role": "system", "content": full_system_prompt, "timestamp": datetime.now().isoformat()})

        # Add user message
        history.append({
            "role": "user",
            "content": message_text,
            "timestamp": datetime.now().isoformat()
        })
        
        # Call LLM
        response_content = await self._call_ollama(history)
        
        # Add assistant message
        history.append({
            "role": "assistant",
            "content": response_content,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_history(project_dir, history)
        return history

    async def generate_draft(self, collection: str, slug: str) -> str:
        project_dir = self._get_project_dir(collection, slug)
        history = self._load_history(project_dir)
        
        # Load Strategy for context (Forense/Spec Sheet vs Manifesto)
        # Using definitions folder for structure rules (Architecture rule 3.B.1.5)
        
        # Instructions for draft
        draft_instruction = ("Genera una propuesta de actualización para el archivo .md final. "
                             "Sigue estrictamente la estructura técnica según la colección. "
                             "Solo devuelve el contenido Markdown, sin explicaciones ni introducciones.")
        
        # Temporarily append instruction for the LLM call
        draft_history = history + [{"role": "system", "content": draft_instruction}]
        
        draft_content = await self._call_ollama(draft_history)
        
        # NOTE: WE DO NOT PERSIST HERE. The user must call /persist to write to disk.
        
        return draft_content

    async def translate_proposal(self, collection: str, slug: str, source_content: str) -> str:
        """
        Generates a translation proposal based on the provided source content.
        """
        system_prompt = self._read_prompt(self.prompts_path / "system" / "translator.md")
        if not system_prompt:
            system_prompt = "You are a professional technical translator. Translate the following Markdown content to English, maintaining all frontmatter and structure."
            
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Translate this:\n\n{source_content}"}
        ]
        
        return await self._call_ollama(messages)

    async def refine_translation(self, collection: str, slug: str, english_content: str, user_instruction: str) -> str:
        """
        Refines an existing translation based on user instructions.
        """
        system_prompt = self._read_prompt(self.prompts_path / "system" / "translator.md")
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": english_content},
            {"role": "user", "content": user_instruction}
        ]
        
        return await self._call_ollama(messages)

    def _load_history(self, project_dir: Path) -> List[Dict[str, Any]]:
        history_file = project_dir / "chat_history.json"
        if history_file.exists():
            try:
                return json.loads(history_file.read_text())
            except:
                return []
        return []

    def _save_history(self, project_dir: Path, history: List[Dict[str, Any]]):
        history_file = project_dir / "chat_history.json"
        history_file.write_text(json.dumps(history, indent=2))

    async def _call_ollama(self, messages: List[Dict[str, Any]]) -> str:
        # Filter messages for Ollama (it doesn't like 'timestamp')
        ollama_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
        
        payload = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(f"{self.ollama_host}/api/chat", json=payload)
                response.raise_for_status()
                return response.json()["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return f"Error: No se pudo conectar con el servicio de IA ({self.ollama_host}). Detalle: {str(e)}"
