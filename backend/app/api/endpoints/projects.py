from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.repositories.project_repository import ProjectRepository
from app.services.project_manager import ProjectManager
from app.services.validation_service import ValidationService

router = APIRouter()

# --- Dependencies ---

def get_repository():
    return ProjectRepository()

def get_validator():
    return ValidationService()

def get_manager(repo: ProjectRepository = Depends(get_repository), 
                validator: ValidationService = Depends(get_validator)):
    return ProjectManager(repo, validator)

# --- Models ---

class CreateProjectRequest(BaseModel):
    name: str
    collection: str = "bits"
    slug: Optional[str] = None

# --- Endpoints ---

@router.get("/", response_model=Dict[str, List[Dict[str, Any]]])
async def list_projects(manager: ProjectManager = Depends(get_manager)):
    """
    List all available projects (content collections).
    Executes the Discovery Cycle.
    """
    try:
        return manager.list_projects()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Dict[str, Any])
async def create_project(request: CreateProjectRequest, manager: ProjectManager = Depends(get_manager)):
    """
    Create a new project scaffolding.
    """
    if not request.name:
        raise HTTPException(status_code=400, detail="Project name is required")
        
    result = manager.create_project(name=request.name, collection=request.collection, slug=request.slug)
    
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 400), detail=result["error"])
        
    return {"id": result["id"], "status": result["status"]}
