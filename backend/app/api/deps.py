from fastapi import Path, HTTPException
from app.repositories.project_repository import ProjectRepository
from app.clients.llm.ollama import OllamaClient
from app.clients.comfyui import ComfyUIClient
from app.services.prompt_service import PromptService

# Specialized Validators
from app.services.validators.project import ProjectValidator
from app.services.validators.content import ContentValidator
from app.services.validators.studio import StudioValidator

# Specialized Services
from app.services.project.discovery import ProjectDiscoveryService
from app.services.project.working_copy import ProjectWorkingCopyService
from app.services.project.publish import ProjectPublishService
from app.services.studio.shot_manager import StudioShotManager
from app.services.studio.generation import StudioGenerationService
from app.services.studio.assets import StudioAssetService
from app.services.chat.conversation import ChatConversationService
from app.services.chat.draft import ChatDraftService
from app.services.system.vitals import SystemVitalsService

# Singletons / Shared Instances
_repo = ProjectRepository()
_llm = OllamaClient()
_comfy = ComfyUIClient()
_prompts = PromptService()

_proj_validator = ProjectValidator()
_cont_validator = ContentValidator()
_studio_validator = StudioValidator()
_vitals_service = SystemVitalsService()

# --- Dependency Providers ---

def get_repository(): return _repo
def get_llm(): return _llm
def get_comfy(): return _comfy
def get_prompts(): return _prompts

# Validators
def get_proj_validator(): return _proj_validator
def get_cont_validator(): return _cont_validator
def get_studio_validator(): return _studio_validator

# Route Dependencies
def validate_collection(collection: str = Path(...)):
    try:
        _proj_validator.ensure_collection(collection)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def validate_project_exists(collection: str = Path(...), slug: str = Path(...)):
    local_exists = _repo.get_project_dir(collection, slug).exists()
    portfolio_exists = _repo.resolve_portfolio_path(collection, slug) is not None
    if not local_exists and not portfolio_exists:
        raise HTTPException(status_code=404, detail=f"Project '{slug}' does not exist in collection '{collection}'.")

def validate_shot_exists(collection: str = Path(...), slug: str = Path(...), shot_id: str = Path(...)):
    path = _repo.get_project_dir(collection, slug) / "shots" / shot_id
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Shot '{shot_id}' does not exist.")

# Project Services
def get_project_discovery():
    return ProjectDiscoveryService(_repo, _proj_validator)

def get_project_working_copy():
    return ProjectWorkingCopyService(_repo, _proj_validator, _cont_validator, _llm, _prompts)

def get_project_publish():
    return ProjectPublishService(_repo, _proj_validator, _cont_validator, _llm, _prompts)

# Studio Services
def get_studio_shot_manager():
    return StudioShotManager(_repo, _studio_validator, _prompts, _llm)

def get_studio_generation():
    return StudioGenerationService(_repo, _studio_validator, _comfy, _llm, _prompts, get_studio_shot_manager())

def get_studio_assets():
    return StudioAssetService(_repo, _studio_validator, get_studio_shot_manager())

# Chat Services
def get_chat_conversation():
    return ChatConversationService(_llm, _repo, _proj_validator, _cont_validator, get_project_working_copy(), _prompts)

def get_chat_draft():
    return ChatDraftService(_llm, _repo, _proj_validator, _cont_validator, get_project_working_copy(), _prompts)

def get_system_vitals():
    return _vitals_service
