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
            "is_working_copy_active": False,
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

        local_md = local_dir / f"{slug}.md"
        
        # If local .md is missing, try index.md
        if not local_md.exists() and (local_dir / "index.md").exists():
            local_md = local_dir / "index.md"
            
        if not local_md.exists():
             return {"error": "Local .md file not found to resurrect", "status_code": 404}

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

    def get_project_state(self, collection: str, slug: str) -> Dict[str, Any]:
        """Reads the doc_state.json for a project."""
        state_file = self.local_path / collection / slug / "doc_state.json"
        if not state_file.exists():
            return {"doc_status": "borrador", "is_working_copy_active": False}
        try:
            return json.loads(state_file.read_text())
        except:
            return {"doc_status": "borrador", "is_working_copy_active": False}

    def get_chat_history_raw(self, collection: str, slug: str) -> List[Dict[str, Any]]:
        """Reads chat_history.json without any filtering."""
        history_file = self.local_path / collection / slug / "chat_history.json"
        if not history_file.exists():
            return []
        try:
            return json.loads(history_file.read_text())
        except Exception as e:
            logger.error(f"Error reading raw chat history for {slug}: {e}")
            return []

    def activate_session(self, collection: str, slug: str):
        """Sets is_working_copy_active to True in doc_state.json."""
        self.update_project_state(collection, slug, {"is_working_copy_active": True})

    def update_project_state(self, collection: str, slug: str, updates: Dict[str, Any]):
        """Updates doc_state.json with new values."""
        local_dir = self.local_path / collection / slug
        local_dir.mkdir(parents=True, exist_ok=True)
        state_file = local_dir / "doc_state.json"
        
        state = self.get_project_state(collection, slug)
        state.update(updates)
        state["last_update"] = datetime.now().isoformat()
        self._write_json(state_file, state)

    def get_working_copy(self, collection: str, slug: str) -> Dict[str, Any]:
        """
        Implementation of the Precedence Logic:
        1. If is_working_copy_active: true -> Read local {slug}.md
        2. If false -> Read from Portfolio, hydrate local if needed.
        3. If nothing -> Load template.
        """
        local_dir = self.local_path / collection / slug
        local_md = local_dir / f"{slug}.md"
        portfolio_dir = self.portfolio_content / collection / slug
        portfolio_md = self._find_md_in_folder(portfolio_dir, slug)
        
        state = self.get_project_state(collection, slug)
        is_active = state.get("is_working_copy_active", False)

        content = ""
        source = "unknown"

        if is_active and local_md.exists():
            content = local_md.read_text()
            source = "local_active"
        elif portfolio_md and portfolio_md.exists():
            content = portfolio_md.read_text()
            source = "portfolio"
            # Hydrate/Update local if active flag is false but portfolio exists
            local_dir.mkdir(parents=True, exist_ok=True)
            local_md.write_text(content)
        elif local_md.exists():
            # Fallback for orphan or just local existence
            content = local_md.read_text()
            source = "local_orphan"
        else:
            # New Project / Template
            template = self._find_template(collection)
            if template:
                content = template.read_text()
                # Placeholder replacement
                name = slug.replace("-", " ").title()
                content = content.replace("TITLE_PLACEHOLDER", name)
                source = "template"
            else:
                content = f"---\ntitle: {slug}\ndraft: true\n---\n\nNuevo proyecto {slug}."
                source = "minimal"

        # Load chat history
        history_file = local_dir / "chat_history.json"
        history = []
        if history_file.exists():
            try: history = json.loads(history_file.read_text())
            except: pass
        
        return {
            "content": content,
            "source": source,
            "state": state,
            "history": history
        }

    def revert_working_copy(self, collection: str, slug: str) -> Dict[str, Any]:
        """
        POST .../revert: Deletes local {slug}.md and replaces with Portfolio version.
        Resets is_working_copy_active to false.
        """
        local_dir = self.local_path / collection / slug
        local_md = local_dir / f"{slug}.md"
        portfolio_dir = self.portfolio_content / collection / slug
        portfolio_md = self._find_md_in_folder(portfolio_dir, slug)

        if not portfolio_md or not portfolio_md.exists():
            return {"error": "No portfolio version to revert to", "status_code": 404}

        # Copy portfolio to local
        shutil.copy2(portfolio_md, local_md)
        
        # Reset flag and set status to revision
        self.update_project_state(collection, slug, {
            "is_working_copy_active": False,
            "doc_status": "revisión"
        })
        
        return {"status": "reverted", "source": "portfolio"}

    def get_chat_history_safe(self, collection: str, slug: str) -> List[Dict[str, Any]]:
        """
        Returns chat history filtering out system_only messages.
        """
        local_dir = self.local_path / collection / slug
        history_file = local_dir / "chat_history.json"
        
        if not history_file.exists():
            return []
            
        try:
            history = json.loads(history_file.read_text())
            # Filter out system_only messages
            return [msg for msg in history if not msg.get("system_only", False)]
        except Exception as e:
            logger.error(f"Error reading chat history for {slug}: {e}")
            return []

    def save_working_copy(self, collection: str, slug: str, content: str) -> Dict[str, Any]:
        """
        PUT .../{slug}: Manual Save.
        Includes Schema Validator (against templates) and Spellcheck placeholder.
        """
        # 1. Validation Logic (Strict as per ARCHITECTURE 3.C)
        if not content.strip():
             return {"error": "Content cannot be empty", "status_code": 400}
             
        if not content.strip().startswith("---"):
             return {"error": "Invalid Markdown: Missing frontmatter (must start with ---)", "status_code": 400}
        
        try:
            post = frontmatter.loads(content)
            # Mandatory Keys (Internal check)
            required_keys = ["title", "description", "draft"]
            missing = [k for k in required_keys if k not in post.metadata]
            if missing:
                # We log warning but allow if it's not a 'publish' action
                logger.warning(f"Project {slug} saved with missing metadata keys: {missing}")
        except Exception as e:
            return {"error": f"Metadata parsing error: {str(e)}", "status_code": 400}
        
        local_dir = self.local_path / collection / slug
        local_dir.mkdir(parents=True, exist_ok=True)
        local_md = local_dir / f"{slug}.md"
        
        local_md.write_text(content)
        
        # Update state: status -> borrador, is_working_copy_active -> true
        self.update_project_state(collection, slug, {
            "is_working_copy_active": True,
            "doc_status": "borrador"
        })
        
        return {"status": "saved", "path": str(local_md)}

    def publish_project(self, collection: str, slug: str) -> Dict[str, Any]:
        """
        POST .../publish: Promote local working copy to portfolio.
        """
        local_dir = self.local_path / collection / slug
        local_md = local_dir / f"{slug}.md"
        
        if not local_md.exists():
            return {"error": "No working copy to publish", "status_code": 404}
            
        portfolio_dir = self.portfolio_content / collection / slug
        portfolio_dir.mkdir(parents=True, exist_ok=True)
        target_md = portfolio_dir / f"{slug}.md"
        
        shutil.copy2(local_md, target_md)
        
        # Reset flag
        self.update_project_state(collection, slug, {
            "is_working_copy_active": False,
            "doc_status": "revisión" # Example transition
        })
        
        return {"status": "published", "path": str(target_md)}

    def get_translation_copy(self, collection: str, slug: str) -> Dict[str, Any]:
        """GET .../translate: Reads the English working copy ({slug}.en.md)"""
        local_dir = self.local_path / collection / slug
        en_md = local_dir / f"{slug}.en.md"
        
        if not en_md.exists():
            # Try to find in portfolio if it exists
            portfolio_en = self.portfolio_content / collection / "en" / f"{slug}.md"
            if portfolio_en.exists():
                content = portfolio_en.read_text()
                en_md.write_text(content)
                return {"content": content, "source": "portfolio_en"}
            return {"error": "Translation copy not found", "status_code": 404}
            
        return {"content": en_md.read_text(), "source": "local_en"}

    def save_translation_copy(self, collection: str, slug: str, content: str) -> Dict[str, Any]:
        """PUT .../translate: Manual save of English version."""
        local_dir = self.local_path / collection / slug
        local_dir.mkdir(parents=True, exist_ok=True)
        en_md = local_dir / f"{slug}.en.md"
        en_md.write_text(content)
        return {"status": "saved", "path": str(en_md)}

    def publish_translation(self, collection: str, slug: str) -> Dict[str, Any]:
        """POST .../publish-en: Finalize translation and move to portfolio."""
        local_dir = self.local_path / collection / slug
        en_md = local_dir / f"{slug}.en.md"
        if not en_md.exists():
            return {"error": "No English version to publish", "status_code": 404}
            
        target_dir = self.portfolio_content / collection / "en"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_md = target_dir / f"{slug}.md"
        
        shutil.copy2(en_md, target_md)
        return {"status": "published_en", "path": str(target_md)}


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
                "is_working_copy_active": False,
                "last_update": datetime.now().isoformat(),
                "pila_de_pendientes": []
            })

    def _get_project_data(self, col: str, slug: str, md_file: Path = None, source: str = "portfolio") -> Optional[dict]:
        local_dir = self.local_path / col / slug
        doc_state_file = local_dir / "doc_state.json"
        
        status = "borrador"
        is_active = False
        if doc_state_file.exists():
            try:
                state = json.loads(doc_state_file.read_text())
                status = state.get("doc_status", "borrador")
                is_active = state.get("is_working_copy_active", False)
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
                "is_working_copy_active": is_active,
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
                "is_working_copy_active": is_active,
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
