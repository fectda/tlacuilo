from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.services.project_service import ProjectService
from app.services.chat_service import ChatService

router = APIRouter()

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

class DraftPersistRequest(BaseModel):
    content: str

def get_project_service():
    return ProjectService()

def get_chat_service():
    return ChatService()

# --- Sincronización de Contexto ---

@router.get("/{collection}/{slug}/content", response_model=Dict[str, Any])
async def get_project_content(collection: str, slug: str, service: ProjectService = Depends(get_project_service)):
    """
    GET .../content: Obtiene el contenido del documento.
    Responsabilidad: Devolver el texto del archivo .md y su estado.
    """
    # TODO: Refactor service to allow non-mutating read (no hydration) if required strict adherence
    # For now, we use get_working_copy which handles precedence logic.
    data = service.get_working_copy(collection, slug)
    if "error" in data:
         raise HTTPException(status_code=data.get("status_code", 400), detail=data["error"])
    
    return {
        "content": data.get("content", ""),
        "status": data.get("state", {}).get("doc_status", "borrador"),
        "source": data.get("source"), # Debug info
        "is_working_copy_active": data.get("state", {}).get("is_working_copy_active", False)
    }

@router.get("/{collection}/{slug}/chat/history", response_model=Dict[str, Any])
async def get_chat_history(collection: str, slug: str, service: ProjectService = Depends(get_project_service)):
    """
    GET .../chat/history: Obtiene el historial de conversación.
    """
    messages = service.get_chat_history_safe(collection, slug)
    return {"messages": messages}

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



@router.post("/{collection}/{slug}/init")
async def init_session(collection: str, slug: str, 
                       chat_service: ChatService = Depends(get_chat_service),
                       project_service: ProjectService = Depends(get_project_service)):
    """
    POST .../init: Arranque de Sesión (Trigger).
    Responsabilidad: Evaluar estado y, si es necesario, construir el Contexto Cero.
    """
    try:
        # 1. Recuperar historial
        history = project_service.get_chat_history_raw(collection, slug)
        
        # 2. Evaluar Escenarios de Negocio
        if not history:
            # Escenario 1: Lienzo en Blanco
            # Delegamos a chat_service la construcción del Contexto Cero y llamada inicial
            response = await chat_service.initialize_new_project(collection, slug)
            return response

        last_msg = history[-1]
        
        if last_msg["role"] == "user":
            # Escenario 2: Deuda Técnica (Último msg User)
            # Llamamos a message sin input nuevo para procesar pendiente
            # Pasamos un mensaje de sistema interno si es necesario, o simplemente disparamos el re-intento
            return await chat_service.process_pending_debt(collection, slug)
            
        if last_msg["role"] == "assistant":
            # Escenario 3: Esperando al Humano
            from fastapi import Response
            return Response(status_code=204)

    except Exception as e:
        logger.error(f"Error in /init for {slug}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{collection}/{slug}/message", response_model=MessageResponse)
async def send_message(collection: str, slug: str, request: MessageRequest, 
                       chat_service: ChatService = Depends(get_chat_service),
                       project_service: ProjectService = Depends(get_project_service)):
    """
    POST .../message: Mensajería Transaccional (Context-Aware).
    Responsabilidad: Recibir un mensaje, persistirlo, obtener respuesta de la IA y persistir respuesta.
    """
    try:
        # Activar working copy flag obligatoriamente
        project_service.activate_session(collection, slug)
        
        # Procesar mensaje
        response = await chat_service.process_message(
            collection, 
            slug, 
            request.content, 
            system_only=request.system_only,
            response_system_only=request.response_system_only
        )
        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in /message for {slug}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

import logging
logger = logging.getLogger(__name__)

@router.post("/{collection}/{slug}/draft")
async def generate_draft(collection: str, slug: str, chat_service: ChatService = Depends(get_chat_service)):
    """
    POST .../draft: Generación de Borrador (Propuesta).
    """
    try:
        content = await chat_service.generate_draft(collection, slug)
        return {"content": content, "status": "draft"}
    except Exception as e:
        logger.error(f"Error generating draft for {slug}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Validación, Persistencia y Promoción ---

@router.post("/{collection}/{slug}/persist")
async def persist_content(collection: str, slug: str, request: ContentUpdate, service: ProjectService = Depends(get_project_service)):
    """
    POST .../persist: Autorización de Cambios (Persistencia).
    """
    result = service.save_working_copy(collection, slug, request.content)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    return result

@router.post("/{collection}/{slug}/promote")
async def promote_project(collection: str, slug: str, service: ProjectService = Depends(get_project_service)):
    """
    POST .../promote: Promoción al Portafolio (Finalización).
    """
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
