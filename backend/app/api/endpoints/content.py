from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.services.project_service import ProjectService
from app.services.chat_service import ChatService

router = APIRouter()

class MessageRequest(BaseModel):
    message: str
    mode: str = "interview"

class ContentUpdate(BaseModel):
    content: str

class DraftPersistRequest(BaseModel):
    content: str

def get_project_service():
    return ProjectService()

def get_chat_service():
    return ChatService()

# --- Sincronización de Contexto ---

@router.get("/{collection}/{slug}", response_model=Dict[str, Any])
async def get_project_content(collection: str, slug: str, service: ProjectService = Depends(get_project_service)):
    """
    GET /api/{collection}/{slug}: Inicializa la sesión de trabajo.
    Aplica las Reglas de Precedencia para cargar el MD correcto.
    """
    result = service.get_working_copy(collection, slug)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    return result

@router.post("/{collection}/{slug}/revert", response_model=Dict[str, Any])
async def revert_project(collection: str, slug: str, service: ProjectService = Depends(get_project_service)):
    """
    POST .../revert: Descarta el trabajo local actual y sobreescribe con la versión del Portafolio.
    """
    result = service.revert_working_copy(collection, slug)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    return result

# --- Ciclo de Entrevista ---

@router.post("/{collection}/{slug}/start", response_model=List[Dict[str, Any]])
async def start_chat(collection: str, slug: str, chat_service: ChatService = Depends(get_chat_service)):
    """Reiniciar chat_history.json para el proyecto."""
    try:
        return await chat_service.start_interview(collection, slug)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{collection}/{slug}/message", response_model=List[Dict[str, Any]])
async def send_message(collection: str, slug: str, request: MessageRequest, 
                       chat_service: ChatService = Depends(get_chat_service),
                       project_service: ProjectService = Depends(get_project_service)):
    """Enviar mensaje al LLM."""
    try:
        # Activate working copy flag on interaction
        project_service.update_project_state(collection, slug, {"is_working_copy_active": True})
        return await chat_service.send_message(collection, slug, request.message, request.mode)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{collection}/{slug}/draft", response_model=Dict[str, Any])
async def generate_draft(collection: str, slug: str, chat_service: ChatService = Depends(get_chat_service)):
    """Generar propuesta de MD (No persistente)."""
    try:
        content = await chat_service.generate_draft(collection, slug)
        return {"content": content, "status": "propuesta_generada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Validación y Persistencia ---

@router.post("/{collection}/{slug}/persist", response_model=Dict[str, Any])
async def persist_draft(collection: str, slug: str, request: DraftPersistRequest, service: ProjectService = Depends(get_project_service)):
    """Guardar la propuesta del agente en el .md local."""
    result = service.save_working_copy(collection, slug, request.content)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    return result

@router.put("/{collection}/{slug}", response_model=Dict[str, Any])
async def save_manual(collection: str, slug: str, request: ContentUpdate, service: ProjectService = Depends(get_project_service)):
    """Guardado manual del usuario con validación."""
    result = service.save_working_copy(collection, slug, request.content)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    return result

@router.post("/{collection}/{slug}/publish", response_model=Dict[str, Any])
async def publish_project(collection: str, slug: str, service: ProjectService = Depends(get_project_service)):
    """Mueve la Copia de Trabajo validada al Portafolio."""
    result = service.publish_project(collection, slug)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    return result

# --- English Flow (Localización) ---

@router.post("/{collection}/{slug}/translate", response_model=Dict[str, Any])
async def translate_project(collection: str, slug: str, 
                            chat_service: ChatService = Depends(get_chat_service),
                            project_service: ProjectService = Depends(get_project_service)):
    """Inicia Localización: Genera propuesta basada en el MD publicado."""
    # Get current content (ideally from portfolio if published)
    content_data = project_service.get_working_copy(collection, slug)
    source_content = content_data["content"]
    
    try:
        en_content = await chat_service.translate_proposal(collection, slug, source_content)
        # Save to local .en.md
        project_service.save_translation_copy(collection, slug, en_content)
        return {"content": en_content, "status": "translation_proposed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{collection}/{slug}/translate", response_model=Dict[str, Any])
async def get_translation(collection: str, slug: str, service: ProjectService = Depends(get_project_service)):
    """Lee la versión actual de la Copia de Trabajo en inglés."""
    result = service.get_translation_copy(collection, slug)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 404), detail=result["error"])
    return result

@router.post("/{collection}/{slug}/translate/refine", response_model=Dict[str, Any])
async def refine_translation(collection: str, slug: str, instruction: str = Body(..., embed=True),
                             chat_service: ChatService = Depends(get_chat_service),
                             project_service: ProjectService = Depends(get_project_service)):
    """Refinamiento Interactivo de la traducción."""
    current_en = project_service.get_translation_copy(collection, slug)
    if "error" in current_en:
        raise HTTPException(status_code=404, detail="No translation to refine")
        
    try:
        new_en = await chat_service.refine_translation(collection, slug, current_en["content"], instruction)
        project_service.save_translation_copy(collection, slug, new_en)
        return {"content": new_en, "status": "translation_refined"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{collection}/{slug}/translate", response_model=Dict[str, Any])
async def save_manual_translation(collection: str, slug: str, request: ContentUpdate, service: ProjectService = Depends(get_project_service)):
    """Edición manual de la versión en inglés."""
    result = service.save_translation_copy(collection, slug, request.content)
    return result

@router.post("/{collection}/{slug}/publish-en", response_model=Dict[str, Any])
async def publish_translation(collection: str, slug: str, service: ProjectService = Depends(get_project_service)):
    """Envía la versión en inglés al Portafolio."""
    result = service.publish_translation(collection, slug)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    return result

# --- Actions (Forget/Resurrect) ---

@router.post("/{collection}/{slug}/forget", response_model=Dict[str, Any])
async def forget_project(collection: str, slug: str, service: ProjectService = Depends(get_project_service)):
    """Elimina permanentemente la memoria local."""
    result = service.delete_project(collection, slug)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    return result

@router.post("/{collection}/{slug}/resurrect", response_model=Dict[str, Any])
async def resurrect_project(collection: str, slug: str, service: ProjectService = Depends(get_project_service)):
    """Restaura el archivo desde la memoria local hacia el portafolio."""
    result = service.resurrect_project(collection, slug)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    return result
