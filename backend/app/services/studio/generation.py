import random
import base64
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from app.repositories.project_repository import ProjectRepository
from app.services.validators.studio import StudioValidator
from app.clients.comfyui import ComfyUIClient
from app.clients.llm.ollama import OllamaClient
from app.services.prompt_service import PromptService
from app.core.config import settings
from app.services.studio.shot_manager import StudioShotManager

logger = logging.getLogger(__name__)

class StudioGenerationService:
    def __init__(self, repo: ProjectRepository, validator: StudioValidator, 
                 comfy: ComfyUIClient, llm: OllamaClient, prompts: PromptService,
                 shot_manager: StudioShotManager):
        self.repo = repo
        self.validator = validator
        self.comfy = comfy
        self.llm = llm
        self.prompts = prompts
        self.shot_manager = shot_manager

    async def upload_and_generate(self, collection: str, slug: str, shot_id: str, image_bytes: bytes) -> Dict[str, Any]:
        meta = self.shot_manager.get_shot(collection, slug, shot_id)
        if not meta.get("focus") or not meta.get("atmosphere"):
            raise ValueError("Shot must have 'focus' and 'atmosphere' defined.")

        shot_dir = self.shot_manager._shot_dir(collection, slug, shot_id)
        shot_dir.mkdir(parents=True, exist_ok=True)
        original_path = shot_dir / "original.png"
        with open(original_path, "wb") as f: f.write(image_bytes)

        # Execute VLM Task with Centralized Logging
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_path = shot_dir / f"{ts}_vlm_generate_history.json"
        
        user_content = f"DESCRIPTION: {meta.get('description')}\nFOCUS: {meta['focus']}\nGenerate hardware visual_prompt."
        visual_prompt = await self._execute_vlm_task(
            original_path, self.prompts.get_visual_prompt_generation_strategy(),
            user_content, log_path
        )

        server_fn = await self.comfy.upload_image(original_path)
        node6_prompt = self._assemble_prompt(visual_prompt, meta["atmosphere"], meta.get("type", "macro"))
        prompt_id = await self.comfy.enqueue_workflow(self.comfy.build_generate_workflow(node6_prompt, server_fn, random.randint(0, 2**32-1)))

        meta["images"].append({"id": prompt_id, "status": "queue"})
        self.repo.write_json(shot_dir / "metadata.json", meta)
        return {"images": meta["images"]}

    async def correct_shot(self, collection: str, slug: str, shot_id: str, instruction: str, comfly_id: str) -> Dict[str, Any]:
        meta = self.shot_manager.get_shot(collection, slug, shot_id)
        self.validator.ensure_variant(meta["images"], comfly_id, "generated")
        shot_dir = self.shot_manager._shot_dir(collection, slug, shot_id)
        base_path = shot_dir / f"{comfly_id}.png"
        self.validator.ensure_file(base_path, comfly_id)

        # Execute VLM Task with Centralized Logging
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_path = shot_dir / f"{ts}_vlm_refine_history.json"

        user_content = f"CORRECTION INSTRUCTION:\n{instruction}"
        refined_prompt = await self._execute_vlm_task(
            base_path, self.prompts.get_vlm_visual_refinement_strategy(),
            user_content, log_path
        )

        server_fn = await self.comfy.upload_image(base_path)
        node6_prompt = self._assemble_prompt(refined_prompt, meta.get("atmosphere", "turquesa"), meta.get("type", "macro"))
        prompt_id = await self.comfy.enqueue_workflow(self.comfy.build_correct_workflow(node6_prompt, server_fn, random.randint(0, 2**32-1)))

        meta["images"].append({"id": prompt_id, "status": "queue"})
        self.repo.write_json(shot_dir / "metadata.json", meta)
        return {"images": meta["images"]}

    async def poll_status(self, collection: str, slug: str, shot_id: str) -> Dict[str, Any]:
        meta = self.shot_manager.get_shot(collection, slug, shot_id)
        shot_dir = self.shot_manager._shot_dir(collection, slug, shot_id)
        updated = False
        for img in list(meta["images"]):
            if img["status"] != "queue": continue
            try:
                status = await self.comfy.get_status(img["id"])
                if status["status"] == "completed":
                    outputs = status.get("outputs", {})
                    for node_id, node_output in outputs.items():
                        if "images" in node_output:
                            for i in node_output["images"]:
                                await self.comfy.download_image(i["filename"], i.get("subfolder", ""), i.get("type", "output"), shot_dir / f"{img['id']}.png")
                                img["status"] = "generated"
                                updated = True
                                break
                        if updated: break
            except Exception as e:
                logger.error(f"Polling error for {img['id']}: {e}")
                img["status"] = "error"
                updated = True
        if updated: self.repo.write_json(shot_dir / "metadata.json", meta)
        return {"images": meta["images"]}

    def _assemble_prompt(self, visual_prompt: str, atmosphere: str, shot_type: str) -> str:
        base = self.prompts.get_ixtli_base()
        type_p = self.prompts.get_ixtli_type(shot_type)
        atm_p = self.prompts.get_ixtli_atm(atmosphere)
        qual_p = self.prompts.get_ixtli_quality()
        return f"{base} {type_p} {visual_prompt} {atm_p} {qual_p}"

    async def _execute_vlm_task(self, image_path: Path, strategy: str, user_content: str, log_path: Path) -> str:
        with open(image_path, "rb") as f: b64 = base64.b64encode(f.read()).decode('utf-8')
        # We delegate the logging to the OllamaClient
        return await self.llm.chat(
            [{"role": "system", "content": strategy}, {"role": "user", "content": user_content, "images": [b64]}], 
            model_override=settings.VISION_MODEL,
            debug_path=log_path
        )
