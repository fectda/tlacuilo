from datetime import datetime
from typing import Dict, Any
from app.clients.llm.base import LLMClient
from app.repositories.project_repository import ProjectRepository
from app.services.validators.project import ProjectValidator
from app.services.validators.content import ContentValidator
from app.services.project.working_copy import ProjectWorkingCopyService
from app.services.prompt_service import PromptService

class ChatConversationService:
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
    async def get_history(self, collection: str, slug: str) -> Dict[str, Any]:
        import json
        from fastapi import HTTPException
        p_dir = self.repo.get_project_dir(collection, slug)
        
        path = p_dir / "chat_history.json"
        if not path.exists():
            return {"messages": []}
            
        content = self.repo.read_text(path)
        if not content:
            return {"messages": []}
            
        try:
            raw_history = json.loads(content)
        except json.JSONDecodeError:
            corrupt_path = path.with_suffix(".json.corrupt")
            self.repo.copy_file(path, corrupt_path)
            path.unlink(missing_ok=True)
            raise HTTPException(status_code=500, detail="Corrupted chat history file. Renamed to .corrupt.")
            
        filtered = [m for m in raw_history if not m.get("system_only", False)]
        filtered.sort(key=lambda x: x.get("timestamp", ""))
        
        return {"messages": filtered}

    async def initialize_new_project(self, collection: str, slug: str) -> Dict[str, Any]:
        p_dir = self.repo.get_project_dir(collection, slug)
        
        wc = self.working_copy_service.get_working_copy(collection, slug)
        sys_p = self.prompts.get_system_prompt(collection, slug, wc["content"])
        strat_p = self.prompts.get_strategy_prompt(collection)
        
        history = [
            {"role": "system", "content": f"{sys_p}\n\n{strat_p}", "system_only": True},
            {"role": "user", "content": "[SYSTEM_TRIGGER: INICIAR ENTREVISTA]", "system_only": True}
        ]
        
        res = await self.llm.chat(history)
        msg = self._create_message("assistant", res)
        history.append(msg)
        self.repo.save_chat_history(p_dir, history)
        return msg

    async def process_message(self, collection: str, slug: str, content: str, 
                               system_only: bool = False, 
                               response_system_only: bool = False) -> Dict[str, Any]:
        self.cont_validator.ensure_content(content)
        p_dir = self.repo.get_project_dir(collection, slug)
        
        history = self.repo.get_chat_history(p_dir)
        if not history or history[0]["role"] != "system":
            wc = self.working_copy_service.get_working_copy(collection, slug)
            sys_p = self.prompts.get_system_prompt(collection, slug, wc["content"])
            strat_p = self.prompts.get_strategy_prompt(collection)
            history.insert(0, {"role": "system", "content": f"{sys_p}\n\n{strat_p}", "system_only": True})

        history.append(self._create_message("user", content, system_only))
        res = await self.llm.chat(history)
        msg = self._create_message("assistant", res, response_system_only)
        history.append(msg)
        self.repo.save_chat_history(p_dir, history)
        return msg

    def _create_message(self, role: str, content: str, system_only: bool = False) -> Dict[str, Any]:
        return {"role": role, "content": content, "timestamp": datetime.now().isoformat(), "system_only": system_only}
