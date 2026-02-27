# Task Directive
Analyze the provided generated headers against the required template structure.

# Target Language (CRITICAL)
The "Actually Generated Headers" MUST be written in the following language: {target_language}

# Required Template Structure
{template_content}

# Actually Generated Headers
{generated_headers}

# Evaluation Criteria
Does the logical flow and meaning of the "Actually Generated Headers" sufficiently cover ALL the key sections implied by the "Required Template Structure"?
- Look for semantic equivalents across languages (e.g., if target language is English, "The Problem" covers Spanish "Reto/Desafío").
- Ignore exact word matching; focus on the presence of the required narrative milestones.
- Ensure the generated headers are in the correct {target_language}.

# Mandatory Output Contract
You must respond with ONLY a single JSON object. No preamble, no formatting blocks.

If the structure is VALID and complete, return EXACTLY:
{"valid": true, "error": ""}

If the structure is INVALID (missing key concepts, or wrong language), return EXACTLY:
{"valid": false, "error": "Missing section [X] OR translated to wrong language (Expected: {target_language})"}
