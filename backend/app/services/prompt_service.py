import logging
from pathlib import Path
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class PromptService:
    def __init__(self):
        self.prompts_path = settings.PROMPTS_PATH

    def load_prompt(self, path: Path) -> str:
        if path.exists():
            return path.read_text()
        logger.warning(f"Prompt file not found: {path}")
        return ""

    def get_system_prompt(self, collection: str, slug: str, project_content: str) -> str:
        path = self.prompts_path / "system" / "tlacuilo_digital.md"
        content = self.load_prompt(path)
        return content.replace("{collection}", collection).replace("{slug}", slug).replace("{project_content}", project_content)

    def get_strategy_prompt(self, collection: str) -> str:
        strategy_file = "atoms_bits_strategy.md" if collection in ["atoms", "bits"] else "mind_strategy.md"
        path = self.prompts_path / "strategies" / strategy_file
        return self.load_prompt(path)

    def get_draft_strategy(self) -> str:
        path = self.prompts_path / "strategies" / "draft_generation.md"
        return self.load_prompt(path)

    def get_global_system_prompt(self, collection: str, slug: str, project_content: str) -> str:
        path = self.prompts_path / "system" / "tlacuilo_global.md"
        content = self.load_prompt(path)
        return content.replace("{collection}", collection).replace("{slug}", slug).replace("{project_content}", project_content)

    def get_translation_strategy(self) -> str:
        path = self.prompts_path / "strategies" / "english_translation.md"
        return self.load_prompt(path)

    def get_correction_strategy(self) -> str:
        path = self.prompts_path / "strategies" / "english_correction.md"
        return self.load_prompt(path)

    def get_shot_suggestion_strategy(self) -> str:
        path = self.prompts_path / "strategies" / "shot_suggestion.md"
        return self.load_prompt(path)

    def get_visual_prompt_generation_strategy(self) -> str:
        path = self.prompts_path / "strategies" / "visual_prompt_generation.md"
        return self.load_prompt(path)

    def get_visual_prompt_correction_strategy(self) -> str:
        path = self.prompts_path / "strategies" / "visual_prompt_correction.md"
        return self.load_prompt(path)

    def get_translator_prompt(self) -> str:
        path = self.prompts_path / "system" / "translator.md"
        return self.load_prompt(path)

    def get_ixtli_base(self) -> str:
        path = self.prompts_path / "strategies" / "ixtli" / "base.md"
        return self.load_prompt(path).strip()

    def get_ixtli_type(self, shot_type: str) -> str:
        path = self.prompts_path / "strategies" / "ixtli" / f"type_{shot_type}.md"
        return self.load_prompt(path).strip()

    def get_ixtli_atm(self, atmosphere: str) -> str:
        path = self.prompts_path / "strategies" / "ixtli" / f"atm_{atmosphere}.md"
        return self.load_prompt(path).strip()

    def get_ixtli_quality(self) -> str:
        path = self.prompts_path / "strategies" / "ixtli" / "quality.md"
        return self.load_prompt(path).strip()
