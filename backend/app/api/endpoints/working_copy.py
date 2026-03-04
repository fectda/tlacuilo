from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from app.api.deps import get_project_working_copy
from app.services.project.working_copy import ProjectWorkingCopyService

router = APIRouter()

class ContentUpdate(BaseModel):
    content: str

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

@router.post("/{collection}/{slug}/persist")
async def persist_content(collection: str, slug: str, request: ContentUpdate, wc: ProjectWorkingCopyService = Depends(get_project_working_copy)):
    return await wc.save_working_copy(collection, slug, request.content)

@router.get("/{collection}/{slug}/translate")
async def get_translation(collection: str, slug: str, wc: ProjectWorkingCopyService = Depends(get_project_working_copy)):
    return wc.get_translation_copy(collection, slug)

@router.post("/{collection}/{slug}/translate/persist")
async def persist_translation(collection: str, slug: str, request: ContentUpdate, wc: ProjectWorkingCopyService = Depends(get_project_working_copy)):
    await wc.save_translation_copy(collection, slug, request.content)
    return Response(status_code=200)
