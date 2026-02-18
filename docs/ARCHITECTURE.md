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
-   **Estatus de Documentación** (`doc_status`): Define la etapa en el flujo de Tlacuilo (`borrador`, `revisión`, `traducción`, `publicado`). 
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
          "doc_status": "borrador",
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
        1.  El `slug` se genera desde el `name` si no se provee. Debe ser kebab-case.
        2.  **Unicidad Externa**: No debe existir la carpeta en `{PORTAFOLIO}/{coleccion}/{slug}`.
        3.  **Unicidad Interna**: No debe existir la carpeta en `projects/{coleccion}/{slug}/`.
        4.  Si falla alguna, regresa `400 Bad Request`.
-   `GET /projects/{collection}/{slug}`: Lee el contenido del archivo `{slug}.md` y recupera el estatus desde `doc_state.json`.
-   `POST /projects/forget/{collection}/{slug}`: **Forget Action**. Elimina permanentemente la memoria local (carpeta en `projects/`). Utiliza `shutil.rmtree()` para borrar el rastro.
-   `POST /projects/resurrect/{collection}/{slug}`: **Resurrect Action**. Restaura el archivo arquitectónico (`{slug}.md`) desde la memoria local hacia el portafolio si este se ha perdido.


```

### C. Servicio de Tlacuilo Digital (`/chat`)
Orquesta la conversación con el GEM y gestiona el **Ciclo de Entrevista**.

-   `POST /chat/start/{project_id}`: **[NUEVO] Inicia la Entrevista**.
    -   **Lógica**:
        1.  Detecta el tipo de proyecto (`atoms`, `bits`, `mind`).
        2.  Carga el **System Prompt de Estrategia** correspondiente:
            -   `atoms/bits`: Estrategia Forense (Ver `docs/definitions/ATOMS_BITS_STRUCTURE.md`).
            -   `mind`: Estrategia Manifiesto (Ver `docs/definitions/MIND_STRUCTURE.md`).
        3.  Inyecta el primer mensaje del Agente en el historial: *"Hola, soy Tlacuilo. Empecemos definiedo la [Primera Sección]. ¿Cuál es el contexto?"*
    -   **Response**: Retorna el historial actualizado.

-   `POST /chat/message`: Envía un mensaje al GEM.
    -   **Payload**:
        ```json
        {
          "project_id": "slug",
          "message": "Texto del usuario",
          "mode": "interview" // "interview" (aplica reglas estrictas) | "free_chat" (libre)
        }
        ```
    -   **Comportamiento en `mode: interview`**:
        -   El System Prompt DEBE instruir al GEM a **NO** generar el documento completo todavía.
        -   El GEM debe validar si la sección actual (ej. Situación) está completa.
        -   Si sí -> Pasa a la siguiente (ej. Tarea).
        -   Si no -> Hace preguntas de profundización (Follow-up questions).
    
-   `GET /chat/history/{project_id}`: Recupera la memoria de la conversación (`chat_history.json`).
-   `POST /chat/draft`: Solicita al GEM que genere el contenido Markdown final basado en la charla acumulada.

### C. Servicio de Tlacuilo Ixtli (`/studio`)
Puente con ComfyUI.
-   `POST /studio/upload`: Recibe la imagen "dirty" de referencia.
-   `POST /studio/generate`: Envía el workflow JSON a ComfyUI con la imagen y parámetros.
-   `GET /studio/status/{prompt_id}`: Consulta el estado de la generación en ComfyUI.
-   `POST /studio/save`: Mueve la imagen generada de `output/` a la carpeta `public/` del proyecto.

### D. Servicio de Git (`/ops`)
Automatización de versionado.
-   `POST /ops/commit`: Realiza `git add .` y `git commit -m "update: {project}"`.
-   `POST /ops/push`: Empuja los cambios al remoto.

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
*Este documento centraliza toda la información de arquitectura y servicios de Tlacuilo.*
