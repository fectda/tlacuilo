# Persistencia de Datos y Memoria

Tlacuilo requiere persistir el **contexto** (historial de chat, estado) sin contaminar el portafolio del usuario.

## 1. El Portafolio (La Verdad Externa)
Los datos finales viven en el sistema de archivos del usuario (`PORTAFOLIO_PATH`).
-   **Ubicación**: Carpeta del portafolio (ej. `~/code/clowd/portafolio`).
-   **Contenido Permitido**: Únicamente archivos `.md` (contenido) y assets en `public/` (imágenes).
-   **Regla de Oro**: Tlacuilo **NUNCA** escribe archivos de configuración, logs o carpetas ocultas (`.tlacuilo`) en este directorio.

## 2. La Memoria del Tlacuilo (El Cerebro Interno)
Toda la meta-información y el contexto de las conversaciones se almacenan **dentro de la instalación de Tlacuilo**, no en el portafolio.

-   **Ubicación Física**: Carpeta `data/` en la raíz del proyecto Tlacuilo.
-   **Docker Volume**: `./data:/app/data` (Montado en el contenedor).
-   **Estructura de Almacenamiento**:
    -   Ruta interna: `data/{coleccion}/{slug}/`.
-   **Archivos de Memoria**:
    -   `chat_history.json`: Historial de conversación con Tlacuilo Digital.
    -   `session_state.json`: Estado del flujo actual.

## 3. Ventajas de esta Estrategia
1.  **Limpieza**: El portafolio permanece puro (Markdown + Imágenes).
2.  **Seguridad**: Si borras el portafolio, la memoria del asistente sigue en Tlacuilo.
3.  **Desacople**: Tlacuilo es una capa de servicios sobre los datos, no un parásito de los datos.

## 4. Mapeo de Identidad
Para vincular la memoria con el proyecto real:
-   **ID del Proyecto**: `{coleccion}/{slug}` (ej. `atoms/mi-teclado`).
-   Cuando Tlacuilo abre `atoms/mi-teclado`, busca en su `/brain/atoms/mi-teclado` si existe historial previo.
