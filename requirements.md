# Tlacuilo - Requerimientos Funcionales

Este documento define los requerimientos funcionales del sistema "Tlacuilo", basado en el análisis de la documentación previa y la corrección del flujo de documentación.

## 1. Gestión del Ciclo de Vida de Documentación (Core)
El sistema debe gestionar los estados del archivo `.md`:
-   **Borrador -> Revisión -> Traducción -> Publicado**.
-   Debe permitir **reabrir** documentos publicados para ediciones futuras.

## 2. Flujo de Generación de Contenido (Tlacuilo Digital)
-   **Interfaz de Chat Integrada**: Ventana de chat para interactuar con el GEM.
-   **Persistencia de Contexto (Memoria)**:
    -   El sistema debe **guardar** automáticamente el historial de conversaciones por proyecto.
    -   Al abrir un proyecto, el sistema debe **cargar** el historial previo para darle contexto al GEM.
-   **Asistente de Redacción**:
    -   Capacidad de generar el contenido Markdown basado en la conversación.

## 3. Flujo de Generación de Imágenes (Tlacuilo Ixtli)
-   **Integración Local con ComfyUI**.
-   **Flujo de Trabajo**:
    1.  Subida de Referencia.
    2.  Generación con parámetros predefinidos (JSON).
    3.  Aprobación y guardado automático en `public/`.
-   **Estética Obligatoria**: "Obsidiana Telemetría".

## 4. Gestión de Proyectos (Command Center)
-   **Visualización**: Listar proyectos mostrando tanto su estatus de madurez (`idea`, `poc`, etc.) como su estado de documentación.
-   **Creación**: Generar estructura de carpetas y archivos base.

## 5. Automatización y Despliegue
-   **Traducción Automática**: Flujo para traducir de ES a EN tras la aprobación del borrador.
-   **Git Ops**: Commit y Push automatizados al finalizar el ciclo de revisión.

## 6. Requerimientos No Funcionales
-   **Privacidad Local**: Todo corre en Localhost.
-   **Interfaz UI**: Estética "Huitzilopochtli Wireframe".
