import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.repositories.project_repository import ProjectRepository
from app.services.validators.project import ProjectValidator

logger = logging.getLogger(__name__)

class ProjectDiscoveryService:
    def __init__(self, repository: ProjectRepository, validator: ProjectValidator):
        self.repo = repository
        self.validator = validator

    def list_projects(self) -> Dict[str, List[Dict[str, Any]]]:
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

    def _assemble_project_data(self, col: str, slug: str, md_path: Optional[Path] = None, source: str = "portfolio") -> Optional[Dict[str, Any]]:
        project_dir = self.repo.get_project_dir(col, slug)
        state = self.repo.get_doc_state(project_dir)
        
        if not md_path:
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
