from typing import Dict, Any
from fastapi.responses import FileResponse
from app.repositories.project_repository import ProjectRepository
from app.services.validators.studio import StudioValidator
from app.services.studio.shot_manager import StudioShotManager

class StudioAssetService:
    def __init__(self, repo: ProjectRepository, validator: StudioValidator, 
                 shot_manager: StudioShotManager):
        self.repo = repo
        self.validator = validator
        self.shot_manager = shot_manager

    def get_image(self, collection: str, slug: str, shot_id: str, comfly_id: str) -> FileResponse:
        meta = self.shot_manager.get_shot(collection, slug, shot_id)
        self.validator.ensure_variant(meta["images"], comfly_id)
        path = self.shot_manager._shot_dir(collection, slug, shot_id) / f"{comfly_id}.png"
        self.validator.ensure_file(path, comfly_id)
        return FileResponse(path)

    def approve_shot(self, collection: str, slug: str, shot_id: str, comfly_id: str) -> Dict[str, Any]:
        meta = self.shot_manager.get_shot(collection, slug, shot_id)
        target = self.validator.ensure_variant(meta["images"], comfly_id, "generated")
        for img in meta["images"]:
            if img["status"] == "approved": img["status"] = "generated"
        target["status"] = "approved"
        self.repo.write_json(self.shot_manager._shot_dir(collection, slug, shot_id) / "metadata.json", meta)
        return {"images": meta["images"]}

    def delete_variant(self, collection: str, slug: str, shot_id: str, comfly_id: str) -> Dict[str, Any]:
        meta = self.shot_manager.get_shot(collection, slug, shot_id)
        self.validator.ensure_variant(meta["images"], comfly_id)
        
        shot_dir = self.shot_manager._shot_dir(collection, slug, shot_id)
        file_path = shot_dir / f"{comfly_id}.png"
        if file_path.exists(): file_path.unlink()
        
        meta["images"] = [img for img in meta["images"] if img["id"] != comfly_id]
        self.repo.write_json(shot_dir / "metadata.json", meta)
        return {"images": meta["images"]}
