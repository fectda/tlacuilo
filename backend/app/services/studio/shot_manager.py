import json
import re
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.repositories.project_repository import ProjectRepository
from app.services.validators.studio import StudioValidator
from app.services.prompt_service import PromptService
from app.clients.llm.ollama import OllamaClient

class StudioShotManager:
    def __init__(self, repo: ProjectRepository, validator: StudioValidator, 
                 prompts: PromptService, llm: OllamaClient):
        self.repo = repo
        self.validator = validator
        self.prompts = prompts
        self.llm = llm

    def _shot_dir(self, collection: str, slug: str, shot_id: str) -> Path:
        return self.repo.get_project_dir(collection, slug) / "shots" / shot_id

    def _derive_shot_status(self, meta: Dict[str, Any]) -> str:
        images = meta.get("images", [])
        if not images: return "pending_upload"
        statuses = [img.get("status") for img in images]
        if "approved" in statuses: return "approved"
        if "generated" in statuses: return "generated"
        if "queue" in statuses: return "queued"
        return "pending_upload"

    async def suggest_shots(self, collection: str, slug: str) -> List[Dict[str, Any]]:
        working_copy_path = self.repo.get_project_dir(collection, slug) / f"{slug}.md"
        content = self.repo.read_text(working_copy_path)
        if not content: raise ValueError("Project content empty.")

        strategy = self.prompts.get_shot_suggestion_strategy()
        raw = await self.llm.chat([{"role": "system", "content": strategy}, {"role": "user", "content": content}])
        
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        shots = json.loads(match.group(0)) if match else []

        created = []
        for shot in shots:
            shot_id = re.sub(r"[^\w\s-]", "", shot.get("title", "").lower()).strip().replace(" ", "-")
            if (self._shot_dir(collection, slug, shot_id)).exists(): continue
            metadata = {
                "shot_id": shot_id, "title": shot.get("title"), "description": shot.get("description"),
                "type": shot.get("type", "macro"), "focus": shot.get("focus"), "atmosphere": shot.get("atmosphere"),
                "images": []
            }
            self.repo.write_json(self._shot_dir(collection, slug, shot_id) / "metadata.json", metadata)
            created.append(metadata)
        return created

    def list_shots(self, collection: str, slug: str) -> List[Dict[str, Any]]:
        shots_dir = self.repo.get_project_dir(collection, slug) / "shots"
        if not shots_dir.exists(): return []
        result = []
        for d in sorted(shots_dir.iterdir()):
            if not d.is_dir(): continue
            meta = self.repo.read_json(d / "metadata.json") or {}
            result.append({
                "shot_id": d.name, "title": meta.get("title", d.name), "type": meta.get("type", ""),
                "status": self._derive_shot_status(meta), "has_original": (d / "original.png").exists(),
                "atmosphere": meta.get("atmosphere"),
            })
        return result

    def create_shot(self, collection: str, slug: str, title: str, description: str, 
                    type: str, focus: str, atmosphere: str) -> Dict[str, Any]:
        shot_id = re.sub(r"[^\w\s-]", "", title.lower()).strip().replace(" ", "-")
        shot_dir = self._shot_dir(collection, slug, shot_id)
        if shot_dir.exists(): raise ValueError(f"Shot '{shot_id}' already exists.")
        metadata = {
            "shot_id": shot_id, "title": title, "description": description,
            "type": type or "macro", "focus": focus, "atmosphere": atmosphere, "images": []
        }
        self.repo.write_json(shot_dir / "metadata.json", metadata)
        return {"shot_id": shot_id, "status": "created"}

    def get_shot(self, collection: str, slug: str, shot_id: str) -> Dict[str, Any]:
        meta = self.repo.read_json(self._shot_dir(collection, slug, shot_id) / "metadata.json")
        return self.validator.ensure_shot(meta, shot_id)

    def update_shot(self, collection: str, slug: str, shot_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        meta = self.get_shot(collection, slug, shot_id)
        for key in ["title", "description", "type", "focus", "atmosphere"]:
            if key in updates: meta[key] = updates[key]
        self.repo.write_json(self._shot_dir(collection, slug, shot_id) / "metadata.json", meta)
        return {"shot_id": shot_id, "status": "updated"}

    def delete_shot(self, collection: str, slug: str, shot_id: str):
        shutil.rmtree(self._shot_dir(collection, slug, shot_id))
