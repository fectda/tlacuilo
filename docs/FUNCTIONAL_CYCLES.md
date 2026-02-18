# Ciclos Funcionales de Construcción

Este documento detalla *cómo* se construye y opera el sistema Tlacuilo desde una perspectiva de desarrollo y uso.

## 1. Ciclo de Scaffolding (Inicialización)
Cuando se crea un nuevo proyecto en Tlacuilo:
1.  **Input**: Usuario define `Título`, `Slug` y `Colección` (Atoms/Bits/Mind).
2.  **Acción Backend**:
    -   Crea directorio en Portafolio: `{PORTAFOLIO}/{coleccion}/{slug}/`.
    -   Crea archivo base: `index.md` con Frontmatter inicial (`status: idea`).
    -   Inicializa memoria interna: Crea carpeta en `data/{coleccion}/{slug}/` y `chat_history.json` vacío.
3.  **Resultado**: Proyecto listo.

## 2. Ciclo de Redacción (Tlacuilo Digital)
El bucle principal de creación de texto:
1.  **Context Loading**: Backend lee `.md` actual (Portafolio) + `chat_history.json` (Internal Brain).
2.  **System Prompting**: Inyecta `prompts/tlacuilo.md` como instrucción del sistema.
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
