import json
import re
import logging
import shutil
import random
import base64
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi.responses import FileResponse

from app.core.config import settings
from app.repositories.project_repository import ProjectRepository
from app.clients.llm.ollama import OllamaClient
from app.clients.comfyui import ComfyUIClient
from app.services.prompt_service import PromptService

logger = logging.getLogger(__name__)

VALID_ATMOSPHERES = ["rojo", "turquesa", "ambar"]
VALID_TYPES = ["macro", "context", "conceptual"]

class StudioService:
    def __init__(self, repo: ProjectRepository, llm: OllamaClient, 
                 comfy: ComfyUIClient, prompts: PromptService):
        self.repo = repo
        self.llm = llm
        self.comfy = comfy
        self.prompts = prompts

    # -------------------------------------------------------------------------
    # Shot Directory Helpers
    # -------------------------------------------------------------------------

    def _shots_dir(self, collection: str, slug: str) -> Path:
        return self.repo.get_project_dir(collection, slug) / "shots"

    def _shot_dir(self, collection: str, slug: str, shot_id: str) -> Path:
        return self._shots_dir(collection, slug) / shot_id

    def _slugify(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        return re.sub(r"[\s_-]+", "-", text)

    def _shot_exists(self, collection: str, slug: str, shot_id: str) -> bool:
        return self._shot_dir(collection, slug, shot_id).exists()

    def _load_shot_metadata(self, collection: str, slug: str, shot_id: str) -> Optional[Dict[str, Any]]:
        shot_dir = self._shot_dir(collection, slug, shot_id)
        if not shot_dir.exists():
            return None
        return self.repo.read_json(shot_dir / "metadata.json") or {}

    def _save_shot_metadata(self, collection: str, slug: str, shot_id: str, data: Dict[str, Any]):
        shot_dir = self._shot_dir(collection, slug, shot_id)
        shot_dir.mkdir(parents=True, exist_ok=True)
        self.repo.write_json(shot_dir / "metadata.json", data)

    def _derive_shot_status(self, meta: Dict[str, Any]) -> str:
        """Derive the aggregate status of a shot from its images array."""
        images = meta.get("images", [])
        if not images:
            return "pending_upload"
        
        statuses = [img.get("status") for img in images]
        if "approved" in statuses:
            return "approved"
        if "generated" in statuses:
            return "generated"
        if "queue" in statuses:
            return "queued"
        
        return "pending_upload"

    # -------------------------------------------------------------------------
    # 1. CRUD de Shots
    # -------------------------------------------------------------------------

    async def suggest_shots(self, collection: str, slug: str) -> List[Dict[str, Any]]:
        """Use the LLM with shot_suggestion.md to analyze the project MD and create shot slots."""
        working_copy_path = self.repo.get_project_dir(collection, slug) / f"{slug}.md"
        content = self.repo.read_text(working_copy_path)
        if not content:
            raise ValueError("Project content not found or empty.")

        strategy = self.prompts.get_shot_suggestion_strategy()
        messages = [
            {"role": "system", "content": strategy},
            {"role": "user", "content": f"Analyze the following project document and generate a shot list:\n\n---\n{content}\n---"}
        ]

        raw = await self.llm.chat(messages)
        shots = self._extract_json_array(raw)
        if not shots:
            raise ValueError("LLM did not return a valid JSON array for shot suggestion.")

        created = []
        for shot in shots:
            title = shot.get("title", "").strip()
            if not title:
                continue
            shot_id = self._slugify(title)
            if self._shot_exists(collection, slug, shot_id):
                continue

            metadata = {
                "shot_id": shot_id,
                "title": title,
                "description": shot.get("description", ""),
                "type": shot.get("type", "macro"),
                "focus": shot.get("focus", ""),
                "atmosphere": shot.get("atmosphere", "turquesa"),
                "images": []
            }
            self._save_shot_metadata(collection, slug, shot_id, metadata)
            created.append(metadata)

        return created

    def list_shots(self, collection: str, slug: str) -> List[Dict[str, Any]]:
        """Scan the shots/ dir and return slim shot-list entries."""
        shots_dir = self._shots_dir(collection, slug)
        if not shots_dir.exists():
            return []

        result = []
        for shot_dir in sorted(shots_dir.iterdir()):
            if not shot_dir.is_dir():
                continue
            meta = self.repo.read_json(shot_dir / "metadata.json") or {}
            
            result.append({
                "shot_id": shot_dir.name,
                "title": meta.get("title", shot_dir.name),
                "type": meta.get("type", ""),
                "status": self._derive_shot_status(meta),
                "has_original": (shot_dir / "original.png").exists(),
                "atmosphere": meta.get("atmosphere"),
            })
        return result

    def create_shot(self, collection: str, slug: str, title: str, description: str, 
                    shot_type: str, focus: str, atmosphere: str) -> Dict[str, Any]:
        """Create a manual shot slot, validate inputs, return shot_id."""
        if not title:
            raise ValueError("title is required.")
        if not description or not description.strip():
            raise ValueError("description is required.")
        if not focus or not focus.strip():
            raise ValueError("focus is required.")
        if atmosphere not in VALID_ATMOSPHERES:
            raise ValueError(f"atmosphere must be one of: {VALID_ATMOSPHERES}")

        shot_id = self._slugify(title)
        if self._shot_exists(collection, slug, shot_id):
            raise ValueError(f"shot_id '{shot_id}' already exists.")

        metadata = {
            "shot_id": shot_id,
            "title": title,
            "description": description,
            "type": shot_type or "macro",
            "focus": focus,
            "atmosphere": atmosphere,
            "images": []
        }
        self._save_shot_metadata(collection, slug, shot_id, metadata)
        return {"shot_id": shot_id, "status": "created"}

    def get_shot(self, collection: str, slug: str, shot_id: str) -> Dict[str, Any]:
        meta = self._load_shot_metadata(collection, slug, shot_id)
        if meta is None:
            raise FileNotFoundError(f"Shot '{shot_id}' not found.")
        return meta

    def get_image(self, collection: str, slug: str, shot_id: str, comfly_id: str) -> FileResponse:
        """Find a variant in metadata and return the physical file via FileResponse."""
        meta = self._load_shot_metadata(collection, slug, shot_id)
        if meta is None:
            raise FileNotFoundError(f"Shot '{shot_id}' not found.")
        
        images = meta.get("images", [])
        img_meta = next((img for img in images if img.get("id") == comfly_id), None)
        if not img_meta:
            raise FileNotFoundError(f"Image variant '{comfly_id}' not found in metadata.")
        
        if img_meta.get("status") not in ["generated", "approved"]:
            raise ValueError(f"Image variant '{comfly_id}' is not ready or has an error.")
            
        shot_dir = self._shot_dir(collection, slug, shot_id)
        file_path = shot_dir / f"{comfly_id}.png"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Physical file for variant '{comfly_id}' missing from disk.")
            
        return FileResponse(file_path)

    def update_shot(self, collection: str, slug: str, shot_id: str, 
                    updates: Dict[str, Any]) -> Dict[str, Any]:
        meta = self._load_shot_metadata(collection, slug, shot_id)
        if meta is None:
            raise FileNotFoundError(f"Shot '{shot_id}' not found.")

        if "atmosphere" in updates and updates["atmosphere"] not in VALID_ATMOSPHERES:
            raise ValueError(f"atmosphere must be one of: {VALID_ATMOSPHERES}")
        if "focus" in updates and not (updates["focus"] or "").strip():
            raise ValueError("focus cannot be empty.")
        if "description" in updates and not (updates["description"] or "").strip():
            raise ValueError("description cannot be empty.")

        for key in ["title", "description", "type", "focus", "atmosphere"]:
            if key in updates and updates[key] is not None:
                meta[key] = updates[key]

        self._save_shot_metadata(collection, slug, shot_id, meta)
        return {"shot_id": shot_id, "status": "updated"}

    def delete_shot(self, collection: str, slug: str, shot_id: str):
        shot_dir = self._shot_dir(collection, slug, shot_id)
        if not shot_dir.exists():
            raise FileNotFoundError(f"Shot '{shot_id}' not found.")
        shutil.rmtree(shot_dir)

    # -------------------------------------------------------------------------
    # 2. Generation Pipeline
    # -------------------------------------------------------------------------

    async def upload_and_generate(self, collection: str, slug: str, shot_id: str,
                                  image_bytes: bytes) -> Dict[str, Any]:
        """Save original.png, call Vision LLM for visual_prompt, enqueue ComfyUI."""
        meta = self._load_shot_metadata(collection, slug, shot_id)
        if meta is None:
            raise FileNotFoundError(f"Shot '{shot_id}' not found.")

        if not meta.get("focus") or not meta.get("atmosphere"):
            raise ValueError("Shot must have 'focus' and 'atmosphere' defined before upload.")

        shot_dir = self._shot_dir(collection, slug, shot_id)
        shot_dir.mkdir(parents=True, exist_ok=True)
        original_path = shot_dir / "original.png"
        with open(original_path, "wb") as f:
            f.write(image_bytes)

        visual_prompt = await self._generate_visual_prompt(
            image_path=original_path,
            description=meta.get("description", ""),
            focus=meta["focus"]
        )

        server_filename = await self.comfy.upload_image(original_path)
        seed = random.randint(0, 2**32 - 1)
        node6_prompt = self._assemble_node6_prompt(visual_prompt, meta["atmosphere"], meta.get("type", "macro"))
        
        workflow = self.comfy.build_generate_workflow(
            visual_prompt=node6_prompt,
            server_filename=server_filename,
            seed=seed
        )
        prompt_id = await self.comfy.enqueue_workflow(workflow)

        if "images" not in meta or not isinstance(meta["images"], list):
            meta["images"] = []
        
        meta["images"].append({
            "id": prompt_id,
            "status": "queue"
        })
        self._save_shot_metadata(collection, slug, shot_id, meta)

        return {"images": meta["images"]}

    async def correct_shot(self, collection: str, slug: str, shot_id: str,
                           instruction: str, comfly_id: str) -> Dict[str, Any]:
        """Refine visual_prompt and re-enqueue ComfyUI using a specific generated image."""
        meta = self._load_shot_metadata(collection, slug, shot_id)
        if meta is None:
            raise FileNotFoundError(f"Shot '{shot_id}' not found.")

        images = meta.get("images", [])
        base_img_meta = next((img for img in images if img.get("id") == comfly_id), None)
        if not base_img_meta or base_img_meta.get("status") != "generated":
            raise ValueError(f"Image variant '{comfly_id}' not found or not in 'generated' state.")

        shot_dir = self._shot_dir(collection, slug, shot_id)
        refined_prompt = await self._refine_visual_prompt(instruction)

        base_image_path = shot_dir / f"{comfly_id}.png"
        if not base_image_path.exists():
            raise FileNotFoundError(f"Physical file for variant '{comfly_id}' missing.")

        server_filename = await self.comfy.upload_image(base_image_path)
        seed = random.randint(0, 2**32 - 1)
        node6_prompt = self._assemble_node6_prompt(refined_prompt, meta.get("atmosphere", "turquesa"), meta.get("type", "macro"))
        
        workflow = self.comfy.build_correct_workflow(
            visual_prompt=node6_prompt,
            server_filename=server_filename,
            seed=seed
        )
        prompt_id = await self.comfy.enqueue_workflow(workflow)

        meta["images"].append({
            "id": prompt_id,
            "status": "queue"
        })
        self._save_shot_metadata(collection, slug, shot_id, meta)

        return {"images": meta["images"]}

    def approve_shot(self, collection: str, slug: str, shot_id: str, comfly_id: str) -> Dict[str, Any]:
        """Mark a specific image variant (by comfly_id) as approved and revert others."""
        meta = self._load_shot_metadata(collection, slug, shot_id)
        if meta is None:
            raise FileNotFoundError(f"Shot '{shot_id}' not found.")
        
        images = meta.get("images", [])
        target = next((img for img in images if img.get("id") == comfly_id), None)
        if not target or target.get("status") != "generated":
            raise ValueError(f"Image variant '{comfly_id}' not found or not 'generated'.")

        for img in images:
            if img.get("status") == "approved":
                img["status"] = "generated"
        
        target["status"] = "approved"
        meta["images"] = images
        self._save_shot_metadata(collection, slug, shot_id, meta)
        return {"images": images}

    def delete_variant(self, collection: str, slug: str, shot_id: str, comfly_id: str) -> Dict[str, Any]:
        """Delete a specific image variant from disk and metadata."""
        meta = self._load_shot_metadata(collection, slug, shot_id)
        if meta is None:
            raise FileNotFoundError(f"Shot '{shot_id}' not found.")
        
        images = meta.get("images", [])
        idx = next((i for i, img in enumerate(images) if img.get("id") == comfly_id), -1)
        if idx == -1:
            raise FileNotFoundError(f"Image variant '{comfly_id}' not found.")
        
        shot_dir = self._shot_dir(collection, slug, shot_id)
        file_path = shot_dir / f"{comfly_id}.png"
        if file_path.exists():
            file_path.unlink()
        
        images.pop(idx)
        meta["images"] = images
        self._save_shot_metadata(collection, slug, shot_id, meta)
        return {"images": images}

    async def poll_status(self, collection: str, slug: str, shot_id: str) -> Dict[str, Any]:
        """Check status of all queued variants and download finished ones as {id}.png."""
        meta = self._load_shot_metadata(collection, slug, shot_id)
        if meta is None:
            raise FileNotFoundError(f"Shot '{shot_id}' not found.")
        
        images = meta.get("images", [])
        shot_dir = self._shot_dir(collection, slug, shot_id)
        updated = False

        for img_meta in list(images):
            if img_meta.get("status") != "queue":
                continue
            
            prompt_id = img_meta["id"]
            try:
                comfy_status = await self.comfy.get_status(prompt_id)
                if comfy_status["status"] == "completed":
                    outputs = comfy_status.get("outputs", {})
                    for node_id, node_output in outputs.items():
                        if "images" in node_output:
                            for img in node_output["images"]:
                                fn = img["filename"]
                                subf = img.get("subfolder", "")
                                f_type = img.get("type", "output")
                                dest = shot_dir / f"{prompt_id}.png"
                                await self.comfy.download_image(fn, subf, f_type, dest)
                                img_meta["status"] = "generated"
                                updated = True
                                break
                        if updated: break
            except Exception as e:
                logger.error(f"Error polling prompt {prompt_id}: {e}")
                img_meta["status"] = "error"
                updated = True

        if updated:
            meta["images"] = images
            self._save_shot_metadata(collection, slug, shot_id, meta)
            
        return {"images": images}

    # -------------------------------------------------------------------------
    # Internal LLM helpers (No session / ephemeral)
    # -------------------------------------------------------------------------

    def _assemble_node6_prompt(self, visual_prompt: str, atmosphere: str, shot_type: str) -> str:
        """Assemble the final Node 6 prompt using the strict Ixtli formula."""
        base = self.prompts.get_ixtli_base()
        t_mod = self.prompts.get_ixtli_type(shot_type)
        atm = self.prompts.get_ixtli_atm(atmosphere)
        quality = self.prompts.get_ixtli_quality()
        return f"{base} {t_mod} {visual_prompt} {atm} {quality}"

    async def _generate_visual_prompt(self, image_path: Path, description: str, 
                                      focus: str) -> str:
        strategy = self.prompts.get_visual_prompt_generation_strategy()
        user_content = f"DESCRIPTION: {description}\nFOCUS: {focus}\nGenerate hardware visual_prompt."
        
        with open(image_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode('utf-8')
            
        messages = [
            {"role": "system", "content": strategy},
            {"role": "user", "content": user_content, "images": [base64_image]}
        ]
        return (await self.llm.chat(messages, model_override=settings.VISION_MODEL)).strip()

    async def _refine_visual_prompt(self, instruction: str) -> str:
        strategy = self.prompts.get_visual_prompt_correction_strategy()
        user_content = f"CORRECTION INSTRUCTION:\n{instruction}"
        messages = [
            {"role": "system", "content": strategy},
            {"role": "user", "content": user_content}
        ]
        return (await self.llm.chat(messages)).strip()

    def _extract_json_array(self, text: str) -> Optional[List[Dict]]:
        try:
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
        return None
