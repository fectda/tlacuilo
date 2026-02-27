from fastapi import APIRouter, Depends, Body, Response
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.api.deps import (
    get_project_working_copy, get_project_publish, 
    get_chat_conversation, get_chat_draft, get_repository
)
from app.services.project.working_copy import ProjectWorkingCopyService
from app.services.project.publish import ProjectPublishService
from app.services.chat.conversation import ChatConversationService
from app.services.chat.draft import ChatDraftService
from app.repositories.project_repository import ProjectRepository

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

class TranslationDraftRequest(BaseModel):
    from_scratch: bool
    instruction: Optional[str] = None
    current_draft: Optional[str] = None

@router.get("/{collection}/{slug}/content")
async def get_project_content(collection: str, slug: str, wc: ProjectWorkingCopyService = Depends(get_project_working_copy)):
    data = wc.get_working_copy(collection, slug)
    return {
        "content": data.get("content", ""),
        "status": data.get("state", {}).get("doc_status", "borrador"),
        "source": data.get("source"),
        "is_working_copy_active": data.get("state", {}).get("is_working_copy_active", False)
    }

@router.post("/{collection}/{slug}/revert")
async def revert_project(collection: str, slug: str, wc: ProjectWorkingCopyService = Depends(get_project_working_copy)):
    return wc.revert_working_copy(collection, slug)

@router.post("/{collection}/{slug}/init")
async def init_session(collection: str, slug: str, chat: ChatConversationService = Depends(get_chat_conversation), repo: ProjectRepository = Depends(get_repository)):
    history = repo.get_chat_history(repo.get_project_dir(collection, slug))
    if not history: return await chat.initialize_new_project(collection, slug)
    last_msg = history[-1]
    if last_msg["role"] == "user": return await chat.process_message(collection, slug, last_msg["content"], system_only=True)
    return Response(status_code=204)

@router.post("/{collection}/{slug}/message", response_model=MessageResponse)
async def send_message(collection: str, slug: str, request: MessageRequest, chat: ChatConversationService = Depends(get_chat_conversation)):
    return await chat.process_message(collection, slug, request.content, request.system_only, request.response_system_only)

@router.post("/{collection}/{slug}/draft")
async def generate_draft(collection: str, slug: str, draft: ChatDraftService = Depends(get_chat_draft)):
    return {"content": await draft.generate_draft(collection, slug), "status": "draft"}

@router.post("/{collection}/{slug}/persist")
async def persist_content(collection: str, slug: str, request: ContentUpdate, wc: ProjectWorkingCopyService = Depends(get_project_working_copy)):
    return wc.save_working_copy(collection, slug, request.content)

@router.post("/{collection}/{slug}/promote")
async def promote_project(collection: str, slug: str, pub: ProjectPublishService = Depends(get_project_publish)):
    return pub.publish_project(collection, slug)

@router.get("/{collection}/{slug}/translate")
async def get_translation(collection: str, slug: str, wc: ProjectWorkingCopyService = Depends(get_project_working_copy)):
    return wc.get_translation_copy(collection, slug)

@router.post("/{collection}/{slug}/translate/draft")
async def translate_draft(collection: str, slug: str, request: TranslationDraftRequest, draft: ChatDraftService = Depends(get_chat_draft)):
    return {"content": await draft.process_translation_draft(collection, slug, request.from_scratch, request.instruction, request.current_draft)}

@router.post("/{collection}/{slug}/translate/persist")
async def persist_translation(collection: str, slug: str, request: ContentUpdate, wc: ProjectWorkingCopyService = Depends(get_project_working_copy)):
    wc.save_translation_copy(collection, slug, request.content)
    return Response(status_code=200)

@router.post("/{collection}/{slug}/forget")
async def forget_project(collection: str, slug: str, pub: ProjectPublishService = Depends(get_project_publish)):
    pub.delete_project(collection, slug)
    return Response(status_code=204)
