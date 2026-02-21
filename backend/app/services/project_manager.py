import logging
import frontmatter
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.repositories.project_repository import ProjectRepository
from app.services.validation_service import ValidationService

logger = logging.getLogger(__name__)

class ProjectManager:
    def __init__(self, repository: ProjectRepository, validator: ValidationService):
        self.repo = repository
        self.validator = validator

    def list_projects(self) -> Dict[str, List[Dict[str, Any]]]:
        """Omni-scanner following ARCHITECTURE 3.C.1."""
        collections = ["atoms", "bits", "mind"]
        grouped = {col: [] for col in collections}
        
        for col in collections:
            seen_slugs = set()
            
            # 1. Portfolio Scan
            portfolio_items = self.repo.list_collection_files(col)
            for item in portfolio_items:
                slug = item["slug"]
                if slug in seen_slugs: continue
                
                data = self._assemble_project_data(col, slug, item["path"])
                if data:
                    grouped[col].append(data)
                    seen_slugs.add(slug)

            # 2. Local Orphans
            local_slugs = self.repo.list_local_projects(col)
            for slug in local_slugs:
                if slug not in seen_slugs:
                    data = self._assemble_project_data(col, slug, source="local")
                    if data:
                        data["missing_files"] = True
                        grouped[col].append(data)
        
        return grouped

    def create_project(self, name: str, collection: str = "bits", slug: str = None) -> Dict[str, Any]:
        if not slug:
            slug = self._generate_slug(name)
            
        project_dir = self.repo.get_project_dir(collection, slug)
        if project_dir.exists() or self.repo.resolve_portfolio_path(collection, slug):
            return {"error": f"Project '{slug}' already exists", "status_code": 400}

        project_dir.mkdir(parents=True, exist_ok=True)
        self.repo.save_chat_history(project_dir, [])
        self.repo.save_doc_state(project_dir, {
            "doc_status": "borrador",
            "is_working_copy_active": True
        })

        # Scaffolding
        template = self._find_template(collection)
        local_md = project_dir / f"{slug}.md"
        
        content = ""
        if template:
            content = self.repo.read_text(template)
            content = content.replace("TITLE_PLACEHOLDER", name)
            # Safe title replacement if placeholder missing
            if name not in content:
                content = re.sub(r'^title:\s*".*"', f'title: "{name}"', content, flags=re.MULTILINE)
        else:
            content = f"---\ntitle: \"{name}\"\ndescription: \"Created via Tlacuilo\"\ndraft: true\ntype: {collection.upper()}\n---\n"
            
        self.repo.write_text(local_md, content)
        return {"id": slug, "status": "created"}

    def _assemble_project_data(self, col: str, slug: str, md_path: Optional[Path] = None, source: str = "portfolio") -> Optional[Dict[str, Any]]:
        project_dir = self.repo.get_project_dir(col, slug)
        state = self.repo.get_doc_state(project_dir)
        
        if not md_path:
             # Try local if source is local
             local_md = project_dir / f"{slug}.md"
             md_path = local_md if local_md.exists() else None

        if not md_path or not md_path.exists():
            return {
                "id": slug, "name": slug.title(), "description": "No metadata file found",
                "doc_status": state.get("doc_status", "borrador"),
                "is_working_copy_active": state.get("is_working_copy_active", False),
                "published": False, "type": col, "missing_files": True
            }

        meta = self.repo.get_metadata(md_path)
        return {
            "id": slug,
            "name": meta.get("title", slug),
            "description": meta.get("description", ""),
            "doc_status": state.get("doc_status", "borrador"),
            "is_working_copy_active": state.get("is_working_copy_active", False),
            "published": meta.get("published", False),
            "type": col,
            "missing_files": False
        }

    def get_working_copy(self, collection: str, slug: str) -> Dict[str, Any]:
        project_dir = self.repo.get_project_dir(collection, slug)
        state = self.repo.get_doc_state(project_dir)
        local_md = project_dir / f"{slug}.md"
        
        # Precedence Logic
        if state.get("is_working_copy_active") and local_md.exists():
            content = self.repo.read_text(local_md)
            return {"content": content, "source": "local", "state": state}
            
        portfolio_md = self.repo.resolve_portfolio_path(collection, slug)
        if portfolio_md:
            content = self.repo.read_text(portfolio_md)
            # Sync to local
            self.repo.write_text(local_md, content)
            return {"content": content, "source": "portfolio", "state": state}
            
        # Fallback to template
        template = self._find_template(collection)
        content = self.repo.read_text(template) if template else ""
        return {"content": content, "source": "template", "state": state}

    def save_working_copy(self, collection: str, slug: str, content: str) -> Dict[str, Any]:
        schema_error = self.validator.validate_schema(content, collection)
        
        if schema_error:
            return {
                "status": "rejected",
                "error": f"Validación estructural fallida: {schema_error}",
                "status_code": 400
            }
        
        project_dir = self.repo.get_project_dir(collection, slug)
        local_md = project_dir / f"{slug}.md"
        self.repo.write_text(local_md, content)
        
        self.repo.save_doc_state(project_dir, {
            "is_working_copy_active": True,
            "doc_status": "borrador"
        })
        
        return {
            "status": "saved",
            "id": slug
        }

    def publish_project(self, collection: str, slug: str) -> Dict[str, Any]:
        project_dir = self.repo.get_project_dir(collection, slug)
        local_md = project_dir / f"{slug}.md"
        
        if not local_md.exists():
            return {"error": "No working copy to publish", "status_code": 404}
            
        content = self.repo.read_text(local_md)
        error = self.validator.validate_schema(content, collection)
        if error:
            return {"error": f"Schema Validation Failed: {error}", "status_code": 400}
            
        target_md = self.repo.portfolio_content / collection / "es" / f"{slug}.md"
        self.repo.copy_file(local_md, target_md)
        
        self.repo.save_doc_state(project_dir, {
            "is_working_copy_active": False,
            "doc_status": "promovido"
        })
        
        return {"id": slug, "status": "published", "path": str(target_md)}

    def revert_working_copy(self, collection: str, slug: str) -> Dict[str, Any]:
        project_dir = self.repo.get_project_dir(collection, slug)
        local_md = project_dir / f"{slug}.md"
        
        portfolio_md = self.repo.resolve_portfolio_path(collection, slug)
        if not portfolio_md:
             return {"error": "No portfolio version to revert to", "status_code": 404}
             
        content = self.repo.read_text(portfolio_md)
        self.repo.write_text(local_md, content)
        
        self.repo.save_doc_state(project_dir, {
            "is_working_copy_active": False,
            "doc_status": "revisión"
        })
        return {"status": "reverted", "content": content}

    def delete_project(self, collection: str, slug: str):
        project_dir = self.repo.get_project_dir(collection, slug)
        self.repo.delete_dir(project_dir)

    def _generate_slug(self, name: str) -> str:
        return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

    def _find_template(self, collection: str) -> Optional[Path]:
        path = self.repo.portfolio_path / "src" / "templates" / f"{collection}-template.md"
        return path if path.exists() else None

    # Helper for style references
    def get_style_reference(self, collection: str) -> Optional[Path]:
        path = self.repo.portfolio_content / "_referencias" / f"{collection}-style.md"
        return path if path.exists() else None
