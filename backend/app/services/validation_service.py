import re
import frontmatter
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ValidationService:
    def validate_schema(self, content: str, collection: Optional[str] = None) -> Optional[str]:
        """Validates Frontmatter Schema and Structural Headers. Returns error message or None."""
        if not content.strip(): return "Content cannot be empty"
        if not content.strip().startswith("---"): return "Invalid Markdown: Missing frontmatter"
        
        try:
            post = frontmatter.loads(content)
            required_keys = ["title", "description", "draft"]
            missing_keys = [k for k in required_keys if k not in post.metadata]
            if missing_keys: return f"Missing metadata keys: {missing_keys}"
            
            # Structural Header Check
            if collection:
                header_mapping = []
                if collection in ["atoms", "bits"]:
                    header_mapping = [
                        ["El Desafío", "The Challenge"],
                        ["La Solución", "The Solution", "Agent Orchestration"],
                        ["Proceso de Armado", "Build Process", "The Assembly", "Assembly Process", "Engineering and Refactoring"],
                        ["Retos y Aprendizajes", "Challenges and Lessons", "Lessons Learned", "The Intervention"],
                        ["Veredicto", "Verdict"]
                    ]
                elif collection == "mind":
                    header_mapping = [
                        ["La Premisa", "The Premise"],
                        ["El Argumento", "The Argument"],
                        ["La Aplicación", "The Application"],
                        ["La Conclusión", "The Conclusion"]
                    ]
                
                missing_headers = []
                lines = content.split("\n")
                header_lines = [line.strip().lower() for line in lines if line.strip().startswith("#")]
                
                for alternatives in header_mapping:
                    found = False
                    for alt in alternatives:
                        alt_lower = alt.lower()
                        if any(alt_lower in h_line for h_line in header_lines):
                            found = True
                            break
                    if not found:
                        missing_headers.append(alternatives[0])
                
                if missing_headers:
                    return f"Missing required sections: {missing_headers}"

        except Exception as e:
            return f"Validation error: {str(e)}"
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
        
        # 2. Handle redundant/triple separators at start
        # If it starts with multiple --- blocks, collapse or remove the empty ones
        while candidate.startswith("---") and candidate[3:].strip().startswith("---"):
            # Remove the first --- and any whitespace until the next one
            candidate = candidate[3:].strip()

        # 3. Repair missing opening --- if title: exists
        if not candidate.startswith("---") and candidate.startswith("title:"):
            candidate = "---\n" + candidate
            
        # 4. Handle Preamble and later separators
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
