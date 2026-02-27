from pathlib import Path
from typing import Any, Optional

class ProjectValidator:
    def ensure_collection(self, collection: str):
        if collection not in ["atoms", "bits", "mind"]:
            raise ValueError(f"Invalid collection: {collection}. Must be 'atoms', 'bits' or 'mind'.")

    def ensure_project_exists(self, project_dir: Any, slug: str):
        p = Path(project_dir) if not isinstance(project_dir, Path) else project_dir
        if not p.exists():
            raise FileNotFoundError(f"Project '{slug}' not found in local memory.")

    def ensure_project_not_exists(self, exists_locally: bool, exists_in_portfolio: bool, slug: str):
        if exists_locally or exists_in_portfolio:
            raise ValueError(f"Project '{slug}' already exists.")
