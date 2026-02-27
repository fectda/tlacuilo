from fastapi import APIRouter, Depends, Response
from app.api.deps import get_project_publish
from app.services.project.publish import ProjectPublishService

router = APIRouter()

@router.post("/{collection}/{slug}/promote")
async def promote_project(collection: str, slug: str, pub: ProjectPublishService = Depends(get_project_publish)):
    return pub.publish_project(collection, slug)

@router.post("/{collection}/{slug}/publish")
async def publish_project_remote(collection: str, slug: str, pub: ProjectPublishService = Depends(get_project_publish)):
    return pub.publish_to_remote(collection, slug)

@router.post("/{collection}/{slug}/forget")
async def forget_project(collection: str, slug: str, pub: ProjectPublishService = Depends(get_project_publish)):
    pub.delete_project(collection, slug)
    return Response(status_code=204)

@router.post("/{collection}/{slug}/resurrect")
async def resurrect_project(collection: str, slug: str, pub: ProjectPublishService = Depends(get_project_publish)):
    pub.resurrect_project(collection, slug)
    return Response(status_code=200)
