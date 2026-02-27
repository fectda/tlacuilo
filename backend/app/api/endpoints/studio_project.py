from fastapi import APIRouter, Depends
from typing import Optional
from pydantic import BaseModel

from app.api.deps import get_studio_shot_manager
from app.services.studio.shot_manager import StudioShotManager

router = APIRouter()

class CreateShotRequest(BaseModel):
    title: str
    description: str
    type: Optional[str] = "macro"
    focus: str
    atmosphere: str

@router.post("/{collection}/{slug}/studio/suggest")
async def suggest_shots(collection: str, slug: str, sm: StudioShotManager = Depends(get_studio_shot_manager)):
    return await sm.suggest_shots(collection, slug)

@router.get("/{collection}/{slug}/studio/shots")
def list_shots(collection: str, slug: str, sm: StudioShotManager = Depends(get_studio_shot_manager)):
    return sm.list_shots(collection, slug)

@router.post("/{collection}/{slug}/studio/shots", status_code=201)
def create_shot(collection: str, slug: str, body: CreateShotRequest, sm: StudioShotManager = Depends(get_studio_shot_manager)):
    return sm.create_shot(collection, slug, **body.model_dump())
