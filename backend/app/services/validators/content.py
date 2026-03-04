import frontmatter
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Required frontmatter fields per collection, derived from the Astro content schema.
# Fields with .optional() are excluded. Fields with .default() ARE included — defaults
# are a build-time concern for Astro, not an excuse to omit them from the source file.
COLLECTION_SCHEMAS: Dict[str, List[str]] = {
    "bits":  ["title", "description", "date", "stack", "status", "progress", "type"],
    "atoms": ["title", "shortTitle", "description", "date", "stack", "status", "type", "icon"],
    "mind":  ["title", "description", "date", "status"],
}

class ContentValidator:
    async def validate_all(self, content: str, collection: Optional[str] = None, 
                           llm_client: Optional[Any] = None, template_content: Optional[str] = None,
                           prompt_service: Optional[Any] = None, target_language: str = "Spanish",
                           debug_dir: Optional[Any] = None, log_prefix: str = "") -> Optional[str]:
        """Orchestrates all validation steps."""
        err = self.validate_frontmatter(content)
        if err: return err
        
        err = self.validate_metadata(content)
        if err: return err
        
        if collection and llm_client and template_content and prompt_service:
            err = await self.validate_semantic_structure(content, collection, llm_client, template_content, prompt_service, target_language, debug_dir, log_prefix)
            if err: return err
            
        return None

    def validate_frontmatter(self, content: str) -> Optional[str]:
        """Validates basic markdown structure."""
        if not content.strip(): return "Content cannot be empty"
        if not content.strip().startswith("---"): return "Invalid Markdown: Missing frontmatter"
        return None

    def validate_metadata(self, content: str, collection: str) -> Optional[str]:
        """Validates required frontmatter keys against the collection schema."""
        try:
            post = frontmatter.loads(content)
            required_keys = COLLECTION_SCHEMAS.get(collection, [])
            missing_keys = [k for k in required_keys if k not in post.metadata]
            if missing_keys:
                return f"Missing required fields for '{collection}': {missing_keys}"
        except Exception as e:
            return f"Frontmatter parse error: {str(e)}"
        return None

    async def validate_semantic_structure(self, content: str, collection: str, 
                                          llm_client: Any, template_content: str, 
                                          prompt_service: Any, target_language: str = "Spanish",
                                          debug_dir: Optional[Any] = None, log_prefix: str = "") -> Optional[str]:
        """Validates headers semantically using an LLM Judge."""
        lines = content.split("\n")
        h2_lines = [line.strip() for line in lines if line.strip().startswith("## ")]
        
        system_prompt = prompt_service.get_structural_validator_prompt()
        strategy_template = prompt_service.get_semantic_validation_strategy()
        
        generated_headers_str = "\n".join(h2_lines)
        strategy_prompt = strategy_template.format(
            template_content=template_content,
            generated_headers=generated_headers_str,
            target_language=target_language
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": strategy_prompt}
        ]
        
        judgment = await self._get_valid_llm_json(llm_client, messages, debug_dir, log_prefix)
        if judgment is None:
            return "LLM Validator failed to return valid JSON format after 3 attempts."
            
        if not judgment.get("valid"):
            return f"Semantic structure validation failed: {judgment.get('error', 'Unknown missing sections')}. Found headers: {h2_lines}"
            
        return None

    async def _get_valid_llm_json(self, llm_client: Any, messages: List[Dict[str, str]], 
                                  debug_dir: Optional[Any] = None, log_prefix: str = "") -> Optional[Dict[str, Any]]:
        """Handles the retry loop to ensure the LLM returns a valid JSON."""
        for attempt in range(3):
            try:
                debug_path = None
                if debug_dir:
                    import datetime
                    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    debug_path = debug_dir / f"{ts}_{log_prefix}val_at{attempt+1}_history.json"
                
                response_text = await llm_client.chat(messages, debug_path=debug_path)
                return self._parse_llm_json(response_text)
            except json.JSONDecodeError as json_e:
                logger.warning(f"LLM Validator returned invalid JSON (attempt {attempt+1}/3). Response: {response_text}")
                # Loop continues to retry
            except Exception as llm_e:
                logger.warning(f"LLM Validator exception: {llm_e}")
                break
        return None

    def _parse_llm_json(self, raw_response: str) -> Dict[str, Any]:
        """Cleans markdown blocks and parses JSON from the LLM response."""
        text = raw_response.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        return json.loads(text)

    def sanitize_draft(self, raw_content: str) -> str:
        """Cleans code blocks and repairs missing headers from LLM output."""
        candidate = raw_content.strip()
        if candidate.startswith("```"):
            lines = candidate.split("\n")
            if lines[0].startswith("```"): lines = lines[1:]
            if lines and lines[-1].startswith("```"): lines = lines[:-1]
            candidate = "\n".join(lines).strip()
        
        while candidate.startswith("---") and candidate[3:].strip().startswith("---"):
            candidate = candidate[3:].strip()

        if not candidate.startswith("---") and candidate.startswith("title:"):
            candidate = "---\n" + candidate
            
        return candidate

    def ensure_content(self, content: Optional[str], message: str = "Content is required"):
        if not content or not content.strip():
            raise ValueError(message)
