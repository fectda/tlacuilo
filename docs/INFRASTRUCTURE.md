# Infraestructura (Docker)

La infraestructura de Tlacuilo se basa en contenedores Docker orquestados por Docker Compose, garantizando un entorno aislado y reproducible.

## Servicios del Contenedor

### 1. `backend` (El Cerebro)
-   **Imagen Base**: `python:3.11-slim`
-   **Responsabilidad**: Ejecutar la API FastAPI, gestionar la lógica de negocio y conectarse con los servicios externos (ComfyUI, Ollama).
-   **Volúmenes**:
    -   `./backend:/app`: Código fuente en vivo.
    -   `${PORTAFOLIO_PATH}:/data`: Montaje del portafolio real para lectura/escritura (Externo).
    -   `./data:/app/internal_data`: Persistencia de memoria interna (Chats, estados).
-   **Puertos**: Expone `8000:8000`.
-   **Variables de Entorno**:
    -   `PORTAFOLIO_PATH`: Ruta al portafolio en el host.
    -   `COMFYUI_HOST`: URL de la instancia local de ComfyUI (ej. `http://host.docker.internal:8188`).

### 2. `frontend` (La Cara)
-   **Imagen Base**: `node:20-slim`
-   **Responsabilidad**: Servir la aplicación Vue 3 + Vite.
-   **Volúmenes**:
    -   `./frontend:/app`: Código fuente para desarrollo (HMR).
-   **Puertos**: Expone `5173:5173`.

### 3. Servicios Externos (No Dockerizados por Tlacuilo)
Tlacuilo asume que estos servicios ya corren en el host del usuario ("Bring Your Own AI"):
-   **ComfyUI**: Debe estar corriendo en el host (puerto 8188). Tlacuilo se conecta vía red.
-   **Ollama / LLM API**: Debe ser accesible desde el contenedor backend.

## Ciclos Funcionales de Construcción

### Ciclo de Desarrollo (Dev)
1.  `docker compose up`: Levanta backend y frontend con *Hot Reload*.
2.  Desarrollador edita código en `/frontend` o `/backend`.
3.  Cambios se reflejan inmediatamente.

### Ciclo de Producción (Local)
1.  `docker compose -f docker-compose.prod.yml up --build`.
2.  Frontend se compila a estático (HTML/JS/CSS).
3.  Backend sirve los estáticos + API.
4.  Optimizado para uso diario sin overhead de desarrollo.
