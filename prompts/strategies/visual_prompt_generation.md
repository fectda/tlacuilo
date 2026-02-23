# Strategy: Visual Prompt Generation (Ixtli – From Image)

## Objective
Analyze a real hardware photograph and generate a precise `visual_prompt` that describes the **subject and technique** for ComfyUI. The aesthetic (background color, lighting style, aspect ratio) is hard-coded in the ComfyUI workflow and must NOT be described in the output.

## Context You Will Receive
The backend will provide:
- **`description`**: The shot's intended technical description (from `metadata.json`).
- **`focus`**: The single physical protagonist (e.g., "PCM5102A DAC chip solder joints").
- **`atmosphere`**: The lighting atmosphere: `rojo` | `turquesa` | `ambar`.
- **Image**: The actual `original.png` photograph for visual analysis.

## Your Analysis Protocol
1. **Identify the Subject**: Confirm that the photo contains the component described in `focus`. If it does not match, flag the discrepancy.
2. **Describe the Object (Not the Aesthetic)**: Write a technical description of the physical object — its geometry, material, size relative to surrounding components, visible labels, pins, traces.
3. **Describe the Technique**: Based on `atmosphere`, specify the lighting angle and intensity that best serves the `focus`. Do NOT describe the background or artistic style — those are fixed in the workflow.

## Atmosphere → Technique Mapping
| Atmosphere | Technique |
|---|---|
| `rojo` | Warm rim lighting from the left, 15° elevation. Hard shadows. |
| `turquesa` | Cold rim lighting from the upper right. Soft gradient falloff. |
| `ambar` | Warm overhead fill. Slight diffusion for organic textures. |

## Output Format
Return ONLY the `visual_prompt` string. One paragraph. No JSON, no markdown, no explanations.

**Example**:
`Close-up photographic study of a PCM5102A I2S DAC chip surface-mounted on a green PCB. Silver solder joints on QFN-28 package. Micro gold traces visible along the board edge. Subject fills 60% of the frame. Cold rim lighting from upper right, catchlights on chip surface.`

## Guardrails
- **Never describe the background** (it is always `#050505`).
- **Never suggest removing or replacing components**.
- **Never describe a component that is not physically visible in the photograph**.
