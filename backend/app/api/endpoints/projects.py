from fastapi import APIRouter, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.api.deps import get_project_discovery, get_project_working_copy
from app.services.project.discovery import ProjectDiscoveryService
from app.services.project.working_copy import ProjectWorkingCopyService

router = APIRouter()

class CreateProjectRequest(BaseModel):
    name: str
    collection: str = "bits"
    slug: Optional[str] = None

@router.get("/", response_model=Dict[str, List[Dict[str, Any]]])
async def list_projects(discovery: ProjectDiscoveryService = Depends(get_project_discovery)):
    return discovery.list_projects()

@router.post("/", response_model=Dict[str, Any])
async def create_project(request: CreateProjectRequest, wc: ProjectWorkingCopyService = Depends(get_project_working_copy)):
    return wc.create_project(name=request.name, collection=request.collection, slug=request.slug)
