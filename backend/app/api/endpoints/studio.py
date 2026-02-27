from fastapi import APIRouter, Depends, UploadFile, File, Response
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.api.deps import get_studio_shot_manager, get_studio_generation, get_studio_assets
from app.services.studio.shot_manager import StudioShotManager
from app.services.studio.generation import StudioGenerationService
from app.services.studio.assets import StudioAssetService

router = APIRouter()

class CreateShotRequest(BaseModel):
    title: str
    description: str
    type: Optional[str] = "macro"
    focus: str
    atmosphere: str

class UpdateShotRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    focus: Optional[str] = None
    atmosphere: Optional[str] = None

class CorrectShotRequest(BaseModel):
    instruction: str
    comfly_id: str

class ApproveShotRequest(BaseModel):
    comfly_id: str

# 1. Shot Management

@router.post("/{collection}/{slug}/studio/suggest")
async def suggest_shots(collection: str, slug: str, sm: StudioShotManager = Depends(get_studio_shot_manager)):
    return await sm.suggest_shots(collection, slug)

@router.get("/{collection}/{slug}/studio/shots")
def list_shots(collection: str, slug: str, sm: StudioShotManager = Depends(get_studio_shot_manager)):
    return sm.list_shots(collection, slug)

@router.post("/{collection}/{slug}/studio/shots", status_code=201)
def create_shot(collection: str, slug: str, body: CreateShotRequest, sm: StudioShotManager = Depends(get_studio_shot_manager)):
    return sm.create_shot(collection, slug, **body.model_dump())

@router.get("/{collection}/{slug}/studio/shots/{shot_id}")
def get_shot(collection: str, slug: str, shot_id: str, sm: StudioShotManager = Depends(get_studio_shot_manager)):
    return sm.get_shot(collection, slug, shot_id)

@router.get("/{collection}/{slug}/studio/shots/{shot_id}/image/{comfly_id}")
def get_image(collection: str, slug: str, shot_id: str, comfly_id: str, assets: StudioAssetService = Depends(get_studio_assets)):
    return assets.get_image(collection, slug, shot_id, comfly_id)

@router.patch("/{collection}/{slug}/studio/shots/{shot_id}")
def update_shot(collection: str, slug: str, shot_id: str, body: UpdateShotRequest, sm: StudioShotManager = Depends(get_studio_shot_manager)):
    return sm.update_shot(collection, slug, shot_id, body.model_dump(exclude_none=True))

@router.delete("/{collection}/{slug}/studio/shots/{shot_id}", status_code=204)
def delete_shot(collection: str, slug: str, shot_id: str, sm: StudioShotManager = Depends(get_studio_shot_manager)):
    sm.delete_shot(collection, slug, shot_id)
    return Response(status_code=204)

# 2. Generation Pipeline

@router.post("/{collection}/{slug}/studio/shots/{shot_id}/upload", status_code=202)
async def upload_and_generate(collection: str, slug: str, shot_id: str, file: UploadFile = File(...), gen: StudioGenerationService = Depends(get_studio_generation)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise ValueError("Only images accepted.")
    return await gen.upload_and_generate(collection, slug, shot_id, await file.read())

@router.post("/{collection}/{slug}/studio/shots/{shot_id}/correct", status_code=202)
async def correct_shot(collection: str, slug: str, shot_id: str, body: CorrectShotRequest, gen: StudioGenerationService = Depends(get_studio_generation)):
    return await gen.correct_shot(collection, slug, shot_id, body.instruction, body.comfly_id)

@router.post("/{collection}/{slug}/studio/shots/{shot_id}/approve")
def approve_shot(collection: str, slug: str, shot_id: str, body: ApproveShotRequest, assets: StudioAssetService = Depends(get_studio_assets)):
    return assets.approve_shot(collection, slug, shot_id, body.comfly_id)

@router.delete("/{collection}/{slug}/studio/shots/{shot_id}/image/{comfly_id}")
def delete_variant(collection: str, slug: str, shot_id: str, comfly_id: str, assets: StudioAssetService = Depends(get_studio_assets)):
    return assets.delete_variant(collection, slug, shot_id, comfly_id)

@router.get("/{collection}/{slug}/studio/shots/{shot_id}/status")
async def poll_status(collection: str, slug: str, shot_id: str, gen: StudioGenerationService = Depends(get_studio_generation)):
    return await gen.poll_status(collection, slug, shot_id)
