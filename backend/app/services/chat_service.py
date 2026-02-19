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

    async def initialize_new_project(self, collection: str, slug: str) -> Dict[str, Any]:
        """
        Escenario 1: Lienzo en Blanco.
        Construye Contexto Cero y obtiene saludo inicial.
        """
        project_dir = self._get_project_dir(collection, slug)
        
        # 1. Base Knowledge: System Prompt
        system_prompt = self._read_prompt(self.prompts_path / "system" / "tlacuilo_digital.md")
        
        # 2. Strategy Prompt
        strategy_file = "atoms_bits_strategy.md" if collection in ["atoms", "bits"] else "mind_strategy.md"
        strategy_prompt = self._read_prompt(self.prompts_path / "strategies" / strategy_file)
        
        full_context = f"{system_prompt}\n\n{strategy_prompt}"
        
        # 3. Contexto Cero (Hidden System Message)
        history = [
            {
                "role": "system", 
                "content": full_context, 
                "timestamp": datetime.now().isoformat(),
                "system_only": True
            }
        ]
        
        # 4. First AI Greeting (Triggered internally)
        # We simulate a "start" trigger message to the AI
        history.append({
            "role": "user",
            "content": "[SYSTEM_TRIGGER: INICIAR ENTREVISTA]",
            "timestamp": datetime.now().isoformat(),
            "system_only": True
        })
        
        response_content = await self._call_ollama(history)
        
        assistant_msg = {
            "role": "assistant",
            "content": response_content,
            "timestamp": datetime.now().isoformat()
        }
        history.append(assistant_msg)
        
        self._save_history(project_dir, history)
        return assistant_msg

    async def process_pending_debt(self, collection: str, slug: str) -> Dict[str, Any]:
        """
        Escenario 2: Deuda Técnica (Último msg User).
        """
        project_dir = self._get_project_dir(collection, slug)
        history = self._load_history(project_dir)
        
        response_content = await self._call_ollama(history)
        
        assistant_msg = {
            "role": "assistant",
            "content": response_content,
            "timestamp": datetime.now().isoformat()
        }
        history.append(assistant_msg)
        
        self._save_history(project_dir, history)
        return assistant_msg

    async def process_message(self, collection: str, slug: str, content: str, 
                              system_only: bool = False, 
                              response_system_only: bool = False) -> Dict[str, Any]:
        """
        POST .../message implementation.
        """
        if not content.strip():
            raise ValueError("Message content cannot be empty")

        project_dir = self._get_project_dir(collection, slug)
        history = self._load_history(project_dir)
        
        # Ensure system prompt exists (Safety injection if re-routing or manual edit cleared it)
        if not history or history[0]["role"] != "system":
            system_prompt = self._read_prompt(self.prompts_path / "system" / "tlacuilo_digital.md")
            strategy_file = "atoms_bits_strategy.md" if collection in ["atoms", "bits"] else "mind_strategy.md"
            strategy_prompt = self._read_prompt(self.prompts_path / "strategies" / strategy_file)
            history.insert(0, {
                "role": "system", 
                "content": f"{system_prompt}\n\n{strategy_prompt}", 
                "timestamp": datetime.now().isoformat(),
                "system_only": True
            })

        # Append User message
        user_msg = {
            "role": "user",
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "system_only": system_only
        }
        history.append(user_msg)
        
        # Call LLM
        response_content = await self._call_ollama(history)
        
        # Append Assistant response
        assistant_msg = {
            "role": "assistant",
            "content": response_content,
            "timestamp": datetime.now().isoformat(),
            "system_only": response_system_only
        }
        history.append(assistant_msg)
        
        self._save_history(project_dir, history)
        return assistant_msg

    async def generate_draft(self, collection: str, slug: str) -> str:
        """
        POST .../draft implementation.
        """
        project_dir = self._get_project_dir(collection, slug)
        history = self._load_history(project_dir)
        
        # Load Draft Generation Strategy
        draft_strategy = self._read_prompt(self.prompts_path / "strategies" / "draft_generation.md")
        
        # Final instruction prompt (invisible)
        draft_history = history + [{
            "role": "system", 
            "content": draft_strategy,
            "system_only": True
        }]
        
        draft_content = await self._call_ollama(draft_history)
        
        # Sanitization: Clean code blocks
        draft_content = draft_content.replace("```markdown", "").replace("```", "").strip()
        
        # Persist response in history as system_only (as per ARCHITECTURE 3.B.2.B.160)
        history.append({
            "role": "assistant",
            "content": draft_content,
            "timestamp": datetime.now().isoformat(),
            "system_only": True
        })
        self._save_history(project_dir, history)
        
        return draft_content

    async def translate_proposal(self, collection: str, slug: str, source_content: str) -> str:
        """
        Generates a translation proposal using translator.md.
        """
        system_prompt = self._read_prompt(self.prompts_path / "system" / "translator.md")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Translate this:\n\n{source_content}"}
        ]
        return await self._call_ollama(messages)

    async def refine_translation(self, collection: str, slug: str, english_content: str, user_instruction: str) -> str:
        """
        Refines an existing translation.
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
            except Exception as e:
                logger.error(f"Error loading history for {project_dir}: {e}")
                return []
        return []

    def _save_history(self, project_dir: Path, history: List[Dict[str, Any]]):
        history_file = project_dir / "chat_history.json"
        try:
            history_file.write_text(json.dumps(history, indent=2))
        except Exception as e:
            logger.error(f"Error saving history for {project_dir}: {e}")

    async def _call_ollama(self, messages: List[Dict[str, Any]]) -> str:
        """
        Sanitizer Protocol: Remove internal metadata (timestamp, system_only).
        """
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
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP Error: {e.response.text}")
            raise Exception(f"IA Service Error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            raise Exception(f"Connection error with IA service: {str(e)}")
