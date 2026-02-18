# Arquitectura Tecnológica (Stack)

Este documento define las tecnologías elegidas para construir el sistema Tlacuilo, siguiendo la filosofía de "Ingeniería de Piedra y Luz".

## 1. Infraestructura (La Piedra)
La base debe ser sólida, reproducible y aislada.

-   **Docker & Docker Compose**: Orquestación de contenedores. Todo el sistema corre encapsulado.
-   **Volúmenes Locales**: Persistencia de datos mapeada directamente al sistema de archivos del host (para que el usuario tenga control total de sus archivos `.md` y fotos).

## 2. Backend (El Cerebro)
Lógica de negocio, gestión de archivos y orquestación de IAs.

-   **Lenguaje**: Python 3.11+.
-   **Framework**: FastAPI (Rápido, tipado estricto con Pydantic).
-   **Librerías Clave**:
    -   `gitpython`: Para operaciones de Git automatizado.
    -   `httpx`: Cliente asíncrono para hablar con ComfyUI y APIs de LLM.
    -   `python-frontmatter`: Manipulación segura de metadatos en Markdown.

## 3. Frontend (La Interfaz)
La herramienta visual para el humano.

-   **Framework**: Vue 3.
-   **Build Tool**: Vite.
-   **Estilos**: TailwindCSS.
-   **Estética**: "Huitzilopochtli Wireframe" (Minimalismo brutal, alto contraste, wireframes visibles).

## 4. Motores de IA (Los Tlacuilos)
Entidades externas con las que el sistema interactúa.

-   **Tlacuilo Digital (Texto)**:
    -   Proveedor: Ollama (Local) o Google Gemini (Cloud).
    -   Interacción: API REST/Streaming.
-   **Tlacuilo Ixtli (Imagen)**:
    -   Motor: **ComfyUI** (Corriendo localmente en `:8188`).
    -   Interacción: WebSocket + API REST para encolar workflows JSON.

## 5. Estructura de Referencias
El sistema se apoya en definiciones constantes ubicadas en `docs/definitions/`:
-   `MATURITY_LEVELS.md`: Estados de madurez del proyecto.
-   `ATOMS_BITS_STRUCTURE.md`: Plantilla mental para proyectos técnicos.
-   `MIND_STRUCTURE.md`: Plantilla mental para ensayos.
