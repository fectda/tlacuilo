import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import frontmatter
from datetime import datetime
import json
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectService:
    def __init__(self):
        # Paths from Environment (aligned with Docker non-root user)
        self.portfolio_path = Path(os.getenv("PORTAFOLIO_PATH", "/home/tlacuilo/portfolio"))
        self.portfolio_content = self.portfolio_path / "src" / "content"
        self.local_path = Path(os.getenv("PROJECTS_PATH", "/home/tlacuilo/projects"))
        self.local_path.mkdir(parents=True, exist_ok=True)
        self.template_path = self.portfolio_path / "src" / "templates"

        logger.info(f"Initialized ProjectService with Portfolio: {self.portfolio_content} and Local: {self.local_path}")

    def list_projects(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Omni-scanner: Detects projects in folders, translation files, and local memory.
        Executes Hydration and Context Injection.
        """
        grouped_projects = {"atoms": [], "bits": [], "mind": []}
        collections = ["atoms", "bits", "mind"]
        
        # Track seen slugs to avoid duplicates and handle orphans
        seen_slugs_by_col: Dict[str, Set[str]] = {col: set() for col in collections}

        for col in collections:
            col_portfolio = self.portfolio_content / col
            if not col_portfolio.exists():
                continue

            # 1. Scan direct subdirectories (Project-as-Folder)
            for item in col_portfolio.iterdir():
                if not item.is_dir() or item.name.startswith(".") or item.name in ["en", "es"]:
                    continue
                
                slug = item.name
                md_file = self._find_md_in_folder(item, slug)
                if md_file:
                    self._process_project(col, slug, md_file, grouped_projects, seen_slugs_by_col)

            # 2. Scan translation folders (File-as-Project)
            for lang in ["es", "en"]:
                lang_dir = col_portfolio / lang
                if not lang_dir.exists():
                    continue
                
                for md_file in lang_dir.glob("*.md"):
                    slug = md_file.stem
                    self._process_project(col, slug, md_file, grouped_projects, seen_slugs_by_col)

        # 3. Detect Orphans (Local memory without Portfolio match)
        for col in collections:
            col_local = self.local_path / col
            if not col_local.exists():
                continue
            
            for local_dir in col_local.iterdir():
                slug = local_dir.name
                if slug not in seen_slugs_by_col[col]:
                    project_data = self._get_project_data(col, slug, source="local")
                    if project_data:
                        project_data["missing_files"] = True
                        grouped_projects[col].append(project_data)

        return grouped_projects

    def create_project(self, name: str, collection: str = "bits", slug: str = None) -> Dict[str, Any]:
        """
        Create a new project locally. Naming: {slug}.md
        """
        if not slug:
            slug = self._generate_slug(name)
            
        if self._slug_exists(collection, slug):
            return {"error": f"Slug '{slug}' already exists", "status_code": 400}

        local_dir = self.local_path / collection / slug
        local_dir.mkdir(parents=True, exist_ok=True)

        # Initialize History & State
        self._write_json(local_dir / "chat_history.json", [])
        self._write_json(local_dir / "doc_state.json", {
            "doc_status": "borrador",
            "last_update": datetime.now().isoformat(),
            "pila_de_pendientes": ["Redactar contenido inicial"]
        })

        # Scaffolding
        template = self._find_template(collection)
        local_md = local_dir / f"{slug}.md"
        
        if template:
            content = template.read_text()
            if "TITLE_PLACEHOLDER" in content:
                content = content.replace("TITLE_PLACEHOLDER", name)
            else:
                # Fallback: Regex replace title line if placeholder missing
                content = re.sub(r'^title:\s*".*"', f'title: "{name}"', content, flags=re.MULTILINE)
            local_md.write_text(content)
        else:
            post = frontmatter.Post("", title=name, description="Created via Tlacuilo", 
                                   date=datetime.now().strftime("%Y-%m-%d"), draft=True, type=collection.upper())
            local_md.write_bytes(frontmatter.dumps(post).encode('utf-8'))

        return {"id": slug, "name": name, "type": collection, "status": "created"}

    def delete_project(self, collection: str, slug: str) -> Dict[str, Any]:
        """
        Forget Action: Removes the local project directory.
        """
        local_dir = self.local_path / collection / slug
        if not local_dir.exists():
            return {"error": "Project memory not found", "status_code": 404}
        
        try:
            shutil.rmtree(local_dir)
            logger.info(f"Deleted local memory for {collection}/{slug}")
            return {"status": "deleted", "id": slug}
        except Exception as e:
            logger.error(f"Error deleting project {slug}: {e}")
            return {"error": str(e), "status_code": 500}

    def resurrect_project(self, collection: str, slug: str) -> Dict[str, Any]:
        """
        Resurrect Action: Restores the .md file from local memory to the portfolio.
        """
        local_dir = self.local_path / collection / slug
        if not local_dir.exists():
            return {"error": "Project memory not found", "status_code": 404}
        
        # Ensure target portfolio dir exists
        portfolio_dir = self.portfolio_content / collection / slug
        portfolio_dir.mkdir(parents=True, exist_ok=True)

        # Establish local_md path (even if it doesn't exist yet)
        local_md = local_dir / f"{slug}.md"
        
        # If local .md is missing, regenerate it!
        if not local_md.exists() and not (local_dir / "index.md").exists():
            logger.info(f"Local .md missing for {slug}, regenerating from template/defaults...")
            template = self._find_template(collection)
            name = slug.replace("-", " ").title()
            
            if template:
                content = template.read_text()
                if "TITLE_PLACEHOLDER" in content:
                    content = content.replace("TITLE_PLACEHOLDER", name)
                else:
                    content = re.sub(r'^title:\s*".*"', f'title: "{name}"', content, flags=re.MULTILINE)
                local_md.write_text(content)
            else:
                post = frontmatter.Post("", title=name, description="Resurrected via Tlacuilo", 
                                       date=datetime.now().strftime("%Y-%m-%d"), draft=True, type=collection.upper())
                local_md.write_bytes(frontmatter.dumps(post).encode('utf-8'))

        # Check for index.md if slug.md still doesn't exist (unlikely now, but safe)
        if not local_md.exists():
             if (local_dir / "index.md").exists():
                 local_md = local_dir / "index.md"
             else:
                 # Should not happen given logic above, but fail safe
                 return {"error": "Failed to generate local .md file", "status_code": 500}

        target_md = portfolio_dir / f"{slug}.md"
        
        try:
            # Enforce Draft Status on Resurrection
            post = frontmatter.load(local_md)
            post.metadata["draft"] = True
            post.metadata["status"] = "draft" 
            
            # Write back to local
            local_md.write_bytes(frontmatter.dumps(post).encode('utf-8'))
            
            # Copy to portfolio
            shutil.copy2(local_md, target_md)
            
            logger.info(f"Resurrected project {collection}/{slug} to portfolio (Draft Mode)")
            return {"status": "resurrected", "id": slug}
        except Exception as e:
            logger.error(f"Error resurrecting project {slug}: {e}")
            return {"error": str(e), "status_code": 500}

    def _process_project(self, col: str, slug: str, md_file: Path, grouped: dict, seen: dict):
        if slug in seen[col]:
            return # Already handled this project via another source (folder vs translation)
        
        seen[col].add(slug)
        
        # Scenario A: Hydrate if local memory missing
        self._hydrate(col, slug, md_file)
        
        # Extract metadata
        data = self._get_project_data(col, slug, md_file=md_file)
        if data:
            grouped[col].append(data)

    def _hydrate(self, col: str, slug: str, md_file: Path):
        local_dir = self.local_path / col / slug
        if not local_dir.exists():
            logger.info(f"Hydrating {col}/{slug}")
            local_dir.mkdir(parents=True, exist_ok=True)
            
            # Protocol: Context Injection
            snippet = ""
            try:
                post = frontmatter.load(md_file)
                snippet = post.content[:500]
            except: pass
            
            history = [{
                "role": "system",
                "content": f"Contexto inicial cargado desde archivo existente: {snippet}",
                "timestamp": datetime.now().isoformat()
            }]
            self._write_json(local_dir / "chat_history.json", history)
            self._write_json(local_dir / "doc_state.json", {
                "doc_status": "borrador",
                "last_update": datetime.now().isoformat(),
                "pila_de_pendientes": []
            })

    def _get_project_data(self, col: str, slug: str, md_file: Path = None, source: str = "portfolio") -> Optional[dict]:
        local_dir = self.local_path / col / slug
        doc_state_file = local_dir / "doc_state.json"
        
        status = "borrador"
        if doc_state_file.exists():
            try: status = json.loads(doc_state_file.read_text()).get("doc_status", "borrador")
            except: pass

        if not md_file:
            # Attempt to find md file in local or portfolio
            base = local_dir if source == "local" else self.portfolio_content / col / slug
            md_file = self._find_md_in_folder(base, slug)
            if not md_file and source == "portfolio":
                # Check translations
                for lang in ["es", "en"]:
                    cand = self.portfolio_content / col / lang / f"{slug}.md"
                    if cand.exists():
                        md_file = cand
                        break

        # Fallback for "Orphan" projects in local memory without an .md file
        if (not md_file or not md_file.exists()) and source == "local":
            return {
                "id": slug,
                "name": slug.title(), 
                "description": "Memoria local sin archivo de metadatos.",
                "doc_status": status,
                "published": False,
                "type": col,
                "missing_files": True, # Specific flag for UI
                "missing_md": True
            }

        if not md_file or not md_file.exists():
            return None

        try:
            post = frontmatter.load(md_file)
            return {
                "id": slug,
                "name": post.metadata.get("title") or slug,
                "description": post.metadata.get("description", ""),
                "doc_status": status,
                "published": not post.metadata.get("draft", True),
                "type": col,
                "missing_files": False
            }
        except Exception as e:
            logger.error(f"Error reading project data for {slug}: {e}")
            return {
                "id": slug,
                "name": slug,
                "description": "Error leyendo metadatos.",
                "doc_status": status,
                "published": False,
                "type": col,
                "error": str(e)
            }

    def _find_md_in_folder(self, folder: Path, slug: str) -> Optional[Path]:
        if not folder.exists(): return None
        for name in [f"{slug}.md", "index.md"]:
            cand = folder / name
            if cand.exists(): return cand
        return None

    def _find_template(self, col: str) -> Optional[Path]:
        for name in [f"{col}-template.md", f"{col}.md"]:
            cand = self.template_path / name
            if cand.exists(): return cand
        return None

    def _write_json(self, path: Path, data: Any):
        path.write_text(json.dumps(data, indent=2))

    def _generate_slug(self, name: str) -> str:
        return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

    def _slug_exists(self, col: str, slug: str) -> bool:
        local = (self.local_path / col / slug).exists()
        port_folder = (self.portfolio_content / col / slug).exists()
        port_es = (self.portfolio_content / col / "es" / f"{slug}.md").exists()
        port_en = (self.portfolio_content / col / "en" / f"{slug}.md").exists()
        return local or port_folder or port_es or port_en
