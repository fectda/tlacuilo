# Definición de Flujos de Trabajo (Workflows)

Documentación técnica de los procesos de creación de contenido y generación de imágenes.

## 1. Estructura de Contenido y Carpetas

### Jerarquía
El portafolio se organiza en tres colecciones principales:
1.  **`atoms`** (Hardware)
2.  **`bits`** (Software)
3.  **`mind`** (Ensayos/Visiones)

### Sistema de Archivos
-   **Contenido (Markdown)**: `src/content/{coleccion}/{idioma}/{slug}.md`
    -   Idioma primario: `es` (Español).
    -   Idioma secundario: `en` (Inglés, generado automáticamente).
-   **Imágenes (Assets)**: `public/{coleccion}/{slug}/`
    -   Nota: `mind` no usa carpeta de imágenes por defecto.

## 2. Flujo de Creación de Contenido (Agente: El Arquitecto)

### Fase A: Inicialización
1.  Selección de Tipo (`atoms` | `bits` | `mind`).
2.  Si es **Nuevo**: Se inicia con plantilla en blanco.
3.  Si es **Existente**: Carga `.md` y el historial de chat persistente.

### Fase B: Entrevista (Loop Iterativo)
El agente dialoga con el usuario para llenar la estructura narrativa específica:
-   **Atoms/Bits (STAR)**: Situación, Tarea, Acción, Resultado. (Datos duros).
-   **Mind (Manifiesto)**: Premisa, Argumento, Praxis, Conclusión. (Reflexión).

### Fase C: Generación y Pulido
1.  **Draft**: El agente escribe el `.md`.
2.  **Edición Manual**: El usuario refina el texto.
3.  **Normalización**: El agente revisa ortografía y estilo final.
4.  **Traducción**: Generación automática de `en/`.

### Fase D: Despliegue
1.  **Git Commit**: Cambios se guardan localmente.
2.  **Git Push**: Despliegue al repositorio remoto.

## 3. Flujo de Generación de Imágenes (Agente: Tlacuilo)

### Objetivo
Estilizar fotografías reales para cumplir la estética "Obsidiana Telemetría" manteniendo la geometría del objeto.
> **Referencia**: Ver Códice de Imagen en `prompts/tlacuilo_ixtli.md` (Definido en `docs/NARRATIVE.md`).

### Pipeline ComfyUI
El sistema orquesta un flujo complejo mediante WebSocket `ws://localhost:8188`:

1.  **Input**: Carga de imagen (Fotografía real de hardware). (Nodo `LoadImage`).
2.  **Análisis VLM**: JoyCaption analiza la imagen para entender el contexto. (Nodo `JoyCaption`).
3.  **Styling (Prompting)**:
    -   **Positivo**: "High fidelity photo editing, chiaroscuro lighting, matte black background #050505, industrial aesthetic".
    -   **Negativo**: "blurry, low quality, distorted, bright background".
4.  **Generación**: KSampler (Stable Diffusion 1.5/SDXL) procesa la imagen.
5.  **Output**: Imagen 1:1 (Canvas cuadrado) con contenido centrado.

### JSON Spec (`tlacuilo_v1_api.json`)
El sistema utiliza un mapa de nodos específico:
-   `Node 3`: KSampler (Seed, Steps, CFG).
-   `Node 6`: Positive Prompt.
-   `Node 10`: Load Image.
-   `Node 11`: JoyCaption (Analysis).
