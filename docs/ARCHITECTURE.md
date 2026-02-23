# Arquitectura del Sistema e Información

## 1. Visión General del Sistema
Tlacuilo es una aplicación web local orquestada mediante Docker, diseñada para gestionar el ciclo de vida de la documentación del portafolio "Altepetl Digital". Actúa como intermediario entre el sistema de archivos local (donde vive la verdad) y los modelos de IA (donde vive la asistencia).

### Diagrama de Alto Nivel
```mermaid
graph TD
    User[Usuario (Humano)] --> Frontend[Frontend (Vue 3)]
    Frontend --> API[Backend API (FastAPI)]
    
    subgraph Localhost Infrastructure
        API --> FS[Sistema de Archivos Externo (Portafolio)]
        API --> Data[Memoria Interna (./data en Root)]
        API --> Prompts[Prompts as Code (./prompts en Root)]
        API --> Comfy[ComfyUI (Imágenes)]
        API --> GEM[Ollama/Gemini (Texto)]
    end
    
    note right of Prompts
      Montado en Docker:
      Host: ./prompts -> Container: /app/prompts
      Host: ./docs/definitions -> Container: /app/definitions
    end
```

## 2. Arquitectura de Información
El sistema organiza la información en tres niveles jerárquicos:

### Nivel 1: Colecciones (Tipos de Proyecto)
Carpetas raíz dentro del portafolio.
-   `atoms/`: Proyectos de Hardware/Físicos.
-   `bits/`: Proyectos de Software/Digitales.
-   `mind/`: Ensayos y Filosofía.

### Nivel 2: Proyectos (Entidades)
Cada carpeta dentro de una colección es un proyecto.
-   Identificador: `slug` (nombre de la carpeta).
-   **Estatus del Proyecto** (`status`): Define la madurez técnica (`idea`, `poc`, `wip`, `done`). (Ver `docs/definitions/MATURITY_LEVELS.md`).
-   **Estatus de Documentación** (`doc_status`): Define la etapa en el flujo de Tlacuilo (`borrador`, `revisión`, `promovido`, `traducción`, `publicado`). 
    -   *Almacenamiento*: Se guarda **exclusivamente** en la Memoria Local (`projects/{slug}/doc_state.json`). **NUNCA** en el Frontmatter del archivo final.
-   **Visibilidad** (`draft`): Booleano en el Frontmatter que indica si el archivo está listo para el mundo o es privado.
-   **Evidencias** (`shots/`): Subcarpeta para la gestión de activos visuales mediante Tlacuilo Ixtli.
    -   *Estructura*: `projects/{collection}/{slug}/shots/{shot_id}/`.
    -   *Contenido*: Metadatos del shot, historial de chat específico y variantes generadas.

> [!NOTE]
> Para detalles sobre cómo se manejan las discrepancias entre el Portafolio y la Memoria Local (ej. archivos faltantes), consultar [SYNCHRONIZATION.md](SYNCHRONIZATION.md).

### Nivel 3: Documentación (El Ciclo)
Dentro de cada proyecto existe el archivo principal `.md` cuyo nombre es igual al slug (ej. `mi-proyecto.md`).
-   Estado del Documento: Gestionado por Tlacuilo fuera del archivo (Local Memory).
-   Historial de Chat: Contexto persistente de la conversación con el GEM.

## 3. Servicios API Requeridos (Backend)

### A. Servicio de Proyectos (`/projects`)
Gestiona la lectura y escritura en el sistema de archivos (Portafolio y Local).
-   `GET /api/projects`: **Listar Proyectos (Discovery Cycle)**
    -   **Responsabilidad**: Escanear el Portafolio y la Memoria Local para identificar proyectos y sincronizar estados iniciales.
    -   **Input**: N/A.
    -   **Validation**: Verifica la legibilidad de `PORTAFOLIO_PATH` y la carpeta `projects/` local.
    -   **Internal Process (Discovery Cycle)**:
        1.  Lista directorios en `{PORTAFOLIO}/{coleccion}/es/`.
        2.  Lista directorios en `projects/{coleccion}/`.
        3.  Cruza ambas listas. Si un proyecto está en Portafolio pero no en Local, dispara la **Hidratación** (Crea memoria local mínima).
    -   **Response Contract (200)**:
        ```json
        {
          "atoms": [
            {
              "id": "slug-identificador",
              "name": "Título del Proyecto",
              "description": "Breve resumen del frontmatter",
              "doc_status": "revisión",
              "published": false,
              "type": "atoms",
              "missing_files": false
            }
          ],
          "bits": [],
          "mind": []
        }
        ```
-   `POST /projects`: Crea un nuevo proyecto.
    -   **Payload**: `{ "name": "Título", "collection": "atoms|bits|mind", "slug": "opcional-slug" }`.
    -   **Reglas de Validación (MANDATORIAS)**:
        1. El `slug` se genera desde el `name` si no se provee. Kebab-case.
        2. **Unicidad Externa**: No debe existir la carpeta en el Portafolio `{PORTAFOLIO}/{coleccion}/es/`.
        3. **Unicidad Interna**: No debe existir la carpeta en `projects/{collection}/` local.
-   `POST /api/{collection}/{slug}/forget`: **Forget Action (Borrado de Memoria)**
    -   **Responsabilidad**: Eliminar permanentemente la carpeta de memoria local del proyecto. **NO toca el Portafolio**.
    -   **Input**: `{}`.
    -   **Validation**: El proyecto debe existir en la memoria local (`projects/`).
    -   **Internal Process**: Borrado recursivo de `projects/{collection}/{slug}/`.
    -   **Response Contract (200)**: Cuerpo vacío.

-   `POST /api/{collection}/{slug}/resurrect`: **Resurrect Action (Rescate de Archivo)**
    -   **Responsabilidad**: Restaurar el archivo principal `{slug}.md` desde la memoria local hacia el Portafolio  si este desapareció.
    -   **Input**: `{}`.
    -   **Validation**: 
        1. Debe existir el archivo `{slug}.md` en la memoria local.
        2. NO debe existir el archivo en el Portafolio (para evitar sobreescritura accidental).
    -   **Internal Process**: Copia el archivo MD de la carpeta local a la ruta correspondiente `{PORTAFOLIO}/{coleccion}/es/` en el Portafolio.
    -   **Response Contract (200)**: Cuerpo vacío.

### B. Servicio de Tlacuilo Digital (Contenido y Chat)
Orquesta el **Ciclo de Entrevista** y la gestión de la **Working Copy** (Copia de Trabajo).

#### 1. Reglas de Precedencia (Lógica de Selección de Contenido)
Tlacuilo decide qué versión del archivo `{slug}.md` mostrar basándose en el estado `is_working_copy_active` definido en `doc_state.json`:

1.  **Sesión Activa (`is_working_copy_active: true`)**: El usuario está en medio de un proceso creativo (chat iniciado, edición manual o borrador propuesto). **Prioridad: Local**. Se ignora el Portafolio para proteger la mesa de trabajo.
2.  **Sincronización Pasiva (`is_working_copy_active: false`)**: No hay sesión abierta. **Prioridad: Portafolio**. Si el archivo oficial existe, se toma como Fuente de Verdad y actualiza el local.
3.  **Hidratación (Semilla)**: Portafolio existe, Local no. Se copia el archivo oficial al local para iniciar la Copia de Trabajo.
4.  **Resurrección (Huerfana)**: Local existe, Portafolio no. **Prioridad: Local**. El sistema permite restaurar el archivo oficial desde la memoria local.
5.  **Proyecto Nuevo**: No existe en ningún lado. **Prioridad: Plantilla**. Se carga el template correspondiente (`atoms|bits|mind`).

#### 2. Acciones del Usuario y Endpoints
Todas las rutas operan bajo el prefijo `/api`.

**A. Sincronización de Contexto**
El frontend debe llamar a estos dos endpoints en paralelo al cargar un proyecto. NUNCA tienen efectos secundarios (no reparan, no escriben, no crean).

-   `GET /api/{collection}/{slug}/content`: **Obtener Contenido del Documento**
    -   **Responsabilidad**: Devolver el contenido del archivo `.md` y su estado de sincronización actual.
    -   **Lógica de Selección (El Validador)**:
        1.  **Vacío (Proyecto Nuevo)**: Si no existe en Portafolio ni en Local -> Retorna Plantilla Base de la colección.
        2.  **Semilla (Hidratación)**: Si Portafolio existe pero Local no -> Copia automáticamente el archivo del Portafolio a la Memoria Local e inicializa `doc_state.json`.
        3.  **Sesión Activa (`is_working_copy_active: true`)**: Si hay un proceso de edición o chat en curso -> Devuelve exclusivamente la copia local. **Ignora cambios externos en el Portafolio** para evitar colisiones durante la entrevista.
        4.  **Sincronización Pasiva (`is_working_copy_active: false`)**: Si no hay sesión activa -> Sincroniza Local desde Portafolio (si este es más reciente) y devuelve contenido.
    -   **Input**: N/A.
    -   **Validation**: El proyecto debe estar registrado en el sistema. Si no existe en ningún lado, retorna 404.
    -   **Response Contract (200)**:
        ```json
        {
          "content": "# Título..."
        }
        ```

-   `GET /api/{collection}/{slug}/chat/history`: **Obtener Historial de Chat**
    -   **Responsabilidad**: Recuperar la bitácora de mensajes de la memoria local, filtrando información puramente técnica.
    -   **Input**: N/A.
    -   **Validation**: Busca `chat_history.json` en la ruta correspondiente. Si el archivo no existe, asume historial vacío.
    -   **Internal Process**: Filtra todos los objetos donde `system_only: true`. Asegura que el array esté ordenado cronológicamente por `timestamp`.
    -   **Response Contract (200)**:
        ```json
        {
          "messages": [
            { "role": "user", "content": "...", "timestamp": "..." },
            { "role": "assistant", "content": "...", "timestamp": "..." }
          ]
        }
        ```
    -   **Failure (500)**: Si el JSON está corrupto, lo renombra a `.corrupt` y notifica al usuario.

-   `POST /api/{collection}/{slug}/revert`: **Abortar Cambios y Restaurar Original**
    -   **Responsabilidad**: Descartar la Copia de Trabajo actual y volver a la versión oficial del Portafolio.
    -   **Efecto**:
        1.  Sobreescribe el `{slug}.md` local con el contenido actual del Portafolio.
        2.  Apaga forzosamente `is_working_copy_active` a `false`.
        3.  Mantiene el historial de chat (para no perder el contexto de por qué se descartó el cambio).
        4.  Actualiza `doc_status` a `revisión`.
    -   **Input**: `{}`.
    -   **Validation**: Debe existir el archivo oficial en el Portafolio. Si no hay original al cual volver, la operación falla (400).
    -   **Response Contract (200)**: Cuerpo vacío.

**B. Ciclo de Entrevista**
-   `POST /api/{collection}/{slug}/init`: **Arranque de Sesión (Trigger)**.
    -   **Responsabilidad**: Evaluar estado y, si es necesario, construir el **Contexto Cero** (System Prompt) para delegar la ejecución al endpoint `/message`.
    -   **Base de Conocimiento**:
        -   System Prompt: `prompts/system/tlacuilo_digital.md`
    -   **Escenarios de Negocio**:
        1.  **Lienzo en Blanco (Nuevo)**: Historial vacío -> Construye Payload con System Prompt y el Strategy Prompt correspondiente a la colección y md del proyecto para generar el contexto inicial -> Llama internamente a `/message` (Trigger oculto).
        2.  **Deuda Técnica (Interrumpido)**: Último msg User -> Llama internamente a `/message` (sin input nuevo) para procesar pendiente.
        3.  **Esperando al Humano**: Último msg Asistente -> Retorno temprano (No llama a message).
    -   **Contrato de Respuesta**:
        -   **Si se genera un Mensaje** (Lienzo/Deuda): Se envía dicho **Mensaje** jutno con la bandera `system_only: true` como input al endpoint `/message` y se retorna su respuesta.
        -   **Si NO se genera Mensaje**: Retorna HTTP 204 No Content.
-   `POST /api/{collection}/{slug}/message`: **Mensajería Transaccional (Context-Aware)**.
    -   **Responsabilidad**: Recibir un mensaje, persistirlo, obtener respuesta de la IA (Llama/Mistral) y persistir respuesta.
    -   **Base de Conocimiento**:
        -   System Prompt: `prompts/system/tlacuilo_digital.md`
        -   Strategy (Atoms/Bits): `prompts/strategies/atoms_bits_strategy.md`
        -   Strategy (Mind): `prompts/strategies/mind_strategy.md`
    -   **Input**: `{ "content": "Texto...", "system_only": true|false (opcional), "response_system_only": true|false (opcional) }`.
    -   **Validación**:
        1.  **Existencia**: El objeto no puede ser nulo.
        2.  **`content`**: String NO vacío. No admite espacios en blanco (" ").
        3.  **`system_only`**: Booleano opcional. Marca el mensaje de entrada como oculto.
        4.  **`response_system_only`**: Booleano opcional. Indica si la respuesta de la IA debe guardarse también como oculta.
    -   **Proceso Interno (Sanitización)**: Antes de enviar a Ollama, el servicio limpia el historial y construye una lista que contiene ÚNICAMENTE `role` y `content`, eliminando cualquier metadato interno (`timestamp`, `system_only`, etc.).
    -   **Output (Respuesta Exitosa)**: Objeto JSON estándar: `{ "role": "assistant", "content": "Respuesta IA...", "timestamp": "ISO-8601" }`.
    -   **Output (Respuesta Fallida - Error General)**:
        -   **Http Code**: 500/503.
        -   **Efecto**: Si falla CUALQUIER paso tras guardar el mensaje del usuario (IA, IO, Formato), se aborta. El mensaje del usuario persiste, pero el del asistente **NO** se genera. NUNCA se guarda basura.


-   `POST /api/{collection}/{slug}/draft`: **Generación de Borrador (Propuesta)**.
    -   **Responsabilidad**: Analizar la conversación reciente y generar un documento Markdown completo y consolidado. **NO guarda en disco local todavía**. Devuelve el contenido para revisión visual (Diff).
    -   **Input**: `{}` (Vacío). Usa el estado del servidor.
    -   **Validación**: Nula.
    -   **Proceso Interno**:
        1.  **Recuperación de Contexto**:
            -   Obtiene el MD actual siguiendo las mismas reglas de precedencia que `GET /api/{collection}/{slug}/content`.
            -   Carga el **Template** estructural del documento desde el portafolio no el local.
            -   Carga el **Template** de recursos del documento desde el portafolio no el local.
            -   Carga el **System Prompt Template** específico para generación de borrador (instrucciones de forzado de formato MD): `prompts/strategies/draft_generation.md`.
        2.  **Construcción de Prompt**: Crea un mensaje de sistema instruyendo "Genera solo MD final...".
        3.  **Delegación a `/message`**: Llama internamente a `/message` con:
            -   `content`: El prompt construido.
            -   `system_only`: true (Prompt oculto).
            -   `response_system_only`: true (Respuesta MD oculta en chat history).
        4.  **Sanitización**: Limpia bloques de código (```markdown) de la respuesta obtenida.
    -   **Contrato de Respuesta (Output)**:
        -   **Exitosa (200)**: `{ "content": "# Nuevo MD...", "status": "draft" }`. (Formato compatible con `GET /content`).
        -   **Fallida (500/503)**: Error en generación.

**C. Validación, Persistencia y Promoción**

-   `POST /api/{collection}/{slug}/persist`: **Autorización de Cambios (Persistencia)**.
    -   **Responsabilidad**: Validar el contenido (contra plantilla) y SOBREESCRIBIR el archivo `{slug}.md` físico (Copia de Trabajo), activando obligatoriamente el estado de sesión.
    -   **Input**: `{ "content": "# Markdown Nuevo..." }`.
    -   **Validación**:
        1.  **Integridad Estructural**: El contenido DEBE cumplir con la estructura/plantilla definida para la colección (Headers, Frontmatter, Secciones obligatorias). Si falla, rechaza.
        2.  **Contenido**: No vacío.
    -   **Proceso Interno**:
        1.  Identificar la ruta física del archivo `{slug}.md` en la carpeta de trabajo.
        2.  Escribir el contenido (Sobreescritura total).
        3.  **Estado**: Actualizar `doc_state.json` -> `doc_status: borrador`.
        4.  Establecer la bandera `is_working_copy_active = true`.
    -   **Contrato de Respuesta (Output)**:
        -   **Exitosa (200)**: Cuerpo vacío.
        -   **Fallida (400)**: Error de validación estructural.
        -   **Fallida (500)**: Error de escritura en disco. 


-   `POST /api/{collection}/{slug}/promote`: **Promoción al Portafolio (Finalización)**.
    -   **Responsabilidad**: Validar estrictamente la Copia de Trabajo, marcarla como `promovido`, MOVERLA al Portafolio. **La orquestación de la Traducción es responsabilidad del Cliente (Frontend) tras recibir el 200 OK**.
    -   **Input**: `{}`.
    -   **Validación**:
        1.  **Schema Check Estricto**: Debe tener Frontmatter completo. Si falta algo, rechaza (400).
        2.  **Existencia**: Debe haber una Copia de Trabajo activa.
    -   **Proceso Interno**:
        1.  Leer `working_copy/{slug}.md`.
        2.  **Estado**: Actualizar `projects/{collection}/{slug}/doc_state.json` -> `doc_status: promovido`.
        3.  **IO**: Mover/Copiar a `PORTFOLIO_PATH/{collection}/es/{slug}.md`.
        4.  Apagar flag `is_working_copy_active`.
    -   **Contrato de Respuesta (Output)**:
        -   **Exitosa (200)**: Cuerpo vacío.
        -   **Fallida (400)**: Error de validación estructural.
        -   **Fallida (500)**: Error de escritura o movimiento de archivo. 

**D. Localización (English Flow)**
-   `GET /api/{collection}/{slug}/translate`: **Lectura Traducción (Inglés)**.
    -   **Responsabilidad**: Obtener el contenido del documento en Inglés aplicando Reglas de Negocio (Espejo de `/content`).
    -   **Paths**:
        -   Local: `working_copy/{slug}.en.md`.
        -   Portafolio: `PORTFOLIO_PATH/{collection}/en/{slug}.md`.
    -   **Lógica de Selección**:
        1.  **Vacío (Nuevo)**: Si no existe en ningún lado -> Devuelve Vacío o Plantilla EN.
        2.  **Semilla (Hidratación)**: Si Portafolio existe (`en/{slug}.md`) pero Local no -> Copia Portafolio a Local (`{slug}.en.md`) y devuelve contenido.
        3.  **Sesión Activa**: Si hay trabajo en curso -> Devuelve Local (Ignora Portafolio).
        4.  **Sincronización Pasiva**: Si existe en ambos y el status de la documentacion no es `promovido` -> Actualiza Local desde Portafolio.
    -   **Respuesta**: `{ "content": "..." }`. 

-   `POST /api/{collection}/{slug}/translate/draft`: **Generación/Refinamiento (Inglés)**.
    -   **Responsabilidad**: Generar la primera versión en Inglés O refinar un borrador existente usando el **The Bilingual Scribe**.
    -   **Ciclo de Revisión y Generación (Reintento y Descarte)**:
        1.  **Recuperación**: Obtiene el `source_content` (Español).
        2.  **Construcción**: Ensambla el payload con `tlacuilo_global.md` + `english_translation.md`.
        3.  **Generación**: Envía a la IA.
        4.  **Validación y Corrección**:
            -   Si el MD generado falla la validación estructural:
                -   Se registra el fallo en la conversación temporal (con timestamp).
                -   Se envía un nuevo prompt a la IA usando `prompts/strategies/english_correction.md` inyectando el bloque `## VALIDATION ERROR:` con el detalle de la falla.
                -   Se repite hasta un máximo de N intentos.
        5.  **Finalización**: Si pasa la validación, se responde al servicio con el contenido limpio.
    -   **Uso de Prompts (Orquestación)**:
        1.  **System Prompt**: `prompts/system/tlacuilo_global.md` (Define identidad).
        2.  **Strategy Prompt**: `prompts/strategies/english_translation.md` (Reglas de salida y formato).
        3.  **Correction Prompt**: `prompts/strategies/english_correction.md` (Instrucciones específicas de reparación).
    -   **Lógica de Negocio**:
        1.  **Traducción Directa (`from_scratch: true`)**:
            -   **Prompt de Usuario**: Instruye traducir el `source_content` (Español) íntegro.
            -   **Comportamiento**: Ignora draft previo y se enfoca en la fidelidad al original.
        2.  **Refinamiento (`from_scratch: false`)**:
            -   **Prompt de Usuario**: Combina el `source_content`, el `current_draft` y la `instruction` del usuario.
            -   **Comportamiento**: Prioriza la instrucción específica manteniendo coherencia con la fuente.
    -   **Construcción del Payload (Prompting)**:
        1.  **System Message**: Fusión de `tlacuilo_global.md` (Identidad) + `english_translation.md` (Estrategia).
        2.  **User Message (from_scratch: true)**:
            ```text
            Translate the FOLLOWING source content to English:
            ---
            {source_content}
            ---
            ```
        3.  **User Message (from_scratch: false)**:
            ```text
            SOURCE CONTENT (Spanish):
            ---
            {source_content}
            ---
            CURRENT DRAFT (English):
            ---
            {current_draft}
            ---
            USER INSTRUCTION: {instruction}
            
            Please REFINE the English draft according to the instruction, ensuring alignment with the source content.
            ```
    -   **Output**: `{ "content": "..." }`. NO guarda en disco. La respuesta de la IA debe empezar directamente con el Frontmatter (`---`).

-   `POST /api/{collection}/{slug}/translate/persist`: **Autorización de Cambios (Persistencia Inglés)**.
    -   **Responsabilidad**: Validar el contenido (contra plantilla) y SOBREESCRIBIR el archivo `{slug}.en.md` físico (Copia de Trabajo), activando obligatoriamente el estado de sesión.
    -   **Input**: `{ "content": "# Markdown Nuevo..." }`.
    -   **Validación**:
        1.  **Integridad Estructural**: El contenido DEBE cumplir con la estructura/plantilla definida para la colección (Headers, Frontmatter, Secciones obligatorias). Si falla, rechaza.
        2.  **Contenido**: No vacío.
    -   **Proceso Interno**:
        1.  Identificar la ruta física del archivo `{slug}.en.md` en la carpeta de trabajo.
        2.  Escribir el contenido (Sobreescritura total).
        3.  **Estado**: Actualizar `doc_state.json` -> `doc_status: traducción`.
    -   **Contrato de Respuesta (Output)**:
        -   **Exitosa (200)**: Cuerpo vacío.
        -   **Fallida (400)**: Error de validación estructural.
        -   **Fallida (500)**: Error de escritura en disco.

**E. Servicio de Tlacuilo Ixtli (`/studio`)**
Gestión de activos visuales mediante un flujo de **Borrador y Corrección** (sin chat persistente) y puente con ComfyUI.

#### 1. Gestión de Evidencias (CRUD de Shots)
Este servicio permite gestionar la "Lista de Tiro" (Shot List) del proyecto. Los metadatos de cada toma se guardan en `projects/{collection}/{slug}/shots/{shot_id}/metadata.json`.

- `POST /api/{collection}/{slug}/studio/suggest`: **Sugerir y Persistir Tomas**
    - **Responsabilidad**: Analizar el archivo `{slug}.md` y crear físicamente las sugerencias de tomas en el sistema de archivos.
    - **Input**: N/A.
    - **Validation**: El proyecto debe existir y tener contenido Markdown legible.
    - **Proceso Interno**: Ejecuta `prompts/strategies/shot_suggestion.md` con el contenido del MD. Por cada sugerencia retornada, invoca la lógica de creación de slot. El prompt de sugerencia **debe incluir** los campos de contexto Ixtli (`focus`, `atmosphere`) para evitar ciclos de corrección.
    - **Contrato de Respuesta (Output)**:
        - **Éxito (200)**: `[{"shot_id": "...", "title": "...", "description": "...", "type": "...", "focus": "¿Qué componente es el protagonista?", "atmosphere": "rojo|turquesa|ambar"}]`.
        - **Falla (404)**: Proyecto no encontrado.

- `GET /api/{collection}/{slug}/studio/shots`: **Listar Tomas**
    - **Responsabilidad**: Retornar la Shot List completa del proyecto con el estado actual de cada toma.
    - **Input**: N/A.
    - **Proceso Interno**: Escanea el directorio `shots/` y agrega los `metadata.json` existentes.
    - **Contrato de Respuesta (Output)**:
        - **Éxito (200)**: `[{"shot_id": "...", "title": "...", "type": "...", "status": "pending_upload|queued|generated|approved", "has_original": boolean, "visual_prompt": "...|null"}]`.
    - **Escenarios de Negocio (Ciclo de vida del `status`)**: `pending_upload` (slot creado) → `queued` (enviado a ComfyUI) → `generated` (imagen disponible) → `approved` (imagen aceptada como válida).

- `POST /api/{collection}/{slug}/studio/shots`: **Crear Toma Manual**
    - **Responsabilidad**: Crear manualmente un slot de toma sin pasar por la IA.
    - **Input**:
        ```json
        {
          "title": "...",
          "description": "Descripción técnica del encuadre",
          "type": "macro|context|conceptual",
          "focus": "Componente protagonista (ej: press-fit entre pieza A y B)",
          "atmosphere": "rojo|turquesa"
        }
        ```
    - **Validation**: `title` y `atmosphere` obligatorios.
    - **Proceso Interno**:
        1. Genera `shot_id` (slug del título).
        2. Crea carpeta `projects/{collection}/{slug}/shots/{shot_id}/`.
        3. Inicializa `metadata.json` con `status: "pending_upload"` y todos los campos de contexto.
    - **Contrato de Respuesta (Output)**:
        - **Éxito (201)**: `{ "shot_id": "...", "status": "created" }`.
        - **Falla (400)**: Título faltante, atmósfera inválida, o `shot_id` duplicado.

- `GET /api/{collection}/{slug}/studio/shots/{shot_id}`: **Obtener Detalle de Toma**
    - **Responsabilidad**: Recuperar metadatos completos de una toma específica.
    - **Input**: N/A (ID en la URL).
    - **Contrato de Respuesta (Output)**:
        - **Éxito (200)**: Objeto completo de `metadata.json`.
        - **Falla (404)**: Shot no encontrado.

- `PATCH /api/{collection}/{slug}/studio/shots/{shot_id}`: **Actualizar Toma**
    - **Responsabilidad**: Editar los metadatos de contexto de una toma ya creada (incluyendo `focus` y `atmosphere`).
    - **Input**: `{ "title": "...", "description": "...", "focus": "...", "atmosphere": "rojo|turquesa" }` (todos opcionales).
    - **Contrato de Respuesta (Output)**:
        - **Éxito (200)**: `{ "shot_id": "...", "status": "updated" }`.
        - **Falla (404)**: Shot no encontrado.

- `DELETE /api/{collection}/{slug}/studio/shots/{shot_id}`: **Borrar Toma**
    - **Responsabilidad**: Eliminación física (recursiva) de la carpeta `shots/{shot_id}/`.
    - **Input**: N/A (ID en la URL).
    - **Contrato de Respuesta (Output)**:
        - **Éxito (204)**: Cuerpo vacío.
        - **Falla (404)**: Shot no encontrado.

#### 2. Flujo de Generación (Upload & Correct Loop)

El flujo comprende **dos acciones**. Upload dispara todo el ciclo; Correct itera sobre el resultado anterior.

**Estado del `metadata.json` a lo largo del ciclo:**
`pending_upload` → `queued` → `generated` → (ciclos de corrección) → `generated`

- `POST /api/{collection}/{slug}/studio/shots/{shot_id}/upload`: **Subir y Disparar Generación**
    - **Responsabilidad**: Recibir la imagen de referencia y lanzar automáticamente el ciclo completo (Vision LLM → prompt → ComfyUI) sin intervención manual adicional.
    - **Input**: `multipart/form-data` con campo `file` (PNG/JPG, máx. 10MB).
    - **Validation**: Tipo de archivo imagen. El shot debe existir con `focus` y `atmosphere` definidos.
    - **Proceso Interno (Pipeline automático)**:
        1. Guarda la imagen como `shots/{shot_id}/original.png`.
        2. Llama al Agente Ixtli (Vision LLM) pasando: `original.png` + `description` + **`focus`** + **`atmosphere`** del `metadata.json` para generar el `visual_prompt` sin ambigüedad.
        3. Inyecta `visual_prompt` y `original.png` en el workflow `ixtli_generate.json` y encola la tarea.
        4. Actualiza `metadata.json` → `status: "queued"`, guarda el `visual_prompt` generado y el `prompt_id` de ComfyUI.
    - **Contrato de Respuesta (Output)**:
        - **Éxito (202)**: `{ "prompt_id": "uuid-comfy", "status": "queued", "visual_prompt": "..." }`.
        - **Falla (400)**: Archivo inválido o shot sin `focus`/`atmosphere` definidos.
        - **Falla (404)**: Shot no encontrado.
    - **Nota**: Re-subir una imagen reinicia el ciclo desde cero (nueva `original.png`, nuevo prompt, nueva generación).

- `POST /api/{collection}/{slug}/studio/shots/{shot_id}/correct`: **Ciclo de Corrección**
    - **Responsabilidad**: Aplicar una instrucción de corrección sobre la última imagen generada y enviar a ComfyUI de nuevo.
    - **Input**: `{ "instruction": "El fondo más oscuro, menos blur en el objeto" }`.
    - **Validation**: Debe existir una generación previa (`status: "generated"`). `instruction` es obligatorio.
    - **Proceso Interno**:
        1. Recupera el `visual_prompt` actual del `metadata.json`.
        2. Llama al Agente Ixtli con el `visual_prompt` anterior + `instruction` para generar un `visual_prompt` refinado.
        3. Encola en ComfyUI usando la última imagen generada como base (`img2img`).
        4. Actualiza `metadata.json` → `status: "queued"`, sobreescribe el `visual_prompt`.
    - **Contrato de Respuesta (Output)**:
        - **Éxito (202)**: `{ "prompt_id": "uuid-comfy", "status": "queued", "visual_prompt": "..." }`.
        - **Falla (400)**: No hay generación previa sobre la cual corregir.

- `POST /api/{collection}/{slug}/studio/shots/{shot_id}/approve`: **Aprobar Imagen**
    - **Responsabilidad**: Marcar una imagen generada como válida y definitiva para el shot. No mueve ni copia archivos.
    - **Input**: `{ "filename": "nombre_del_archivo_generado.png" }` (nombre del archivo dentro de `shots/{shot_id}/`).
    - **Validation**: El shot debe estar en `status: "generated"`.
    - **Proceso Interno**: Actualiza `metadata.json` → `status: "approved"`, registra el `approved_filename`.
    - **Contrato de Respuesta (Output)**:
        - **Éxito (200)**: `{ "status": "approved", "approved_file": "..." }`.
        - **Falla (400)**: Shot no tiene imagen generada aún.
        - **Falla (404)**: Shot no encontrado.

#### 3. Especificaciones para el Experto en ComfyUI (Ixtli)

El Experto en ComfyUI es responsable de diseñar los workflows JSON que el Backend inyectará y ejecutará. Su entrega es un archivo JSON compatible con la API de ComfyUI.

**Principio Central**: El usuario **nunca** debe dar instrucciones estéticas manuales ("quita el fondo", "cambia el color"). Toda decisión visual de tratamiento está **pre-codificada** en el diseño del workflow, basada en el **Códice de Imagen "Obsidiana Telemetría"**.

---

##### 3.1 Estética Obligatoria ("Obsidiana Telemetría")
El workflow debe aplicar automáticamente estos parámetros sin excepción:

| Parámetro | Valor |
|---|---|
| **Fondo** | Negro `#050505` — obligatorio, sin variación |
| **Aspecto** | 1:1 cuadrado — obligatorio |
| **Composición** | Sujeto centrado en franja horizontal 3:2; espacio negro en top/bottom |
| **Iluminación** | Chiaroscuro dramático + rim lighting en `#D4442F` (Rojo) o `#00A6B6` (Turquesa) |
| **Resolución** | 8k upscale final |
| **Prohibido** | Fondos claros, alteración de geometría del hardware, distorsión de componentes |

El **Agente Ixtli (Vision LLM)** alimenta el flujo. Su output es un `visual_prompt` describiendo el **objeto y la técnica** (no la estética — la estética ya está en el workflow).

---

##### 3.2 Mapa de Nodos (Interface Contract con el Backend)
El Backend inyecta los valores dinámicos en los siguientes nodos. **Sus IDs son fijos e inamovibles**:

| Node ID | Tipo | Valor Inyectado |
|---|---|---|
| `Node 3` | KSampler | Seed aleatoria, Steps: 30, CFG: 7 |
| `Node 6` | CLIPTextEncode (+) | `visual_prompt` del `metadata.json` |
| `Node 7` | CLIPTextEncode (−) | Prompt negativo estándar (`blurry, low quality, bright background, distorted`) |
| `Node 10` | LoadImage | Ruta a `shots/{shot_id}/original.png` |
| `Node 11` | JoyCaption / VLM | Análisis automático de la imagen (contexto del objeto) |

**Regla**: El Experto **no puede** cambiar los IDs de estos nodos. Puede añadir nodos auxiliares con IDs adicionales.

---

##### 3.3 Flujos Requeridos
El Experto debe entregar **dos workflows JSON**:

1. **`ixtli_generate.json`** (`txt2img` + `img2img` con ControlNet): Flujo primario. Toma `original.png` como referencia (ControlNet Depth/Canny), aplica el `visual_prompt`, y genera 4 variantes.
2. **`ixtli_correct.json`** (`img2img`): Flujo de corrección. Toma la última imagen generada como base, aplica el `visual_prompt` refinado. Preserve la geometría del sujeto.

---

##### 3.4 Reglas de Integridad de Hardware
- **Nunca** generar un componente diferente al de la foto original.
- **Nunca** modificar la topología de circuitos, posición de piezas ni cableado.
- Si el modelo altera la geometría del hardware, el workflow debe incluir un nodo de control que lo detecte (p. ej., ControlNet Canny alto-peso).
- **Salida**: 4 variantes en batch. El Backend las recupera y las guarda en `shots/{shot_id}/`. El usuario elige una con `/approve`.


**F. Servicio de Publicación (`/publish`)**
Operación de sistema que cierra el ciclo completo de documentación y sincroniza el portafolio con el repositorio remoto. Es una acción global del proyecto, independiente de cualquier flujo de contenido o imagen.

- `POST /api/{collection}/{slug}/publish`: **Publicación al Portafolio**
    - **Responsabilidad**: Marcar el proyecto como COMPLETADO y sincronizar la Verdad Técnica con el repositorio remoto.
    - **Input**: `{}`.
    - **Validation**:
        1. Debe existir versión en Inglés (`en/{slug}.md`).
        2. El `doc_status` debe ser distinto de `publicado` (evitar re-publicaciones innecesarias).
    - **Proceso Interno**:
        1. Actualiza `doc_state.json` → `doc_status: publicado`.
        2. El Sistema (no agentes) ejecuta `git add`, `git commit`, `git push` sobre el portafolio de forma automatizada. **NUNCA** delegar comandos git a los agentes.
    - **Contrato de Respuesta (Output)**:
        - **Éxito (200)**: `{ "status": "publicado" }`.
        - **Falla (400)**: Falta versión en Inglés.

## 4. Protocolos de Sincronización y Alineación

Tlacuilo gestiona las discrepancias entre la **Verdad Externa** (Portafolio) y la **Memoria Interna** (`projects/`) mediante protocolos estandarizados.

### Escenario A: Proyecto Existente, Tlacuilo Nuevo (Hidratación)
- **Caso**: Existe el archivo `.md` en el portafolio, pero no hay carpeta en `projects/`.
- **Acción**: Tlacuilo crea la carpeta necesaria e inicializa un historial de chat vacío con un mensaje de sistema que carga el contexto inicial del archivo.

### Escenario B: Memoria Huérfana (Diagnóstico y Rescate)
- **Caso**: Existe historial en `projects/`, pero el archivo `.md` ha desaparecido del portafolio.
- **Acción (UI)**: El frontend marca el proyecto como **"MEMORIA HUÉRFANA"** en el Centro de Mando.
- **Protocolo**: El usuario puede elegir **DESCARTAR MEMORIA** (endpoint `forget`) o **RESTAURAR PROYECTO** (endpoint `resurrect`).

### Escenario C: Sincronización Normal (Operación Diaria)
- **Caso**: Ambos existen.
- **Acción**: Tlacuilo confía en el `.md` para el contenido y en `projects/` para el contexto conversacional y el estado del flujo (`doc_status`).

> [!IMPORTANT]
> **Regla de Oro**: El Portafolio manda. Tlacuilo nunca sobreescribe el Portafolio automáticamente al arrancar. Solo escribe cuando el usuario ejecuta explícitamente una acción de "Guardar", "Generar" o "Restaurar".

---
## 5. Arquitectura de Prompts (Prompts as Code)

Tlacuilo utiliza un sistema de **Prompts Composicionales**, donde la instrucción final enviada al LLM se construye dinámicamente combinando un Role (Persona) y una Strategy (Contextual).

### A. Catálogo de Prompts
| Tipo | Archivo | Funcionalidad |
| :--- | :--- | :--- |
| **System** | `prompts/system/tlacuilo_digital.md` | Persona "El Escriba Fiel" (Español). Tono de taller y mentor. |
| **System** | `prompts/system/tlacuilo_global.md` | Persona "The Bilingual Scribe" (Inglés). Traductor técnico. |
| **Strategy** | `prompts/strategies/atoms_bits_strategy.md` | Lógica de entrevista/extracción para proyectos técnicos. |
| **Strategy** | `prompts/strategies/mind_strategy.md` | Lógica de extracción para ensayos y reflexiones. |
| **Strategy** | `prompts/strategies/draft_generation.md` | Instrucciones de ensamblaje final y blindaje de Frontmatter. |
| **Strategy** | `prompts/strategies/english_translation.md` | Reglas de translocalización técnica y preservación de términos. |
| **System** | `prompts/system/tlacuilo_ixtli.md` | Persona "Tlacuilo Ixtli" (Director Visual). Experto en fotografía técnica. |

### B. Mapeo de Servicios vs Prompts
El Backend orquesta la inyección según el endpoint:

| Endpoint | System Prompt (Role) | Strategy Prompt (Context) |
| :--- | :--- | :--- |
| `/init` | `tlacuilo_digital.md` | `atoms_bits_strategy.md` o `mind_strategy.md` |
| `/message` | `tlacuilo_digital.md` | Seguimiento de la estrategia cargada en sesión. |
| `/draft` | `tlacuilo_digital.md` | `draft_generation.md` + Strategy de Colección. |
| `/translate/draft` | `tlacuilo_global.md` | `english_translation.md`. |
| `/studio/*` | `tlacuilo_ixtli.md` | Ciclo de sugerencia y refinamiento visual. |

### C. Reglas de Construcción de Prompts
Para mantener la calidad de la asistencia, todo prompt en Tlacuilo debe seguir estos axiomas:

1.  **Zero Tolerancia a la Invención**: Se prohíbe explícitamente al asistente inventar componentes, pasos o resultados. "Prefiere preguntar que alucinar".
2.  **Tono de Ingeniería Forense**: El lenguaje debe ser técnico, seco y orientado a la evidencia (evitar el "misticismo" o "poesía" excesiva).
3.  **Blindaje de Estructura**: Las instrucciones deben forzar la salida en bloques de código limpios, prohibiendo el uso de iconos en llaves de Frontmatter o estructuras de datos.
4.  **Prioridad de la Verdad Loca**: El contenido del archivo `.md` actual siempre tiene jerarquía sobre lo que el LLM crea que es "lo normal" para un sensor o código.

---
## 6. Roles de Agentes
Para la implementación técnica de este sistema, se definen dos roles de liderazgo:
- **Arquitecto**: Define el "cómo" técnico, diseña los prompts y asegura la coherencia con esta arquitectura.
- **Orquestador**: Gestiona el "cuándo" y el "quién", delegando tareas y validando resultados.

## 7. Gestión del Entorno (Infraestructura)

Para garantizar la estabilidad del sistema y la correcta carga de configuraciones, se ha establecido un protocolo estricto de ejecución:

### El Script de Entrada (`./run.sh`)
El archivo `./run.sh` en la raíz del proyecto es el **único** punto de entrada autorizado para iniciar o reiniciar el entorno de Tlacuilo.

- **Responsabilidades del Script**:
    1. Cargar variables de entorno desde el archivo `.env` (saltando variables protegidas del sistema).
    2. Validar que la ruta del portafolio (`PORTAFOLIO_PATH`) sea válida.
    3. Iniciar todos los contenedores en modo **Detached** (`-d`).
- **Regla de Oro para Agentes**: NUNCA ejecutar `docker compose up` directamente. Cualquier cambio en la infraestructura, volúmenes o variables de entorno **DEBE** ir seguido de una ejecución de `./run.sh`.

*Este documento centraliza toda la información de arquitectura y servicios de Tlacuilo.*
