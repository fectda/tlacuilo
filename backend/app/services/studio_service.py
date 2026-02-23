import json
import re
import logging
import shutil
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.repositories.project_repository import ProjectRepository
from app.clients.llm.ollama import OllamaClient
from app.clients.comfyui import ComfyUIClient
from app.services.prompt_service import PromptService

logger = logging.getLogger(__name__)

VALID_ATMOSPHERES = ["rojo", "turquesa", "ambar"]
VALID_TYPES = ["macro", "context", "conceptual"]

# Obsidiana Telemetría — atmosphere suffixes as per architecture spec
ATMOSPHERE_SUFFIXES = {
    "rojo": "hard rim light from the left at 15° elevation, deep crimson #D4442F cast on metal edges and seams, specular hot spot on dominant surface, hard shadows fall right",
    "turquesa": "cold rim light upper-right at 30°, teal #00A6B6 glaze on curved surfaces and labels, soft catchlights, gradient falloff to black",
    "ambar": "warm overhead fill at 45°, amber diffusion on organic textures, gentle specular bloom, minimal hard shadows",
}
FIXED_SUFFIX = "cinematic square composition, subject in central 3:2 horizontal band, matte black negative space top and bottom, 8k ultra-sharp, technical photography, no geometry alteration"


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
        data["updated_at"] = datetime.now().isoformat()
        if "created_at" not in data:
            data["created_at"] = data["updated_at"]
        self.repo.write_json(shot_dir / "metadata.json", data)

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

        # Extract JSON array from the response
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
                continue  # Skip duplicates

            metadata = {
                "shot_id": shot_id,
                "title": title,
                "description": shot.get("description", ""),
                "type": shot.get("type", "macro"),
                "focus": shot.get("focus", ""),
                "atmosphere": shot.get("atmosphere", "turquesa"),
                "status": "pending_upload",
                "visual_prompt": None,
                "prompt_id": None,
                "approved_filename": None,
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
                "status": meta.get("status", "pending_upload"),
                "has_original": (shot_dir / "original.png").exists(),
                "visual_prompt": meta.get("visual_prompt"),
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
            "status": "pending_upload",
            "visual_prompt": None,
            "prompt_id": None,
            "approved_filename": None,
        }
        self._save_shot_metadata(collection, slug, shot_id, metadata)
        return {"shot_id": shot_id, "status": "created"}

    def get_shot(self, collection: str, slug: str, shot_id: str) -> Dict[str, Any]:
        meta = self._load_shot_metadata(collection, slug, shot_id)
        if meta is None:
            raise FileNotFoundError(f"Shot '{shot_id}' not found.")
        return meta

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

        # 1. Save original image
        shot_dir = self._shot_dir(collection, slug, shot_id)
        shot_dir.mkdir(parents=True, exist_ok=True)
        original_path = shot_dir / "original.png"
        with open(original_path, "wb") as f:
            f.write(image_bytes)

        # 2. Generate visual_prompt via Ixtli (Vision LLM)
        visual_prompt = await self._generate_visual_prompt(
            image_path=original_path,
            description=meta.get("description", ""),
            focus=meta["focus"],
            atmosphere=meta["atmosphere"]
        )

        # 3. Build workflow and enqueue in ComfyUI
        seed = random.randint(0, 2**32 - 1)
        node6_prompt = self._assemble_node6_prompt(visual_prompt, meta["atmosphere"])
        workflow = self.comfy.build_generate_workflow(
            visual_prompt=node6_prompt,
            original_image_path=str(original_path),
            seed=seed
        )
        prompt_id = await self.comfy.enqueue_workflow(workflow)

        # 4. Update metadata
        meta.update({
            "status": "queued",
            "visual_prompt": visual_prompt,
            "prompt_id": prompt_id,
        })
        self._save_shot_metadata(collection, slug, shot_id, meta)

        return {"prompt_id": prompt_id, "status": "queued", "visual_prompt": visual_prompt}

    async def correct_shot(self, collection: str, slug: str, shot_id: str,
                           instruction: str) -> Dict[str, Any]:
        """Refine visual_prompt and re-enqueue ComfyUI using the last generated image."""
        meta = self._load_shot_metadata(collection, slug, shot_id)
        if meta is None:
            raise FileNotFoundError(f"Shot '{shot_id}' not found.")

        if meta.get("status") != "generated":
            raise ValueError("Shot must be in 'generated' status to apply corrections.")

        previous_prompt = meta.get("visual_prompt", "")

        # Refine visual_prompt with instruction
        refined_prompt = await self._refine_visual_prompt(previous_prompt, instruction)

        # Find last generated image in the shot directory
        shot_dir = self._shot_dir(collection, slug, shot_id)
        generated_images = sorted(shot_dir.glob("generated_*.png"), reverse=True)
        if not generated_images:
            raise ValueError("No generated image found to use as base for correction.")
        base_image = generated_images[0]

        # Re-enqueue with correct workflow
        seed = random.randint(0, 2**32 - 1)
        node6_prompt = self._assemble_node6_prompt(refined_prompt, meta.get("atmosphere", "turquesa"))
        workflow = self.comfy.build_correct_workflow(
            visual_prompt=node6_prompt,
            base_image_path=str(base_image),
            seed=seed
        )
        prompt_id = await self.comfy.enqueue_workflow(workflow)

        meta.update({
            "status": "queued",
            "visual_prompt": refined_prompt,
            "prompt_id": prompt_id,
        })
        self._save_shot_metadata(collection, slug, shot_id, meta)

        return {"prompt_id": prompt_id, "status": "queued", "visual_prompt": refined_prompt}

    def approve_shot(self, collection: str, slug: str, shot_id: str, filename: str) -> Dict[str, Any]:
        """Mark a generated image as approved."""
        meta = self._load_shot_metadata(collection, slug, shot_id)
        if meta is None:
            raise FileNotFoundError(f"Shot '{shot_id}' not found.")
        if meta.get("status") != "generated":
            raise ValueError("Shot must be in 'generated' status to be approved.")

        meta["status"] = "approved"
        meta["approved_filename"] = filename
        self._save_shot_metadata(collection, slug, shot_id, meta)
        return {"status": "approved", "approved_file": filename}

    # -------------------------------------------------------------------------
    # Internal LLM helpers (No session / ephemeral)
    # -------------------------------------------------------------------------

    def _assemble_node6_prompt(self, visual_prompt: str, atmosphere: str) -> str:
        """Assemble the final Node 6 prompt: {visual_prompt}. {atmosphere_suffix}. {fixed_suffix}"""
        atm_suffix = ATMOSPHERE_SUFFIXES.get(atmosphere, "")
        return f"{visual_prompt}. {atm_suffix}. {FIXED_SUFFIX}"

    async def _generate_visual_prompt(self, image_path: Path, description: str, 
                                      focus: str, atmosphere: str) -> str:
        strategy = self.prompts.get_visual_prompt_generation_strategy()
        user_content = (
            f"DESCRIPTION: {description}\n"
            f"FOCUS (Protagonist Component): {focus}\n"
            f"ATMOSPHERE: {atmosphere}\n\n"
            f"Generate the visual_prompt for this hardware shot."
        )
        messages = [
            {"role": "system", "content": strategy},
            {"role": "user", "content": user_content}
        ]
        return (await self.llm.chat(messages)).strip()

    async def _refine_visual_prompt(self, previous_prompt: str, instruction: str) -> str:
        strategy = self.prompts.get_visual_prompt_correction_strategy()
        user_content = (
            f"PREVIOUS VISUAL PROMPT:\n{previous_prompt}\n\n"
            f"CORRECTION INSTRUCTION:\n{instruction}"
        )
        messages = [
            {"role": "system", "content": strategy},
            {"role": "user", "content": user_content}
        ]
        return (await self.llm.chat(messages)).strip()

    def _extract_json_array(self, text: str) -> Optional[List[Dict]]:
        """Extract a JSON array from the LLM response, even if wrapped in markdown."""
        try:
            # Try to extract from markdown code block first
            match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            # Fall back to direct parse
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
        return None
