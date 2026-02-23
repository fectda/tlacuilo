from fastapi import APIRouter, HTTPException, Depends, Body, Response
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

from app.core.config import settings
from app.repositories.project_repository import ProjectRepository
from app.clients.llm.ollama import OllamaClient
from app.services.project_manager import ProjectManager
from app.services.chat_orchestrator import ChatOrchestrator
from app.services.prompt_service import PromptService
from app.services.validation_service import ValidationService

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Dependencies ---

def get_repository():
    return ProjectRepository()

def get_validator():
    return ValidationService()

def get_prompts():
    return PromptService()

def get_llm():
    return OllamaClient()

def get_project_manager(repo: ProjectRepository = Depends(get_repository), 
                        validator: ValidationService = Depends(get_validator)):
    return ProjectManager(repo, validator)

def get_chat_orchestrator(llm: OllamaClient = Depends(get_llm),
                         manager: ProjectManager = Depends(get_project_manager),
                         prompts: PromptService = Depends(get_prompts),
                         validator: ValidationService = Depends(get_validator),
                         repo: ProjectRepository = Depends(get_repository)):
    return ChatOrchestrator(llm, manager, prompts, validator, repo)

# --- Models ---

class MessageRequest(BaseModel):
    content: str
    system_only: Optional[bool] = False
    response_system_only: Optional[bool] = False

class MessageResponse(BaseModel):
    role: str
    content: str
    timestamp: str

class ContentUpdate(BaseModel):
    content: str

class TranslationDraftRequest(BaseModel):
    from_scratch: bool
    instruction: Optional[str] = None
    current_draft: Optional[str] = None

# --- Sincronización de Contexto ---

@router.get("/{collection}/{slug}/content", response_model=Dict[str, Any])
async def get_project_content(collection: str, slug: str, manager: ProjectManager = Depends(get_project_manager)):
    data = manager.get_working_copy(collection, slug)
    if "error" in data:
         raise HTTPException(status_code=data.get("status_code", 400), detail=data["error"])
    
    return {
        "content": data.get("content", ""),
        "status": data.get("state", {}).get("doc_status", "borrador"),
        "source": data.get("source"),
        "is_working_copy_active": data.get("state", {}).get("is_working_copy_active", False)
    }

@router.get("/{collection}/{slug}/chat/history")
async def get_chat_history(collection: str, slug: str, repo: ProjectRepository = Depends(get_repository)):
    project_dir = repo.get_project_dir(collection, slug)
    history = repo.get_chat_history(project_dir)
    # Filter system messages for UI safety as before
    safe_history = [m for m in history if not m.get("system_only")]
    return {"messages": safe_history}

@router.post("/{collection}/{slug}/revert")
async def revert_project(collection: str, slug: str, manager: ProjectManager = Depends(get_project_manager)):
    result = manager.revert_working_copy(collection, slug)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    return result

# --- Ciclo de Entrevista ---

@router.post("/{collection}/{slug}/init")
async def init_session(collection: str, slug: str, 
                       orchestrator: ChatOrchestrator = Depends(get_chat_orchestrator),
                       repo: ProjectRepository = Depends(get_repository)):
    try:
        project_dir = repo.get_project_dir(collection, slug)
        history = repo.get_chat_history(project_dir)
        
        if not history:
            return await orchestrator.initialize_new_project(collection, slug)

        last_msg = history[-1]
        if last_msg["role"] == "user":
            return await orchestrator.process_message(collection, slug, last_msg["content"], system_only=True)
            
        return Response(status_code=204)

    except Exception as e:
        logger.error(f"Error in /init for {slug}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{collection}/{slug}/message", response_model=MessageResponse)
async def send_message(collection: str, slug: str, request: MessageRequest, 
                       orchestrator: ChatOrchestrator = Depends(get_chat_orchestrator)):
    try:
        return await orchestrator.process_message(
            collection, slug, request.content, 
            system_only=request.system_only,
            response_system_only=request.response_system_only
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in /message for {slug}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{collection}/{slug}/draft")
async def generate_draft(collection: str, slug: str, orchestrator: ChatOrchestrator = Depends(get_chat_orchestrator)):
    try:
        content = await orchestrator.generate_draft(collection, slug)
        return {"content": content, "status": "draft"}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error generating draft for {slug}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Validación, Persistencia y Promoción ---

@router.post("/{collection}/{slug}/persist")
async def persist_content(collection: str, slug: str, request: ContentUpdate, manager: ProjectManager = Depends(get_project_manager)):
    result = manager.save_working_copy(collection, slug, request.content)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    return result

@router.post("/{collection}/{slug}/promote")
async def promote_project(collection: str, slug: str, manager: ProjectManager = Depends(get_project_manager)):
    result = manager.publish_project(collection, slug)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    return result

# --- English Flow ---

@router.get("/{collection}/{slug}/translate")
async def get_translation(collection: str, slug: str, manager: ProjectManager = Depends(get_project_manager)):
    """Recupera el contenido en inglés para traducción (Sección D)."""
    return manager.get_translation_copy(collection, slug)

@router.post("/{collection}/{slug}/translate/draft")
async def translate_draft(collection: str, slug: str, request: TranslationDraftRequest,
                          orchestrator: ChatOrchestrator = Depends(get_chat_orchestrator)):
    """Genera o refina un borrador en inglés (Sección D)."""
    try:
        content = await orchestrator.process_translation_draft(
            collection, slug, 
            from_scratch=request.from_scratch,
            instruction=request.instruction,
            current_draft=request.current_draft
        )
        return {"content": content}
    except Exception as e:
        logger.error(f"Error in translate/draft for {slug}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{collection}/{slug}/translate/persist")
async def persist_translation(collection: str, slug: str, request: ContentUpdate, 
                              manager: ProjectManager = Depends(get_project_manager)):
    """Persiste el borrador traducido (Sección D)."""
    result = manager.save_translation_copy(collection, slug, request.content)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    return Response(status_code=200)

# --- Actions (Forget/Resurrect) ---

@router.post("/{collection}/{slug}/forget")
async def forget_project(collection: str, slug: str, manager: ProjectManager = Depends(get_project_manager)):
    manager.delete_project(collection, slug)
    return Response(status_code=204)
