# Ciclos Funcionales de Construcción

Este documento detalla *cómo* se construye y opera el sistema Tlacuilo desde una perspectiva de desarrollo y uso.

## 0. Ciclo de Descubrimiento (Escaneo Inicial)
Ocurre cada vez que el Backend recibe una petición de listado (`GET /projects`):
1.  **Escaneo Portafolio**: Lee directorios en `{PORTAFOLIO}/{coleccion}/`.
2.  **Identificación**: Cada carpeta es un proyecto potencial. Tlacuilo busca el archivo `{slug}.md`.
3.  **Alineación Automática**: Si el proyecto existe en el portafolio pero no en `projects/` local, se dispara la **Hidratación** (Ver `SYNCHRONIZATION.md`).

## 1. Ciclo de Scaffolding (Inicialización)
Cuando se crea un nuevo proyecto en Tlacuilo:
1.  **Input**: Usuario define `Título`, y `Colección` (Atoms/Bits/Mind).
2.  **Validación**: Verifica que el `slug` no exista en Portafolio ni en Carpeta Local.
3.  **Acción Backend**:
    -   Crea directorio local: `projects/{coleccion}/{slug}/`.
    -   Inicializa memoria interna: Crea `chat_history.json` vacío y `doc_state.json` con `status: borrador`.
    -   Crea archivo base local: `{slug}.md` usando el template.

4.  **Resultado**: Proyecto listo para redacción.

## 2. Ciclo de Redacción (Tlacuilo Digital)
...
## 5. Ciclo de Descubrimiento (Sincronización)
Para los casos donde existe un proyecto en el Portafolio pero no en la memoria local, o viceversa, Tlacuilo sigue los protocolos detallados en [SYNCHRONIZATION.md](SYNCHRONIZATION.md) y [WORKFLOWS.md](WORKFLOWS.md).
El bucle principal de creación de texto:
1.  **Context Loading**: Backend lee `.md` actual (Portafolio) + `chat_history.json` (Internal Brain). 
2.  **System Prompting**: Inyecta `prompts/tlacuilo_digital.md` como instrucción del sistema.
3.  **Interacción (Loop)**:
    -   Usuario habla -> Backend guarda -> GEM procesa -> Backend guarda -> Frontend muestra.
4.  **Generación de Borrador**:
    -   Usuario solicita "Generar Documento".
    -   Backend instruye al GEM a producir bloque Markdown.
    -   Backend escribe el bloque en el archivo `.md` (sobreescribiendo o anexando).

## 3. Ciclo de Imagen (Tlacuilo Ixtli)
El bucle de generación visual:
1.  **Upload**: Usuario sube imagen a `backend/tmp/`.
2.  **Payload Construction**: Backend lee `WORKFLOWS.md` (JSON template) e inyecta la ruta de la imagen y el prompt positivo/negativo.
3.  **Queueing**: Backend envía JSON a `ComfyUI API`.
4.  **Polling**: Backend consulta estado hasta que `status: success`.
5.  **Retrieval & Storage**:
    -   Backend descarga imagen generada.
    -   Backend mueve imagen a `{PORTAFOLIO}/public/{coleccion}/{slug}/cover.png` (o nombre secuencial).

## 4. Ciclo de Publicación (Git Ops)
El cierre del trabajo:
1.  **Trigger**: Usuario hace clic en "Publicar" en la UI.
2.  **Git Add**: Backend ejecuta `git add {proyecto_path}`.
3.  **Git Commit**: Backend ejecuta `git commit -m "feat(tlacuilo): update {slug}"`.
4.  **Git Push**: Backend ejecuta `git push origin main`.
5.  **Feedback**: UI muestra notificación de éxito/error.
