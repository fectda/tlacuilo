import json
import shutil
import logging
import frontmatter
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)

class ProjectRepository:
    def __init__(self):
        self.projects_path = settings.PROJECTS_PATH
        self.portfolio_path = settings.PORTAFOLIO_PATH
        self.portfolio_content = self.portfolio_path / "src" / "content"

    def get_project_dir(self, collection: str, slug: str) -> Path:
        return self.projects_path / collection / slug

    def read_text(self, path: Path) -> Optional[str]:
        if path.exists():
            return path.read_text()
        return None

    def write_text(self, path: Path, content: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def read_json(self, path: Path) -> Optional[Dict[str, Any]]:
        content = self.read_text(path)
        if content:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                pass
        return None

    def write_json(self, path: Path, data: Any):
        self.write_text(path, json.dumps(data, indent=2))

    def resolve_portfolio_path(self, collection: str, slug: str, lang: str = "es") -> Optional[Path]:
        """Unified resolution: {collection}/{lang}/{slug}.md or legacy folder."""
        # Standard: {collection}/{lang}/{slug}.md
        std_path = self.portfolio_content / collection / lang / f"{slug}.md"
        if std_path.exists():
            return std_path
            
        # Legacy: {collection}/{slug}/{slug}.md or index.md
        legacy_dir = self.portfolio_content / collection / slug
        if legacy_dir.exists():
            for name in [f"{slug}.md", "index.md"]:
                legacy_path = legacy_dir / name
                if legacy_path.exists():
                    return legacy_path
        return None

    def get_chat_history(self, project_dir: Path) -> List[Dict[str, Any]]:
        path = project_dir / "chat_history.json"
        return self.read_json(path) or []

    def save_chat_history(self, project_dir: Path, history: List[Dict[str, Any]]):
        path = project_dir / "chat_history.json"
        self.write_json(path, history)

    def get_doc_state(self, project_dir: Path) -> Dict[str, Any]:
        path = project_dir / "doc_state.json"
        return self.read_json(path) or {
            "doc_status": "revisión",
            "is_working_copy_active": False,
            "last_update": datetime.now().isoformat()
        }

    def save_doc_state(self, project_dir: Path, state: Dict[str, Any]):
        path = project_dir / "doc_state.json"
        state["last_update"] = datetime.now().isoformat()
        self.write_json(path, state)

    def initialize_local_memory(self, collection: str, slug: str, doc_status: str = "revisión", is_active: bool = False):
        """Creates the minimal local structure for a project."""
        project_dir = self.get_project_dir(collection, slug)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # chat_history.json (Empty)
        if not (project_dir / "chat_history.json").exists():
            self.save_chat_history(project_dir, [])
            
        # doc_state.json
        state_path = project_dir / "doc_state.json"
        if not state_path.exists():
            self.save_doc_state(project_dir, {
                "doc_status": doc_status,
                "is_working_copy_active": is_active
            })
        return project_dir

    def list_collection_files(self, collection: str) -> List[Dict[str, Any]]:
        """Scans both flat files and folder-based projects in a collection."""
        found = []
        col_dir = self.portfolio_content / collection
        if not col_dir.exists():
            return found

        # 1. Scan folders (Project-as-Folder)
        for item in col_dir.iterdir():
            if item.is_dir() and item.name not in ["en", "es"] and not item.name.startswith("."):
                slug = item.name
                md = self.resolve_portfolio_path(collection, slug)
                if md:
                    found.append({"slug": slug, "path": md, "source": "portfolio"})

        # 2. Scan translation folders (File-as-Project)
        for lang in ["es", "en"]:
            lang_dir = col_dir / lang
            if lang_dir.exists():
                for md in lang_dir.glob("*.md"):
                    found.append({"slug": md.stem, "path": md, "source": "portfolio"})
        
        return found

    def list_local_projects(self, collection: str) -> List[str]:
        local_col = settings.PROJECTS_PATH / collection
        if not local_col.exists():
            return []
        return [d.name for d in local_col.iterdir() if d.is_dir() and not d.name.startswith(".")]

    def get_metadata(self, md_file: Path) -> Dict[str, Any]:
        try:
            post = frontmatter.load(md_file)
            return {
                "title": post.metadata.get("title", md_file.stem),
                "description": post.metadata.get("description", ""),
                "published": not post.metadata.get("draft", True),
                "metadata": post.metadata
            }
        except Exception as e:
            logger.error(f"Error reading metadata from {md_file}: {e}")
            return {"title": md_file.stem, "error": str(e)}

    def copy_file(self, src: Path, dst: Path):
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    def delete_dir(self, directory: Path):
        if directory.exists():
            shutil.rmtree(directory)
