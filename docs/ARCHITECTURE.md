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

> [!NOTE]
> Para detalles sobre cómo se manejan las discrepancias entre el Portafolio y la Memoria Local (ej. archivos faltantes), consultar [SYNCHRONIZATION.md](SYNCHRONIZATION.md).

### Nivel 3: Documentación (El Ciclo)
Dentro de cada proyecto existe el archivo principal `.md` cuyo nombre es igual al slug (ej. `mi-proyecto.md`).
-   Estado del Documento: Gestionado por Tlacuilo fuera del archivo (Local Memory).
-   Historial de Chat: Contexto persistente de la conversación con el GEM.

## 3. Servicios API Requeridos (Backend)

### A. Servicio de Proyectos (`/projects`)
Gestiona la lectura y escritura en el sistema de archivos (Portafolio y Local).
-   `GET /projects`: Lista todos los proyectos. Ejecuta el **Ciclo de Descubrimiento** (Alineación Portafolio <-> Local).
    -   El frontend recibe los proyectos agrupados por colección con esta estructura (Contrato API):
    ```json
    {
      "atoms": [
        {
          "id": "slug-identificador",
          "name": "Título del Proyecto",
          "description": "Breve resumen del frontmatter",
          "doc_status": "revisión",
          "published": false,
          "type": "atoms"
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
        2. **Unicidad Externa**: No debe existir la carpeta en el Portafolio.
        3. **Unicidad Interna**: No debe existir la carpeta en `projects/` local.
-   `POST /api/{collection}/{slug}/forget`: **Forget Action**. Elimina permanentemente la memoria local (carpeta en `projects/`).
-   `POST /api/{collection}/{slug}/resurrect`: **Resurrect Action**. Restaura el archivo arquitectónico (`{slug}.md`) desde la memoria local hacia el portafolio.

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

-   `GET /api/{collection}/{slug}/content`: Obtiene el contenido del documento aplicando Reglas de Negocio.
    -   **Responsabilidad**: Devolver el texto del archivo `.md` y su estado.
    -   **Lógica de Selección (El Validador)**:
        1.  **Vacío (Proyecto Nuevo)**: Si no existe en ningún lado -> Devuelve Plantilla Base.
        2.  **Semilla (Hidratación)**: Si Portafolio existe pero Local no -> Copia Portafolio a Local y devuelve contenido.
        3.  **Sesión Activa (`is_working_copy_active: true`)**: Si hay trabajo en curso -> Devuelve Local (Ignora Portafolio).
        4.  **Sincronización Pasiva (`is_working_copy_active: false`)**: Si existe en ambos y no hay sesión -> Actualiza Local desde Portafolio y devuelve contenido. Estado: `revisión`.
    -   **Respuesta**: `{ "content": "..." }`.
-   `GET /api/{collection}/{slug}/chat/history`: Obtiene el historial de conversación.
    -   **Responsabilidad**: Devolver la lista de mensajes VISIBLES del `chat_history.json`. Filtra y oculta los mensajes con `system_only: true`.
    -   **Respuesta**: `{ "messages": [...] }`. Si está vacío o corrupto, devuelve `{ "messages": [] }`.
-   `POST /api/{collection}/{slug}/revert`: **Abortar/Retomar Original**.
    -   **Responsabilidad**: Descartar el borrador local actual y restaurar la versión del Portafolio.
    -   **Efecto**: Sobreescribe el `{slug}.md` local con el oficial, apaga el validador (`is_working_copy_active: false`). Mantiene el historial de chat. Regresa el estado a `revisión`.

**B. Ciclo de Entrevista**
-   `POST /api/{collection}/{slug}/init`: **Arranque de Sesión (Trigger)**.
    -   **Responsabilidad**: Evaluar estado y, si es necesario, construir el **Contexto Cero** (System Prompt) para delegar la ejecución al endpoint `/message`.
    -   **Base de Conocimiento**:
        -   System Prompt: `prompts/system/tlacuilo_digital.md`
    -   **Escenarios de Negocio**:
        1.  **Lienzo en Blanco (Nuevo)**: Historial vacío -> Construye Payload con System Prompt -> Llama internamente a `/message` (Trigger oculto).
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
            -   Carga el **Template** estructural del documento.
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
    -   **Responsabilidad**: Generar la primera versión en Inglés O refinar un borrador existente.
    -   **Input**: `{ "from_scratch": boolean, "instruction": "string (requerido si from_scratch es false)", "current_draft": "string (requerido si from_scratch es false)" }`.
    -   **Lógica de Negocio**:
        1.  **Traducción Directa (`from_scratch: true`)**:
            -   Ignora `instruction` y `current_draft`.
            -   **Contexto**: Solo `{slug}.md` (Fuente).
            -   **Prompt**: System Prompt de Traducción + "contexto" + "instrucciones de formato".
        2.  **Refinamiento (`from_scratch: false`)**:
            -   Requiere `instruction` (Feedback Usuario) y `current_draft` (Estado actual del editor).
            -   **Contexto**: `{slug}.md` (Fuente) + `current_draft` (Target) + `instruction`.
            -   **Prompt**: System Prompt + "Contexto" + "instrucciones de formato".
    -   **Output**: `{ "content": "..." }`. NO guarda en disco. 

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
Puente con ComfyUI para generación de imágenes.

-   `POST /api/studio/generate`: **Generar Imagen**.
    -   **Responsabilidad**: Encolar un workflow en ComfyUI.
    -   **Input**: `{ "prompt": "...", "base_image": "base64..." (opcional), "workflow_id": "txt2img|img2img" }`.
    -   **Proceso**:
        1.  Seleccionar workflow template.
        2.  Inyectar prompt y semillas.
        3.  Llamar a ComfyUI API (`POST /prompt`).
    -   **Respuesta**: `{ "prompt_id": "comfy-uuid" }`.

-   `GET /api/studio/history/{prompt_id}`: **Consultar Estado**.
    -   **Responsabilidad**: Polling del estado de la generación.
    -   **Proceso**: Consultar ComfyUI history.
    -   **Respuesta**: 
        -   **Pendiente**: `{ "status": "running" }`.
        -   **Listo**: `{ "status": "completed", "url": "http://comfyui:8188/view?filename=..." }`.

-   `POST /api/{collection}/{slug}/studio/save`: **Guardar Imagen**.
    -   **Responsabilidad**: Descargar la imagen de ComfyUI y guardarla en la carpeta del proyecto.
    -   **Input**: `{ "image_url": "...", "filename": "cover.png" }`.
    -   **Proceso**:
        1.  Descargar stream desde `image_url`.
        2.  Guardar en `projects/{collection}/{slug}/public/assets/{filename}`.
    -   **Respuesta**: `{ "local_path": "/assets/{filename}" }`.

**F. Publicación Global (Git Ops)**
-   `POST /api/{collection}/{slug}/publish`: **Publicación Final**.
    -   **Responsabilidad**: Marcar el proyecto como COMPLETADO y sincronizar con el repositorio remoto.
    -   **Input**: `{}`.
    -   **Validación**: Debe existir versión en Inglés (`en/{slug}.md`).
    -   **Proceso**:
        1.  **Estado**: Actualizar `doc_state.json` -> `doc_status: publicado`.
        2.  **Sistema (No Agentes)**: El backend ejecuta comandos git (`add`, `commit`, `push`) de forma automatizada y segura. **NUNCA** delegar comandos git a los agentes.
    -   **Respuesta**: 200 OK.



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
## 5. Roles de Agentes
Para la implementación técnica de este sistema, se definen dos roles de liderazgo:
- **Arquitecto**: Define el "cómo" técnico, diseña los prompts y asegura la coherencia con esta arquitectura.
- **Orquestador**: Gestiona el "cuándo" y el "quién", delegando tareas y validando resultados.

## 6. Gestión del Entorno (Infraestructura)

Para garantizar la estabilidad del sistema y la correcta carga de configuraciones, se ha establecido un protocolo estricto de ejecución:

### El Script de Entrada (`./run.sh`)
El archivo `./run.sh` en la raíz del proyecto es el **único** punto de entrada autorizado para iniciar o reiniciar el entorno de Tlacuilo.

- **Responsabilidades del Script**:
    1. Cargar variables de entorno desde el archivo `.env` (saltando variables protegidas del sistema).
    2. Validar que la ruta del portafolio (`PORTAFOLIO_PATH`) sea válida.
    3. Iniciar todos los contenedores en modo **Detached** (`-d`).
- **Regla de Oro para Agentes**: NUNCA ejecutar `docker compose up` directamente. Cualquier cambio en la infraestructura, volúmenes o variables de entorno **DEBE** ir seguido de una ejecución de `./run.sh`.

*Este documento centraliza toda la información de arquitectura y servicios de Tlacuilo.*
