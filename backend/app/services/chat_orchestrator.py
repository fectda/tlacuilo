import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.clients.llm.base import LLMClient
from app.services.project_manager import ProjectManager
from app.services.prompt_service import PromptService
from app.services.validation_service import ValidationService
from app.repositories.project_repository import ProjectRepository

logger = logging.getLogger(__name__)

class ChatOrchestrator:
    def __init__(self, 
                 llm_client: LLMClient, 
                 project_manager: ProjectManager, 
                 prompt_service: PromptService,
                 validation_service: ValidationService,
                 repository: ProjectRepository):
        self.llm = llm_client
        self.manager = project_manager
        self.prompts = prompt_service
        self.validator = validation_service
        self.repo = repository

    async def initialize_new_project(self, collection: str, slug: str) -> Dict[str, Any]:
        project_dir = self.repo.get_project_dir(collection, slug)
        working_copy = self.manager.get_working_copy(collection, slug)
        
        system_prompt = self.prompts.get_system_prompt(collection, slug, working_copy["content"])
        strategy_prompt = self.prompts.get_strategy_prompt(collection)
        
        history = [{
            "role": "system", 
            "content": f"{system_prompt}\n\n{strategy_prompt}", 
            "system_only": True
        }]
        
        history.append({
            "role": "user",
            "content": "[SYSTEM_TRIGGER: INICIAR ENTREVISTA]",
            "system_only": True
        })
        
        response_content = await self.llm.chat(history)
        assistant_msg = self._create_message("assistant", response_content)
        history.append(assistant_msg)
        
        self.repo.save_chat_history(project_dir, history)
        return assistant_msg

    async def process_message(self, collection: str, slug: str, content: str, 
                               system_only: bool = False, 
                               response_system_only: bool = False) -> Dict[str, Any]:
        project_dir = self.repo.get_project_dir(collection, slug)
        history = self.repo.get_chat_history(project_dir)
        
        # Inject system prompt if missing
        if not history or history[0]["role"] != "system":
            working_copy = self.manager.get_working_copy(collection, slug)
            system_prompt = self.prompts.get_system_prompt(collection, slug, working_copy["content"])
            strategy_prompt = self.prompts.get_strategy_prompt(collection)
            history.insert(0, {
                "role": "system", 
                "content": f"{system_prompt}\n\n{strategy_prompt}", 
                "system_only": True
            })

        user_msg = self._create_message("user", content, system_only)
        history.append(user_msg)
        
        response_content = await self.llm.chat(history)
        assistant_msg = self._create_message("assistant", response_content, response_system_only)
        history.append(assistant_msg)
        
        self.repo.save_chat_history(project_dir, history)
        return assistant_msg

    async def generate_draft(self, collection: str, slug: str) -> str:
        project_dir = self.repo.get_project_dir(collection, slug)
        history = self.repo.get_chat_history(project_dir)
        working_copy = self.manager.get_working_copy(collection, slug)
        
        # Build instruction
        template = self.manager._find_template(collection)
        style = self.manager.get_style_reference(collection)
        
        # Prepare context injection as a USER message for better priority
        # Role Eduardo personification as requested
        context_message = (
            "Eduardo: Por favor, genera o actualiza el borrador del proyecto basándote en nuestra conversación reciente.\n\n"
            "---\n"
            "## ESTRUCTURA DE REFERENCIA:\n"
            "```markdown\n" + (self.repo.read_text(template) if template else "") + "\n```\n\n"
            "## REFERENCIAS DE ESTILO:\n"
            "```markdown\n" + (self.repo.read_text(style) if style else "") + "\n```\n\n"
            "## CONTENIDO ACTUAL:\n"
            "```markdown\n" + working_copy["content"] + "\n```\n\n"
            "---\n"
            "## INSTRUCCIONES:\n"
            + self.prompts.get_draft_strategy()
        )
        
        # Prepare request message (not yet added to history)
        request_msg = self._create_message("user", context_message, system_only=True)
        draft_history = history + [request_msg]
        
        draft_content = ""
        max_retries = 3
        for attempt in range(max_retries):
            raw_response = await self.llm.chat(draft_history)
            candidate = self.validator.sanitize_draft(raw_response)
            validation_error = self.validator.validate_schema(candidate)
            is_valid = validation_error is None
            
            # Debug logging for ALL attempts in drafts-tests/
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_dir = project_dir / "drafts-tests"
            debug_dir.mkdir(parents=True, exist_ok=True)
            
            suffix = "success" if is_valid else "fail"
            # Save Raw Response (MD) and History (JSON) for technical audit
            self.repo.write_text(debug_dir / f"{timestamp}_{suffix}_raw.md", raw_response)
            self.repo.write_json(debug_dir / f"{timestamp}_{suffix}_history.json", draft_history)
            
            if is_valid:
                draft_content = candidate
                # SELECTIVE PERSISTENCE: Save both request and response to history
                history.append(request_msg)
                assistant_msg = self._create_message("assistant", draft_content, system_only=True)
                history.append(assistant_msg)
                
                self.repo.save_chat_history(project_dir, history)
                logger.info(f"Draft valid on attempt {attempt+1}. Request and response persisted to history.")
                break
            else:
                logger.warning(f"Draft validation failed on attempt {attempt+1}. Error: {validation_error}")

        if not draft_content:
            raise ValueError("IA failed to generate valid draft after multiple retries.")

        return draft_content

    async def translate_proposal(self, source_content: str) -> str:
        system_prompt = self.prompts.get_translator_prompt()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Translate this:\n\n{source_content}"}
        ]
        return await self.llm.chat(messages)

    def _create_message(self, role: str, content: str, system_only: bool = False) -> Dict[str, Any]:
        return {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "system_only": system_only
        }
