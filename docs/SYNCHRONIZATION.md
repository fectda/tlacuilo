# Estrategia de Sincronización

Este documento define las reglas de oro para la sincronización entre el **Portafolio** (Sistema de Archivos Externo) y la **Memoria Local** (`projects/`).

## Principios Fundamentales

1.  **La Verdad está en el Portafolio**: El contenido final de los archivos `.md` en el portafolio es la fuente de verdad para la publicación.
2.  **La Memoria Local es Resiliente**: Si el Portafolio falla o falta un archivo, la Memoria Local (`projects/{slug}/{slug}.md`) asume el control temporalmente para evitar la pérdida de datos y permitir la visibilidad en la UI.
3.  **Local-First en Creación**: Al crear un proyecto, los metadatos iniciales (título, tipo) se escriben PRIMERO en la Memoria Local.

## Protocolos de Manejo de Proyectos

### 1. Creación de Proyectos
Cuando se crea un proyecto nuevo:
1.  Se genera el `slug` basado en el nombre.
2.  Se crea la carpeta en `projects/{coleccion}/{slug}/`.
3.  Se copia la plantilla correspondiente (`atoms`, `bits`, `mind`).
4.  **Inyección de Metadatos**: El sistema reemplaza el título genérico de la plantilla con el nombre proporcionado por el usuario en el archivo local `{slug}.md`.
5.  El proyecto nace en estado `borrador` y vive solo localmente hasta que se decida "Publicar" o "Restaurar" al portafolio.

### 2. Lectura y Listado (Omni-Scanner)
El proceso `list_projects` escanea ambas ubicaciones:
1.  **Portafolio**: Busca carpetas y archivos en el portafolio.
2.  **Local**: Busca carpetas en `projects/`.

**Resolución de Conflictos de Metadatos**:
-   **Escenario Ideal**: El archivo existe en Portafolio. Se leen los metadatos de ahí.
-   **Escenario Huérfano (Missing MD)**: El archivo existe en Local pero NO en Portafolio. Se leen los metadatos del archivo local.
-   **Escenario Roto (Missing File)**: La carpeta existe en Local pero NO hay archivo `.md` (ni local ni remoto).
    -   El sistema **NO** oculta el proyecto.
    -   Muestra el `slug` como nombre.
    -   Marca el proyecto con `missing_md: true` y `missing_files: true`.
    -   Esto permite al usuario ver que algo existe y tomar acciones (borrar o investigar), en lugar de tener "archivos fantasma" invisibles.

### 3. Sincronización de Contenido
-   Tlacuilo NO sobrescribe automáticamente el Portafolio al iniciar.
-   La sincronización hacia el Portafolio ocurre explícitamente mediante acciones de usuario (Guardar, Publicar).

---
*Documento actualizado para reflejar la estrategia "Local-First" y robustez ante archivos faltantes.*
