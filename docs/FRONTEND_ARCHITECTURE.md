# Arquitectura de Información Frontend y Flujos UI

Este documento define la estructura visual, navegación y acciones disponibles en la interfaz de Tlacuilo.

## 1. Filosofía de Diseño
-   **Estética UI (Tlacuilo)**: "Huitzilopochtli Wireframe". Inspirada en `${PORTAFOLIO}/design/DESIGN_BLUEPRINT.md` pero optimizada para herramientas de trabajo (Data Density). No es obligatorio seguir al pie de la letra los PDFs de arte para la interfaz.
-   **Estética Output (Contenido Generado)**: **ESTRICTAMENTE** adherida a las guías del portafolio (Ver [AGENTS.md](../AGENTS.md)). El resultado final (imágenes, textos) SÍ debe cumplir con el PDF de estética Mexica.

## 2. Reglas de Implementación (Copia y Textos)
-   **Idioma**: Todo el contenido, etiquetas, mensajes de error y copies de la interfaz deben estar **estrictamente en español**.
-   **No Hardcoding de Textos**: Queda **prohibido** tener texto hardcodeado en los componentes. Todos los textos deben provenir de variables, constantes o un sistema de i18n.
-   **Componentes Reutilizables**: Todo el desarrollo debe priorizar la creación y uso de componentes reutilizables para mantener la consistencia y facilitar el mantenimiento.
-   **No Hardcoding de Colores**: Queda **prohibido** el uso de colores hardcodeados en las vistas. Todos los colores deben derivarse directamente del sistema de temas (tokens de Tailwind o variables CSS).
-   **Gestión de SVGs**: Los archivos SVG **no deben** formar parte del código de las vistas/templates. Deben llamarse desde archivos externos para mantener la limpieza del componente.


## 3. Mapa del Sitio (Sitemap)

```mermaid
graph TD
    Dashboard[Command Center] --> Project[Project Detail]
    Project --> Editor[Tlacuilo Digital (Chat)]
    Project --> Studio[Tlacuilo Ixtli (Studio)]
    Project --> Settings[Configuración Proyecto]
    
    Dashboard --> GlobalSettings[Config Global]
    Dashboard --> Deploy[Deploy Console]
```

## 4. Pantallas y Accionables

### A. Command Center (Home)
La vista de águila de todo el portafolio.
-   **Componentes**:
    -   `StatBar`: Métricas globales (Proyectos Totales, Drafts, Published).
    -   `SystemVitals`: Cuadro de disponibilidad de servicios (Backend API, Ollama, ComfyUI).
    -   `ProjectGrid`: Grilla de tarjetas de proyecto.
        -   **Card Body**:
            1.  **Título**: Nombre del proyecto.
            2.  **Slug**: ID del proyecto.
            3.  **Descripción**: Resumen corto extraído del Frontmatter.
            4.  **Estatus de Documentación**: Etapa del ciclo (`borrador`, `revisión`, `traducción`, `publicado`).
            5.  **Estatus de Publicación**: Indicador de visibilidad (`DRAFT` o `PUBLISHED`).
    -   `SearchBar`: Buscador en tiempo real por título o slug.
    -   `FilterBar`:
        -   Por Colección: `atoms`, `bits`, `mind`.
        -   Por Estatus de Documentación: `borrador`, `revisión`, `traducción`, `publicado`.
-   **Acciones**:
    -   `[primary] New Project`: Abre modal de creación.
        -   **Campos**:
            1.  **Nombre**: Texto libre.
            2.  **Slug**: Generado automáticamente o manual (kebab-case).
            3.  **Colección**: Dropdown (`atoms`, `bits`, `mind`).
    -   `[secondary] Sync`: Actualiza estado desde disco.
    -   `[icon] Deploy`: Navega a Deploy Console.

### B. Project Detail (Hub del Proyecto)
El centro de mando de un proyecto específico.
-   **Header**: Título, Slug, Estatus (Madurez), Badges de Documentación.
-   **Tabs**:
    1.  **Overview**: Resumen, Frontmatter editable, Galería rápida.
    2.  **Digital (Texto)**: Acceso al Chat.
    3.  **Ixtli (Imagen)**: Acceso al Studio.
-   **Acciones**:
    -   `[primary] Open Folder`: Abre en explorador de archivos del OS.
    -   `[danger] Delete Memory`: Borra historial de chat.

### C. Tlacuilo Digital (Chat Interface)
Donde se crea el texto. El corazón de la Fase de Entrevista.

-   **Layout (Split View)**:
    -   **ChatArea (Izquierda 60%)**: Historial de mensajes scrollable.
        -   *Estado Inicial*: Si el historial está vacío, debe llamar a `POST /chat/start/{project_id}` automáticamente al montar.
        -   *Render*: Soporte Markdown para mensajes del agente.
        -   *Input*: "Send Message" bloqueado mientras el agente responde.
    -   **DraftPreview (Derecha 40%)**:
        -   Render en tiempo real del archivo `.md` actual.
        -   Debe refrescarse cuando el usuario gatilla la acción "Generar Borrador".
        -   Sticky header con el botón "Save to Disk".
        -   **Spellcheck**: Responsabilidad exclusiva del Frontend. Debe mostrar errores ortográficos visualmente antes de permitir el guardado.
-   **Acciones**:
    -   `[input] Send Message`: Envía payload con `mode: interview` (por defecto) o `mode: free_chat` (si el usuario activa un toggle).
    -   `[primary] Generate Draft`: Solicita al GEM escribir el bloque. (Habilitado solo cuando el agente indica que tiene suficiente info).
    -   `[success] Save to Disk`: Escribir cambios al portafolio.
    -   `[danger] Reset Memory`: Limpia el historial local y reinicia la entrevista.

### D. Tlacuilo Studio (Image Interface)
Donde se crean las imágenes.
-   **Layout**:
    -   `ReferenceArea` (Izquierda): Upload de imagen "dirty".
    -   `PromptArea` (Centro): Configuración de workflow (Estilo, Trigger word).
    -   `ResultArea` (Derecha): Imagen generada.
-   **Acciones**:
    -   `[primary] Generate`: Enviar a ComfyUI.
    -   `[secondary] Stylize (Huitzilopochtli)`: Cargar preset de estilo.
    -   `[success] Approve & Save`: Mover a `public/`.

## 5. Referencias Estéticas (Fuente de Verdad)
El sistema **DEBE** leer los estilos y tokens visuales de los archivos ubicados en el portafolio real:
1.  **Reglas Maestras**: `${PORTAFOLIO}/design/DESIGN_BLUEPRINT.md`.
2.  **Teoría Visual**: `${PORTAFOLIO}/design/altepetl digital/Estética Mexica y Huitzilopochtli para Web.pdf`.
3.  **Referencias de Estilo**:
    -   Atoms: `design/altepetl digital/images/atoms_single.png`
    -   Bits: `design/altepetl digital/images/bits_single.png`
    -   Mind: `design/altepetl digital/images/mind_single.png`
