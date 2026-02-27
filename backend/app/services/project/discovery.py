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
            # 1. Lista todo lo que hay en Portfolio
            portfolio_items = self.repo.list_collection_files(col)
            # Mapa de slug -> path para acceso rápido
            portfolio_map = {item["slug"]: item["path"] for item in portfolio_items}

            # 2. Lista lo que hay en Local
            local_slugs = set(self.repo.list_local_projects(col))

            # 3. Discovery Cycle (3.A): Cruce e Hidratación
            # Todos los slugs que nos interesan (Unión de ambos mundos)
            all_slugs = set(portfolio_map.keys()) | local_slugs
            
            for slug in sorted(all_slugs):
                # Caso Hidratación: Está en Portafolio pero NO en Local
                if slug in portfolio_map and slug not in local_slugs:
                    logger.info(f"Hidratando proyecto: {slug} en {col}")
                    project_dir = self.repo.initialize_local_memory(col, slug)
                    local_md = project_dir / f"{slug}.md"
                    if not local_md.exists():
                        self.repo.copy_file(portfolio_map[slug], local_md)
                
                # Ensamblar datos (Sea local, portafolio o recién hidratado)
                # Si está en portafolio enviamos el path del portafolio como pista
                p_path = portfolio_map.get(slug)
                data = self._assemble_project_data(col, slug, p_path)
                
                if data:
                    # Marcar como huérfano si solo existe localmente
                    if slug not in portfolio_map:
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
