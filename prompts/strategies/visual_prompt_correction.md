# Strategy: Visual Prompt Correction (Ixtli – Correction Loop)

## Objective
Refine an existing `visual_prompt` based on a user's correction instruction. The goal is a targeted, surgical edit — not a full rewrite.

## Context You Will Receive
- **`previous_visual_prompt`**: The current `visual_prompt` stored in `metadata.json`.
- **`instruction`**: The user's correction instruction (e.g., "make the chip fill more of the frame", "reduce blur on the connectors").

## Rules
1. **Preserve Hardware Accuracy**: Do not remove or change any physically observable detail from the `previous_visual_prompt` unless the instruction explicitly requests it.
2. **Targeted Edit**: Apply the minimum change necessary to satisfy the instruction. Do not rewrite the entire prompt.
3. **Aesthetic Constraints Remain Fixed**: Never add background descriptions, color palettes, or style references. Those are in the ComfyUI workflow.
4. **Language**: Output must be in English.

## Output Format
Return ONLY the refined `visual_prompt` string. One paragraph. No JSON, no markdown, no explanations.
