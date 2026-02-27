# Task Directive
Analyze the provided generated headers against the required template structure.

# Required Template Structure
{template_content}

# Actually Generated Headers
{generated_headers}

# Evaluation Criteria
Does the logical flow and meaning of the "Actually Generated Headers" sufficiently cover ALL the key sections implied by the "Required Template Structure"?
- Look for semantic equivalents (e.g., "The Problem" covers "Challenge", "How we built it" covers "Implementation/Solution").
- Ignore exact word matching; focus on the presence of the required narrative milestones.

# Mandatory Output Contract
You must respond with ONLY a single JSON object. No preamble, no formatting blocks.

If the structure is VALID and complete, return EXACTLY:
{"valid": true, "error": ""}

If the structure is INVALID (missing key concepts), return EXACTLY:
{"valid": false, "error": "Missing section describing [Concept X] and [Concept Y]"}
