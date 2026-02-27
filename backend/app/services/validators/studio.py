from pathlib import Path
from typing import List, Dict, Any, Optional

class StudioValidator:
    def ensure_shot(self, meta: Optional[Dict[str, Any]], shot_id: str) -> Dict[str, Any]:
        if meta is None:
            raise FileNotFoundError(f"Shot '{shot_id}' not found.")
        return meta

    def ensure_variant(self, images: List[Dict[str, Any]], comfly_id: str, 
                       required_status: Optional[str] = None) -> Dict[str, Any]:
        variant = next((img for img in images if img.get("id") == comfly_id), None)
        if not variant:
            raise FileNotFoundError(f"Image variant '{comfly_id}' not found.")
        
        if required_status and variant.get("status") != required_status:
            raise ValueError(f"Image variant '{comfly_id}' is not in '{required_status}' state.")
        
        return variant

    def ensure_file(self, file_path: Any, comfly_id: str):
        p = Path(file_path) if not isinstance(file_path, Path) else file_path
        if not p.exists():
            raise FileNotFoundError(f"Physical file for variant '{comfly_id}' missing.")
