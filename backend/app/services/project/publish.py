import logging
from pathlib import Path
from typing import Dict, Any, List
from fastapi import HTTPException
from app.repositories.project_repository import ProjectRepository
from app.services.validators.content import ContentValidator
from app.services.system.git_service import GitService
from app.services.studio.image_service import ImageOptimizationService
from app.clients.llm.base import LLMClient
from app.services.prompt_service import PromptService

logger = logging.getLogger(__name__)

class ProjectPublishService:
    """
    Orchestrator for the publishing lifecycle.
    Follows SOLID by delegating Git and Image operations to specialized services.
    """
    def __init__(self, repository: ProjectRepository, 
                 cont_validator: ContentValidator,
                 git: GitService,
                 image_opt: ImageOptimizationService,
                 llm: LLMClient,
                 prompts: PromptService):
        self.repo = repository
        self.cont_validator = cont_validator
        self.git = git
        self.image_opt = image_opt
        self.llm = llm
        self.prompts = prompts

    async def promote_to_portfolio(self, collection: str, slug: str) -> Dict[str, Any]:
        """
        Validates the working copy and promotes it to the portfolio (Español).
        Sets draft: false in the local copy before moving/copying.
        """
        project_dir = self.repo.get_project_dir(collection, slug)
        local_md = project_dir / f"{slug}.md"
        
        if not local_md.exists():
            raise HTTPException(status_code=404, detail="No existe una copia de trabajo para promover.")
            
        content = self.repo.read_text(local_md)
        
        # 1. Structural Validation
        err = await self.cont_validator.orchestrate_full_validation(
            content=content,
            collection=collection,
            repo=self.repo,
            llm=self.llm,
            prompts=self.prompts,
            debug_dir=None # No debug files for promotion
        )
        if err:
            raise ValueError(f"Fallo en la validación de contenido: {err}")
            
        # 2. Update Frontmatter (draft: false)
        self.repo.set_metadata(local_md, {"draft": False})
        
        # 3. Copy to Portfolio (es)
        target_md = self.repo.portfolio_content / collection / "es" / f"{slug}.md"
        self.repo.copy_file(local_md, target_md)
        
        # 4. Update state
        self.repo.save_doc_state(project_dir, {
            "is_working_copy_active": False, 
            "doc_status": "promovido"
        })
        
        return {"id": slug, "status": "promovido"}

    def publish_global(self, collection: str, slug: str) -> Dict[str, Any]:
        """
        Final publishing step:
        1. Optimizes images.
        2. Consolidates files.
        3. Clean Git transaction (commit & push).
        """
        project_dir = self.repo.get_project_dir(collection, slug)
        state = self.repo.get_doc_state(project_dir)
        
        if state.get("doc_status") == "publicado":
             return {"status": "Already published"}

        # 1. Verify existence of both ES and EN in local memory (shadow drafts)
        local_es = project_dir / f"{slug}.md"
        local_en = project_dir / f"{slug}.en.md"
        
        if not local_es.exists() or not local_en.exists():
            raise ValueError("Faltan archivos locales (Español o Inglés) para realizar la publicación global.")

        # 2. Ensure "draft: false" in both
        self.repo.set_metadata(local_es, {"draft": False})
        self.repo.set_metadata(local_en, {"draft": False})

        # 3. Synchronize MD files to portfolio
        portfolio_es = self.repo.portfolio_content / collection / "es" / f"{slug}.md"
        portfolio_en = self.repo.portfolio_content / collection / "en" / f"{slug}.md"
        self.repo.copy_file(local_es, portfolio_es)
        self.repo.copy_file(local_en, portfolio_en)

        # 4. Image Optimization and Deployment
        public_dir = self.image_opt.optimize_and_deploy(collection, slug)

        # 5. Git Transaction
        try:
            self.git.ensure_clean_index()
        except ValueError as e:
            # Dirty index is a precondition/user-fixable error (400)
            raise HTTPException(status_code=400, detail=str(e))

        try:
            # File list for surgical commit
            files_to_add = [
                portfolio_es,
                portfolio_en
            ]
            if public_dir.exists():
                for asset in public_dir.glob("*.webp"):
                    files_to_add.append(asset)
            
            self.git.add_files(files_to_add)
            self.git.commit(f"publish(docs): {collection}/{slug}")
        except Exception as e:
            logger.error(f"Git staging/commit failed: {e}")
            raise HTTPException(status_code=500, detail=f"Error al preparar el commit de Git: {str(e)}")

        try:
            self.git.push()
        except RuntimeError as e:
            # Push failed: rollback the commit to keep the repo clean.
            logger.error(f"Git push failed, rolling back commit: {e}")
            self.git.rollback_last_commit()
            raise HTTPException(
                status_code=503,
                detail="No se pudo conectar con el repositorio remoto. Verifica las credenciales SSH en el contenedor."
            )

        # 6. Final State Update
        state.update({
            "doc_status": "publicado",
            "is_working_copy_active": False
        })
        self.repo.save_doc_state(project_dir, state)
        
        return {"status": "publicado", "slug": slug}

    def forget_project_memory(self, collection: str, slug: str):
        project_dir = self.repo.get_project_dir(collection, slug)
        self.repo.delete_dir(project_dir)

    def resurrect_portfolio_file(self, collection: str, slug: str):
        project_dir = self.repo.get_project_dir(collection, slug)
        local_md = project_dir / f"{slug}.md"
        
        if not local_md.exists():
            raise FileNotFoundError("No existe copia local para resucitar.")
            
        target_md = self.repo.portfolio_content / collection / "es" / f"{slug}.md"
        if target_md.exists():
            raise FileExistsError("El archivo ya existe en el portafolio.")
            
        self.repo.copy_file(local_md, target_md)
