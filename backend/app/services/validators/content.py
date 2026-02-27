import frontmatter
from typing import List, Dict, Any, Optional

class ContentValidator:
    def validate_schema(self, content: str, collection: Optional[str] = None) -> Optional[str]:
        """Validates Frontmatter Schema and Structural Headers."""
        if not content.strip(): return "Content cannot be empty"
        if not content.strip().startswith("---"): return "Invalid Markdown: Missing frontmatter"
        
        try:
            post = frontmatter.loads(content)
            required_keys = ["title", "description", "draft"]
            missing_keys = [k for k in required_keys if k not in post.metadata]
            if missing_keys: return f"Missing metadata keys: {missing_keys}"
            
            if collection:
                header_mapping = []
                if collection in ["atoms", "bits"]:
                    header_mapping = [
                        ["El Desafío", "The Challenge"],
                        ["La Solución", "The Solution"],
                        ["Proceso de Armado", "Build Process"],
                        ["Retos y Aprendizajes", "Challenges and Lessons"],
                        ["Veredicto", "Verdict"]
                    ]
                elif collection == "mind":
                    header_mapping = [
                        ["La Premisa", "The Premise"],
                        ["El Argumento", "The Argument"],
                        ["La Aplicación", "The Application"],
                        ["La Conclusión", "The Conclusion"]
                    ]
                
                lines = content.split("\n")
                header_lines = [line.strip().lower() for line in lines if line.strip().startswith("#")]
                
                missing_headers = []
                for alternatives in header_mapping:
                    if not any(alt.lower() in h_line for alt in alternatives for h_line in header_lines):
                        missing_headers.append(alternatives[0])
                
                if missing_headers:
                    return f"Missing required sections: {missing_headers}"

        except Exception as e:
            return f"Validation error: {str(e)}"
        return None

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
