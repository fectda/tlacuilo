# Explicación de Flujos ComfyUI: Ixtli Suite (Flux Edition)

Este documento detalla la lógica y el encadenamiento de nodos de los flujos **Ixtli**, optimizados para la generación de activos visuales de hardware con estética "Obsidiana" utilizando modelos **Flux**.

---

## 1. Ixtli Generate (`ixtli_generate.json`)
**Objetivo:** Transformar una fotografía real en una variante publicitaria premium, extendiendo el lienzo y aplicando el estilo visual del proyecto.

### Estructura del Flujo (7 Pasos Clave)

| Paso | Nodo / Grupo | Función | Razón Técnica |
| :--- | :--- | :--- | :--- |
| **1. Entrada** | `LoadImage` (ID 1) | Carga la foto original. | Punto de inyección para el backend (Shot original). |
| **2. Limpieza Inicial** | `RMBG` (ID 84) | Elimina el fondo original. | Aísla el hardware para que el proceso de "Outpainting" no se contamine con el entorno real. |
| **3. Reencuadre** | `image resize` (ID 66) | Escala y añade padding. | Prepara la imagen para una composición 3:2 o 16:9, añadiendo espacio vacío para generar contexto. |
| **4. Extensión** | `extiende la imagen` (ID 55) | Generación Flux (Inpaint). | Rellena las áreas de padding con texturas coherentes, integrando el objeto en un plano infinito. |
| **5. Purificación** | `RMBG` (ID 82) | Segunda eliminación de fondo. | Asegura que el hardware extendido esté perfectamente recortado antes de la estilización final. |
| **6. Estilización** | `genera el modelo` (ID 86) | **Core Flux Generation**. | Nodo crítico donde se inyecta el "Visual Prompt" (Obsidiana, Ámbar, etc.) para crear la imagen final. |
| **7. Salida** | `SaveImage` (ID 87) | Almacenamiento. | Guarda el resultado con el prefijo `tlacuilo` para su sincronización. |

---

## 2. Ixtli Correct (`ixtli_correct.json`)
**Objetivo:** Refinar detalles técnicos o estéticos sobre una imagen ya generada, omitiendo pasos de redimensionado o extensión.

### Estructura del Flujo (4 Pasos Clave)

| Paso | Nodo | Función | Razón Técnica |
| :--- | :--- | :--- | :--- |
| **1. Entrada** | `LoadImage` (ID 1) | Carga la variante previa. | Permite iterar sobre lo ya generado. |
| **2. Aislamiento** | `RMBG` (ID 82) | Limpieza de máscara. | Garantiza que la corrección se centre únicamente en el objeto y no en el espacio negativo. |
| **3. Refinado** | `genera el modelo` (ID 86) | Re-generación Flux. | Aplica el modelo Flux con un prompt de ajuste para corregir texturas, luces o fallos menores. |
| **4. Salida** | `SaveImage` (ID 87) | Almacenamiento final. | Guarda la versión definitiva con el prefijo `Ixtli_Corrected`. |

---

## Especificaciones del Modelo
- **Motor de Inferencia:** Flux (utilizando subgrafos para encapsular complejidad).
- **Checkpoints:** `flux-2-klein-9b-nvfp4.safetensors` (modelo base de alta fidelidad).
- **VLM Encoder:** `qwen_3_8b_fp8mixed.safetensors`.
- **Pre-procesado:** `RMBG-2.0` para una segmentación quirúrgica del hardware.

## Contrato de Inyección (Backend)
Para controlar estos flujos vía API, el backend debe inyectar datos en:
- **Prompt:** Nodo ID 86 (o 55), input `text`.
- **Imagen:** Nodo ID 1, input `upload`.
- **Semilla:** Nodo ID 86, input `noise_seed`.

