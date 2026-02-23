import httpx
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

NEGATIVE_PROMPT = "blurry, low quality, bright background, distorted, unrealistic hardware, altered geometry, text, watermark"


class ComfyUIClient:
    def __init__(self):
        self.host = settings.COMFYUI_HOST

    async def enqueue_workflow(self, workflow: Dict[str, Any]) -> str:
        """Send a workflow to ComfyUI and return the prompt_id."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.host}/prompt", json={"prompt": workflow})
                response.raise_for_status()
                return response.json()["prompt_id"]
        except httpx.HTTPStatusError as e:
            logger.error(f"ComfyUI HTTP Error: {e.response.text}")
            raise Exception(f"ComfyUI Error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error calling ComfyUI: {e}")
            raise Exception(f"ComfyUI connection error: {str(e)}")

    async def get_status(self, prompt_id: str) -> Dict[str, Any]:
        """Poll the state of a generation from ComfyUI history."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{self.host}/history/{prompt_id}")
                response.raise_for_status()
                history = response.json()
                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    return {"status": "completed", "outputs": outputs}
                return {"status": "running"}
        except Exception as e:
            logger.error(f"Error polling ComfyUI: {e}")
            raise Exception(f"ComfyUI polling error: {str(e)}")

    async def download_image(self, filename: str, dest_path: Path):
        """Download a generated image from ComfyUI and save to dest_path."""
        url = f"{self.host}/view?filename={filename}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with open(dest_path, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)

    def build_generate_workflow(self, visual_prompt: str, original_image_path: str, seed: int) -> Dict[str, Any]:
        """Build and inject values into the ixtli_generate workflow."""
        workflow_path = settings.PROMPTS_PATH / ".." / "workflows" / "ixtli_generate.json"
        import json
        if not workflow_path.exists():
            raise FileNotFoundError(f"Workflow not found: {workflow_path}")
        with open(workflow_path) as f:
            workflow = json.load(f)

        # Inject dynamic values per Node Map (3.2 ARCHITECTURE)
        workflow["3"]["inputs"]["seed"] = seed
        workflow["6"]["inputs"]["text"] = visual_prompt
        workflow["7"]["inputs"]["text"] = NEGATIVE_PROMPT
        workflow["10"]["inputs"]["image"] = original_image_path
        return workflow

    def build_correct_workflow(self, visual_prompt: str, base_image_path: str, seed: int) -> Dict[str, Any]:
        """Build and inject values into the ixtli_correct workflow."""
        workflow_path = settings.PROMPTS_PATH / ".." / "workflows" / "ixtli_correct.json"
        import json
        if not workflow_path.exists():
            raise FileNotFoundError(f"Workflow not found: {workflow_path}")
        with open(workflow_path) as f:
            workflow = json.load(f)

        workflow["3"]["inputs"]["seed"] = seed
        workflow["6"]["inputs"]["text"] = visual_prompt
        workflow["7"]["inputs"]["text"] = NEGATIVE_PROMPT
        workflow["10"]["inputs"]["image"] = base_image_path
        return workflow
