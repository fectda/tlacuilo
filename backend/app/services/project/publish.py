import subprocess
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

    def resurrect_project(self, collection: str, slug: str):
        project_dir = self.repo.get_project_dir(collection, slug)
        local_md = project_dir / f"{slug}.md"
        
        if not local_md.exists(): raise FileNotFoundError("No local working copy to resurrect")
            
        target_md = self.repo.portfolio_content / collection / "es" / f"{slug}.md"
        if target_md.exists(): raise FileExistsError("The file already exists in the portfolio")
            
        self.repo.copy_file(local_md, target_md)

    def publish_to_remote(self, collection: str, slug: str) -> Dict[str, Any]:
        project_dir = self.repo.get_project_dir(collection, slug)
        state = self.repo.get_doc_state(project_dir)
        
        if state.get("doc_status") == "publicado":
            raise ValueError("El proyecto ya se encuentra publicado.")
            
        portfolio_en_md = self.repo.portfolio_content / collection / "en" / f"{slug}.md"
        if not portfolio_en_md.exists():
            raise ValueError(f"No se puede publicar: Falta versión en Inglés en el portafolio (en/{slug}.md)")
            
        state["doc_status"] = "publicado"
        self.repo.save_doc_state(project_dir, state)
        
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            cwd = str(self.repo.portfolio_path)
            subprocess.run(["git", "add", "."], cwd=cwd, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", f"publish(docs): {collection}/{slug}"], cwd=cwd, check=True, capture_output=True)
            subprocess.run(["git", "push"], cwd=cwd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Git execution failed: {e.stderr.decode() if e.stderr else str(e)}")
            # Rollback state
            state["doc_status"] = "promovido"
            self.repo.save_doc_state(project_dir, state)
            raise ValueError("Error al sincronizar con el repositorio remoto. Verifica los logs.")
            
        return {"status": "publicado"}
