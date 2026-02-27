import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from app.clients.llm.base import LLMClient
from app.repositories.project_repository import ProjectRepository
from app.services.validators.project import ProjectValidator
from app.services.validators.content import ContentValidator
from app.services.project.working_copy import ProjectWorkingCopyService
from app.services.prompt_service import PromptService
from app.core.config import settings

logger = logging.getLogger(__name__)

class ChatDraftService:
    def __init__(self, llm: LLMClient, repo: ProjectRepository, 
                 proj_validator: ProjectValidator, cont_validator: ContentValidator,
                 working_copy_service: ProjectWorkingCopyService,
                 prompts: PromptService):
        self.llm = llm
        self.repo = repo
        self.proj_validator = proj_validator
        self.cont_validator = cont_validator
        self.working_copy_service = working_copy_service
        self.prompts = prompts

    async def generate_draft(self, collection: str, slug: str) -> str:
        self.proj_validator.ensure_collection(collection)
        p_dir = self.repo.get_project_dir(collection, slug)
        self.proj_validator.ensure_project_exists(p_dir, slug)
        
        history = self.repo.get_chat_history(p_dir)
        wc = self.working_copy_service.get_working_copy(collection, slug)
        template_path = self.repo.portfolio_path / "src" / "templates" / f"{collection}-template.md"
        template_content = self.repo.read_text(template_path) if template_path.exists() else ""
        
        context = (
            f"## ESTRUCTURA:\n```markdown\n{template_content}\n```\n\n"
            f"## CONTENIDO ACTUAL:\n```markdown\n{wc['content']}\n```\n\n"
            f"## INSTRUCCIONES:\n{self.prompts.get_draft_strategy()}"
        )
        
        req_msg = {"role": "user", "content": context, "system_only": True, "timestamp": datetime.now().isoformat()}
        draft_history = history + [req_msg]
        
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_dir = p_dir / "drafts-tests"

        for attempt in range(3):
            # Centralized JSON Logging (Point 1)
            log_name = f"{ts}_at{attempt+1}_history.json"
            raw = await self.llm.chat(draft_history, debug_path=debug_dir / log_name)
            
            candidate = self.cont_validator.sanitize_draft(raw)
            err = self.cont_validator.validate_schema(candidate, collection)
            
            # Markdown Copy (Point 2: Encapsulated helper)
            self._save_debug_md(debug_dir / f"{ts}_at{attempt+1}_{'ok' if not err else 'fail'}.md", raw)

            if not err:
                history.append(req_msg)
                history.append({"role": "assistant", "content": candidate, "system_only": True, "timestamp": datetime.now().isoformat()})
                self.repo.save_chat_history(p_dir, history)
                return candidate
        raise ValueError("IA failed valid draft generation.")

    async def process_translation_draft(self, collection: str, slug: str, from_scratch: bool, 
                                       instruction: Optional[str] = None, 
                                       current_draft: Optional[str] = None) -> str:
        self.proj_validator.ensure_collection(collection)
        p_dir = self.repo.get_project_dir(collection, slug)
        self.proj_validator.ensure_project_exists(p_dir, slug)
        
        wc = self.working_copy_service.get_working_copy(collection, slug)
        sys_msg = f"{self.prompts.get_global_system_prompt(collection, slug, wc['content'])}\n\n{self.prompts.get_translation_strategy()}"
        
        if from_scratch: 
            user_msg = f"Translate to English:\n---\n{wc['content']}\n---"
        else: 
            user_msg = f"REFINE English draft:\nINSTRUCTION: {instruction}\nSOURCE: {wc['content']}\nDRAFT: {current_draft}"

        msgs = [{"role": "system", "content": sys_msg}, {"role": "user", "content": user_msg}]
        
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_dir = p_dir / "drafts-tests"

        for attempt in range(3):
            log_name = f"{ts}_en_at{attempt+1}_history.json"
            raw = await self.llm.chat(msgs, debug_path=debug_dir / log_name)
            msgs.append({"role": "assistant", "content": raw})
            
            candidate = self.cont_validator.sanitize_draft(raw)
            err = self.cont_validator.validate_schema(candidate, collection)
            
            # Markdown Copy (Point 2: Encapsulated helper)
            self._save_debug_md(debug_dir / f"{ts}_at{attempt+1}_{'en_ok' if not err else 'en_fail'}.md", raw)

            if not err: return candidate
            
            msgs.append({"role": "user", "content": f"{self.prompts.get_correction_strategy()}\n\nERROR: {err}"})
            
        return candidate

    def _save_debug_md(self, path: Path, content: str):
        """Helper to centralize MD logging logic (Point 2 & 4)"""
        if settings.DEBUG_LOGS_ENABLED:
            self.repo.write_text(path, content)
