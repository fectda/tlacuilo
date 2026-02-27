from pathlib import Path
from typing import Dict, Any
from app.repositories.project_repository import ProjectRepository
from app.services.validators.project import ProjectValidator
from app.services.validators.content import ContentValidator

class ProjectPublishService:
    def __init__(self, repository: ProjectRepository, 
                 proj_validator: ProjectValidator, 
                 cont_validator: ContentValidator):
        self.repo = repository
        self.proj_validator = proj_validator
        self.cont_validator = cont_validator

    def publish_project(self, collection: str, slug: str) -> Dict[str, Any]:
        self.proj_validator.ensure_collection(collection)
        project_dir = self.repo.get_project_dir(collection, slug)
        local_md = project_dir / f"{slug}.md"
        
        if not local_md.exists(): raise FileNotFoundError("No working copy to publish")
            
        content = self.repo.read_text(local_md)
        err = self.cont_validator.validate_schema(content, collection)
        if err: raise ValueError(f"Schema Validation Failed: {err}")
            
        target_md = self.repo.portfolio_content / collection / "es" / f"{slug}.md"
        self.repo.copy_file(local_md, target_md)
        
        self.repo.save_doc_state(project_dir, {"is_working_copy_active": False, "doc_status": "promovido"})
        return {"id": slug, "status": "published"}

    def delete_project(self, collection: str, slug: str):
        project_dir = self.repo.get_project_dir(collection, slug)
        self.repo.delete_dir(project_dir)
