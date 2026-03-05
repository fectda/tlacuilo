from fastapi import APIRouter, Depends, Response
from app.api.deps import get_project_publish
from app.services.project.publish import ProjectPublishService

router = APIRouter()

@router.post("/{collection}/{slug}/promote")
async def promote_project(collection: str, slug: str, pub: ProjectPublishService = Depends(get_project_publish)):
    return await pub.promote_to_portfolio(collection, slug)

@router.post("/{collection}/{slug}/publish")
async def publish_project_remote(collection: str, slug: str, pub: ProjectPublishService = Depends(get_project_publish)):
    return pub.publish_global(collection, slug)

@router.post("/{collection}/{slug}/forget")
async def forget_project(collection: str, slug: str, pub: ProjectPublishService = Depends(get_project_publish)):
    pub.forget_project_memory(collection, slug)
    return Response(status_code=204)

@router.post("/{collection}/{slug}/resurrect")
async def resurrect_project(collection: str, slug: str, pub: ProjectPublishService = Depends(get_project_publish)):
    pub.resurrect_portfolio_file(collection, slug)
    return Response(status_code=200)
