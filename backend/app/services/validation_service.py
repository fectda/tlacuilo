import re
import frontmatter
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ValidationService:
    def validate_schema(self, content: str) -> Optional[str]:
        """Validates Frontmatter Schema. Returns error message or None."""
        if not content.strip(): return "Content cannot be empty"
        if not content.strip().startswith("---"): return "Invalid Markdown: Missing frontmatter"
        try:
            post = frontmatter.loads(content)
            required_keys = ["title", "description", "draft"]
            missing = [k for k in required_keys if k not in post.metadata]
            if missing: return f"Missing metadata keys: {missing}"
        except Exception as e:
            return f"Metadata parsing error: {str(e)}"
        return None

    def sanitize_draft(self, raw_content: str) -> str:
        """Cleans code blocks and repairs missing headers from LLM output."""
        candidate = raw_content.strip()
        
        # 1. Strip Code Blocks
        if candidate.startswith("```"):
            lines = candidate.split("\n")
            if lines[0].startswith("```"): lines = lines[1:]
            if lines and lines[-1].startswith("```"): lines = lines[:-1]
            candidate = "\n".join(lines).strip()
        
        # 2. Repair missing opening --- if title: exists
        if not candidate.startswith("---") and candidate.startswith("title:"):
            candidate = "---\n" + candidate
            
        # 3. Handle Preamble and later separators
        if "---" in candidate and not candidate.startswith("---"):
            idx = candidate.find("---")
            preamble = candidate[:idx].strip()
            if not preamble.startswith("title:"):
                candidate = candidate[idx:].strip()
            else:
                candidate = "---\n" + candidate
        
        return candidate

    def check_spelling(self, content: str) -> List[str]:
        # Placeholder for spellcheck logic
        return []
