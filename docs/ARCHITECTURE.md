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
        API --> Comfy[ComfyUI (Imágenes)]
        API --> GEM[Ollama/Gemini (Texto)]
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
-   Metadatos Críticos (Frontmatter): `status` (idea, poc, wip, done), `title`, `description`.

### Nivel 3: Documentación (El Ciclo)
Dentro de cada proyecto existe el archivo principal `.md` (ej. `index.md` o `nombre.md`).
-   Estado del Documento: Gestionado por Tlacuilo (Draft, Review, Published).
-   Historial de Chat: Contexto persistente de la conversación con el GEM.

## 3. Servicios API Requeridos (Backend)

### A. Servicio de Proyectos (`/projects`)
Gestiona la lectura y escritura en el sistema de archivos.
-   `GET /projects`: Lista todos los proyectos escaneando las carpetas.
-   `POST /projects`: Crea un nuevo proyecto (scaffolding de carpetas).
-   `GET /projects/{collection}/{slug}`: Lee el contenido y metadatos de un proyecto específico.

### B. Servicio de Tlacuilo Digital (`/chat`)
Orquesta la conversación con el GEM.
-   `POST /chat/message`: Envía un mensaje al GEM, incluyendo el contexto del proyecto y el historial previo.
-   `GET /chat/history/{project_id}`: Recupera la memoria de la conversación.
-   `POST /chat/draft`: Solicita al GEM que genere el contenido Markdown final basado en la charla.

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
