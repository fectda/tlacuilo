from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.services.project_service import ProjectService

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter()

class CreateProjectRequest(BaseModel):
    name: str
    collection: str = "bits"
    slug: Optional[str] = None

def get_project_service():
    return ProjectService()

@router.get("/", response_model=Dict[str, List[Dict[str, Any]]])
async def list_projects(service: ProjectService = Depends(get_project_service)):
    """
    List all available projects (content collections).
    Executes the Discovery Cycle.
    """
    try:
        return service.list_projects()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Dict[str, Any])
async def create_project(request: CreateProjectRequest, service: ProjectService = Depends(get_project_service)):
    """
    Create a new project scaffolding.
    """
    if not request.name:
        raise HTTPException(status_code=400, detail="Project name is required")
        
    result = service.create_project(request.name, request.collection, request.slug)
    
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
        
        
    return result

@router.post("/forget/{collection}/{slug}", response_model=Dict[str, Any])
async def forget_project(collection: str, slug: str, service: ProjectService = Depends(get_project_service)):
    """
    Forget Action: Permanent deletion of local memory.
    """
    result = service.delete_project(collection, slug)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    return result

@router.post("/resurrect/{collection}/{slug}", response_model=Dict[str, Any])
async def resurrect_project(collection: str, slug: str, service: ProjectService = Depends(get_project_service)):
    """
    Resurrect Action: Restore architectural file to portfolio.
    """
    result = service.resurrect_project(collection, slug)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
    return result
