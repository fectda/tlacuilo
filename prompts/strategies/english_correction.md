# Strategy: English Correction (Validation Recovery)

## Objective
Correct a validation error in the English version of the document. The assistant must analyze the provided error and adjust the Markdown content without losing the technical context or the "Bilingual Scribe" tone.

## Instructions
1.  **Analyze the Validation Error**: A block labeled `## VALIDATION ERROR` will be provided at the end of the prompt. This contains the specific reasons why the previous draft was rejected (e.g., malformed Frontmatter, missing required headers, or incorrect `stack` format).
2.  **Apply Surgical Correction**: Fix ONLY the reported error. Ensure the rest of the content remains intact and professional.
3.  **Frontmatter Enforcement**:
    *   **Field `stack`**: Must use the inline array format: `stack: ["ESP32", "ESPHome"]`.
    *   **Keys**: Do not translate or modify YAML keys.
4.  **Language**: Maintain 100% US English.

## Mandatory Output
Your response must consist ONLY of the corrected Markdown code, starting with the Frontmatter separator `---`. Do not include any preambles, apologies, or explanations.
