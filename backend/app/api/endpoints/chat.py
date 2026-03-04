from fastapi import APIRouter, Depends, Response
from typing import Optional
from pydantic import BaseModel

from app.api.deps import get_chat_conversation, get_chat_draft, get_repository
from app.services.chat.conversation import ChatConversationService
from app.services.chat.draft import ChatDraftService
from app.repositories.project_repository import ProjectRepository

router = APIRouter()

class MessageRequest(BaseModel):
    content: str
    system_only: Optional[bool] = False
    response_system_only: Optional[bool] = False
    is_note: Optional[bool] = False

class MessageResponse(BaseModel):
    role: str
    content: str
    timestamp: str

class TranslationDraftRequest(BaseModel):
    from_scratch: bool
    instruction: Optional[str] = None
    current_draft: Optional[str] = None

@router.get("/{collection}/{slug}/chat/history")
async def get_chat_history(collection: str, slug: str, chat: ChatConversationService = Depends(get_chat_conversation)):
    return await chat.get_history(collection, slug)

@router.post("/{collection}/{slug}/init")
async def init_session(collection: str, slug: str, chat: ChatConversationService = Depends(get_chat_conversation), repo: ProjectRepository = Depends(get_repository)):
    history = repo.get_chat_history(repo.get_project_dir(collection, slug))
    if not history: return await chat.initialize_new_project(collection, slug)
    last_msg = history[-1]
    if last_msg["role"] == "user" and not last_msg.get("is_note", False): 
        return await chat.process_message(collection, slug, last_msg["content"], system_only=True)
    return Response(status_code=204)

@router.post("/{collection}/{slug}/message")
async def send_message(collection: str, slug: str, request: MessageRequest, 
                       chat: ChatConversationService = Depends(get_chat_conversation),
                       response: Response = None):
    res = await chat.process_message(collection, slug, request.content, request.system_only, request.response_system_only, request.is_note)
    if request.is_note:
        response.status_code = 202
    return res

@router.post("/{collection}/{slug}/draft")
async def generate_draft(collection: str, slug: str, draft: ChatDraftService = Depends(get_chat_draft)):
    return {"content": await draft.generate_draft(collection, slug), "status": "draft"}

@router.post("/{collection}/{slug}/translate/draft")
async def translate_draft(collection: str, slug: str, request: TranslationDraftRequest, draft: ChatDraftService = Depends(get_chat_draft)):
    return {"content": await draft.process_translation_draft(collection, slug, request.from_scratch, request.instruction, request.current_draft)}
