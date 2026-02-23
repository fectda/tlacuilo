from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Response
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

from app.repositories.project_repository import ProjectRepository
from app.clients.llm.ollama import OllamaClient
from app.clients.comfyui import ComfyUIClient
from app.services.studio_service import StudioService
from app.services.prompt_service import PromptService

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Dependencies ---

def get_repository():
    return ProjectRepository()

def get_llm():
    return OllamaClient()

def get_comfy():
    return ComfyUIClient()

def get_prompts():
    return PromptService()

def get_studio_service(
    repo: ProjectRepository = Depends(get_repository),
    llm: OllamaClient = Depends(get_llm),
    comfy: ComfyUIClient = Depends(get_comfy),
    prompts: PromptService = Depends(get_prompts),
):
    return StudioService(repo, llm, comfy, prompts)

# --- Models ---

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

class ApproveShotRequest(BaseModel):
    filename: str

# --- Endpoints ---

# 1. Shot Management

@router.post("/{collection}/{slug}/studio/suggest", status_code=200)
async def suggest_shots(
    collection: str, slug: str,
    service: StudioService = Depends(get_studio_service)
):
    """POST /api/{collection}/{slug}/studio/suggest — Suggest and persist shots using LLM."""
    try:
        shots = await service.suggest_shots(collection, slug)
        return shots
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error suggesting shots: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{collection}/{slug}/studio/shots", status_code=200)
def list_shots(
    collection: str, slug: str,
    service: StudioService = Depends(get_studio_service)
):
    """GET /api/{collection}/{slug}/studio/shots — List all shots."""
    return service.list_shots(collection, slug)


@router.post("/{collection}/{slug}/studio/shots", status_code=201)
def create_shot(
    collection: str, slug: str,
    body: CreateShotRequest,
    service: StudioService = Depends(get_studio_service)
):
    """POST /api/{collection}/{slug}/studio/shots — Create a manual shot slot."""
    try:
        return service.create_shot(
            collection, slug,
            title=body.title,
            description=body.description,
            shot_type=body.type,
            focus=body.focus,
            atmosphere=body.atmosphere
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating shot: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{collection}/{slug}/studio/shots/{shot_id}", status_code=200)
def get_shot(
    collection: str, slug: str, shot_id: str,
    service: StudioService = Depends(get_studio_service)
):
    """GET /api/{collection}/{slug}/studio/shots/{shot_id} — Get shot detail."""
    try:
        return service.get_shot(collection, slug, shot_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{collection}/{slug}/studio/shots/{shot_id}", status_code=200)
def update_shot(
    collection: str, slug: str, shot_id: str,
    body: UpdateShotRequest,
    service: StudioService = Depends(get_studio_service)
):
    """PATCH /api/{collection}/{slug}/studio/shots/{shot_id} — Update shot metadata."""
    try:
        return service.update_shot(collection, slug, shot_id, body.model_dump(exclude_none=True))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{collection}/{slug}/studio/shots/{shot_id}", status_code=204)
def delete_shot(
    collection: str, slug: str, shot_id: str,
    service: StudioService = Depends(get_studio_service)
):
    """DELETE /api/{collection}/{slug}/studio/shots/{shot_id} — Delete a shot."""
    try:
        service.delete_shot(collection, slug, shot_id)
        return Response(status_code=204)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

# 2. Generation Pipeline

@router.post("/{collection}/{slug}/studio/shots/{shot_id}/upload", status_code=202)
async def upload_and_generate(
    collection: str, slug: str, shot_id: str,
    file: UploadFile = File(...),
    service: StudioService = Depends(get_studio_service)
):
    """POST /api/{collection}/{slug}/studio/shots/{shot_id}/upload — Upload + generate."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are accepted.")
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image exceeds 10MB limit.")
    try:
        return await service.upload_and_generate(collection, slug, shot_id, contents)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in upload_and_generate: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{collection}/{slug}/studio/shots/{shot_id}/correct", status_code=202)
async def correct_shot(
    collection: str, slug: str, shot_id: str,
    body: CorrectShotRequest,
    service: StudioService = Depends(get_studio_service)
):
    """POST /api/{collection}/{slug}/studio/shots/{shot_id}/correct — Correction cycle."""
    try:
        return await service.correct_shot(collection, slug, shot_id, body.instruction)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in correct_shot: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{collection}/{slug}/studio/shots/{shot_id}/approve", status_code=200)
def approve_shot(
    collection: str, slug: str, shot_id: str,
    body: ApproveShotRequest,
    service: StudioService = Depends(get_studio_service)
):
    """POST /api/{collection}/{slug}/studio/shots/{shot_id}/approve — Approve an image."""
    try:
        return service.approve_shot(collection, slug, shot_id, body.filename)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# 3. ComfyUI Status Polling

@router.get("/{collection}/{slug}/studio/shots/{shot_id}/status", status_code=200)
async def poll_generation_status(
    collection: str, slug: str, shot_id: str,
    service: StudioService = Depends(get_studio_service),
    comfy: ComfyUIClient = Depends(get_comfy),
    repo: ProjectRepository = Depends(get_repository)
):
    """GET /api/{collection}/{slug}/studio/shots/{shot_id}/status — Poll ComfyUI status."""
    meta = service.get_shot(collection, slug, shot_id)
    prompt_id = meta.get("prompt_id")
    if not prompt_id:
        return {"status": meta.get("status", "pending_upload")}

    try:
        comfy_status = await comfy.get_status(prompt_id)
        if comfy_status["status"] == "completed":
            # Download and save generated images
            shot_dir = service._shot_dir(collection, slug, shot_id)
            outputs = comfy_status.get("outputs", {})
            saved = []
            for node_id, node_output in outputs.items():
                for img in node_output.get("images", []):
                    fn = img["filename"]
                    dest = shot_dir / f"generated_{fn}"
                    await comfy.download_image(fn, dest)
                    saved.append(dest.name)

            # Update status to 'generated'
            meta["status"] = "generated"
            service._save_shot_metadata(collection, slug, shot_id, meta)
            return {"status": "generated", "files": saved}

        return comfy_status
    except Exception as e:
        logger.error(f"Error polling ComfyUI: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
