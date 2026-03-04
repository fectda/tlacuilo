import re
from pathlib import Path
from typing import Dict, Any, Optional
from app.repositories.project_repository import ProjectRepository
from app.services.validators.project import ProjectValidator
from app.services.validators.content import ContentValidator

class ProjectWorkingCopyService:
    def __init__(self, repository: ProjectRepository, 
                 proj_validator: ProjectValidator, 
                 cont_validator: ContentValidator,
                 llm: Any,
                 prompts: Any):
        self.repo = repository
        self.proj_validator = proj_validator
        self.cont_validator = cont_validator
        self.llm = llm
        self.prompts = prompts

    def create_project(self, name: str, collection: str, slug: Optional[str] = None) -> Dict[str, Any]:
        self.cont_validator.ensure_content(name, "Project title is required")
        
        if not slug:
            slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

        project_dir = self.repo.get_project_dir(collection, slug)
        portfolio_path = self.repo.resolve_portfolio_path(collection, slug)
        self.proj_validator.ensure_project_not_exists(project_dir.exists(), portfolio_path is not None, slug)

        self.repo.initialize_local_memory(collection, slug, doc_status="borrador", is_active=True)

        template_path = self.repo.portfolio_path / "src" / "content" / collection / f"_template.md"
        local_md = project_dir / f"{slug}.md"
        
        if template_path.exists():
            content = self.repo.read_text(template_path)
            # Try to inject title into existing frontmatter
            content = re.sub(r'^title:\s*".*"', f'title: "{name}"', content, flags=re.MULTILINE)
        else:
            header = "---\n"
            content = f"{header}title: \"{name}\"\ndescription: \"Created via Tlacuilo\"\ndraft: true\ndate: 2026-01-01\ntags: [\"draft\"]\n---\n\n## La Tesis de la Resistencia\n\n\n## La Anatomía de la Fricción\n\n\n## El Imperativo del Rediseño\n\n\n## El Veredicto Final\n"
            
        self.repo.write_text(local_md, content)
        return {"id": slug, "status": "created"}

    def get_working_copy(self, collection: str, slug: str) -> Dict[str, Any]:
        project_dir = self.repo.get_project_dir(collection, slug)
        state = self.repo.get_doc_state(project_dir)
        local_md = project_dir / f"{slug}.md"
        
        if state.get("is_working_copy_active") and local_md.exists():
            return {"content": self.repo.read_text(local_md), "source": "local", "state": state}
            
        portfolio_md = self.repo.resolve_portfolio_path(collection, slug)
        if portfolio_md:
            content = self.repo.read_text(portfolio_md)
            self.repo.write_text(local_md, content)
            return {"content": content, "source": "portfolio", "state": state}
            
        return {"content": "", "source": "template", "state": state}

    async def save_working_copy(self, collection: str, slug: str, content: str) -> Dict[str, Any]:
        self.cont_validator.ensure_content(content)
        
        project_dir = self.repo.get_project_dir(collection, slug)
        err = await self.cont_validator.orchestrate_full_validation(
            content=content,
            collection=collection,
            repo=self.repo,
            llm=self.llm,
            prompts=self.prompts,
            debug_dir=project_dir / "drafts-tests",
            log_prefix="persist_"
        )
        if err: raise ValueError(f"Validación fallida: {err}")
        
        project_dir = self.repo.get_project_dir(collection, slug)
        self.repo.write_text(project_dir / f"{slug}.md", content)
        self.repo.save_doc_state(project_dir, {"is_working_copy_active": True, "doc_status": "borrador"})
        return {"status": "saved", "id": slug}

    def revert_working_copy(self, collection: str, slug: str) -> Dict[str, Any]:
        project_dir = self.repo.get_project_dir(collection, slug)
        portfolio_md = self.repo.resolve_portfolio_path(collection, slug)
        if not portfolio_md: raise FileNotFoundError("No portfolio version to revert to")
             
        content = self.repo.read_text(portfolio_md)
        self.repo.write_text(project_dir / f"{slug}.md", content)
        self.repo.save_doc_state(project_dir, {"is_working_copy_active": False, "doc_status": "revisión"})
        return {"status": "reverted", "content": content}

    def get_translation_copy(self, collection: str, slug: str) -> Dict[str, Any]:
        project_dir = self.repo.get_project_dir(collection, slug)
        local_en_md = project_dir / f"{slug}.en.md"
        portfolio_en_md = self.repo.portfolio_content / collection / "en" / f"{slug}.md"
        state = self.repo.get_doc_state(project_dir)

        content = ""
        if portfolio_en_md.exists(): content = self.repo.read_text(portfolio_en_md)
        if local_en_md.exists(): content = self.repo.read_text(local_en_md)
        if local_en_md.exists() and portfolio_en_md.exists() and state.get("doc_status") != "promovido":
            content = self.repo.read_text(portfolio_en_md)

        return {"content": content, "is_working_copy_active": local_en_md.exists()}

    async def save_translation_copy(self, collection: str, slug: str, content: str):
        self.cont_validator.ensure_content(content)
        project_dir = self.repo.get_project_dir(collection, slug)
        
        err = await self.cont_validator.orchestrate_full_validation(
            content=content,
            collection=collection,
            repo=self.repo,
            llm=self.llm,
            prompts=self.prompts,
            debug_dir=project_dir / "drafts-tests",
            log_prefix="persist_en_",
            target_language="English"
        )
        if err: raise ValueError(f"Validación traducción fallida: {err}")
            
        project_dir = self.repo.get_project_dir(collection, slug)
        self.repo.write_text(project_dir / f"{slug}.en.md", content)
        state = self.repo.get_doc_state(project_dir)
        state["doc_status"] = "traducción"
        self.repo.save_doc_state(project_dir, state)
