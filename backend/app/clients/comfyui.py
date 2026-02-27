import httpx
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import json
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

    async def upload_image(self, image_path: Path) -> str:
        """Upload an image to ComfyUI and return the server filename."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                with open(image_path, "rb") as f:
                    files = {"image": (image_path.name, f, "image/png")}
                    response = await client.post(f"{self.host}/upload/image", files=files)
                    response.raise_for_status()
                    return response.json()["name"]
        except Exception as e:
            logger.error(f"Error uploading image to ComfyUI: {e}")
            raise Exception(f"ComfyUI upload error: {str(e)}")

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

    async def download_image(self, filename: str, subfolder: str, folder_type: str, dest_path: Path):
        """Download a generated image from ComfyUI and save to dest_path."""
        url = f"{self.host}/view?filename={filename}&subfolder={subfolder}&type={folder_type}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with open(dest_path, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)

    def build_generate_workflow(self, visual_prompt: str, server_filename: str, seed: int) -> Dict[str, Any]:
        """Build and inject values into the ixtli_generate_api workflow."""
        workflow_path = settings.PROMPTS_PATH / ".." / "workflows" / "ixtli_generate_api.json"
        if not workflow_path.exists():
            raise FileNotFoundError(f"Workflow not found: {workflow_path}")
        with open(workflow_path) as f:
            workflow = json.load(f)

        # Inject dynamic values per demo script
        if "1" in workflow:
            workflow["1"]["inputs"]["image"] = server_filename
        if "86:74" in workflow:
            workflow["86:74"]["inputs"]["text"] = visual_prompt
        
        # Seeds
        if "55:73" in workflow:
            workflow["55:73"]["inputs"]["noise_seed"] = seed
        if "86:73" in workflow:
            workflow["86:73"]["inputs"]["noise_seed"] = seed

        return workflow

    def build_correct_workflow(self, visual_prompt: str, server_filename: str, seed: int) -> Dict[str, Any]:
        """Build and inject values into the ixtli_correct_api workflow."""
        workflow_path = settings.PROMPTS_PATH / ".." / "workflows" / "ixtli_correct_api.json"
        if not workflow_path.exists():
            raise FileNotFoundError(f"Workflow not found: {workflow_path}")
        with open(workflow_path) as f:
            workflow = json.load(f)

        # Inject dynamic values per demo script
        if "1" in workflow:
            workflow["1"]["inputs"]["image"] = server_filename
        if "86:74" in workflow:
            workflow["86:74"]["inputs"]["text"] = visual_prompt
            
        # Refiner seed to force variation
        if "86:73" in workflow:
            workflow["86:73"]["inputs"]["noise_seed"] = seed

        return workflow
