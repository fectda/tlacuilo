# Arquitectura de Información Frontend y Flujos UI

Este documento define la estructura visual, navegación y acciones disponibles en la interfaz de Tlacuilo.

## 1. Filosofía de Diseño
-   **Estética UI (Tlacuilo)**: "Huitzilopochtli Wireframe". Inspirada en `design/DESIGN_BLUEPRINT.md` pero optimizada para herramientas de trabajo (Data Density). No es obligatorio seguir al pie de la letra los PDFs de arte para la interfaz.
-   **Estética Output (Contenido Generado)**: **ESTRICTAMENTE** adherida a las guías del portafolio (Ver `AGENTS.md`). El resultado final (imágenes, textos) SÍ debe cumplir con el PDF de estética Mexica.

## 2. Mapa del Sitio (Sitemap)

```mermaid
graph TD
    Dashboard[Command Center] --> Project[Project Detail]
    Project --> Editor[Tlacuilo Digital (Chat)]
    Project --> Studio[Tlacuilo Ixtli (Studio)]
    Project --> Settings[Configuración Proyecto]
    
    Dashboard --> GlobalSettings[Config Global]
    Dashboard --> Deploy[Deploy Console]
```

## 3. Pantallas y Accionables

### A. Command Center (Home)
La vista de águila de todo el portafolio.
-   **Componentes**:
    -   `StatBar`: Métricas globales (Proyectos Totales, Drafts, Published).
    -   `ProjectGrid`: Grilla de tarjetas de proyecto.
    -   `SearchBar`: Buscador en tiempo real por título o slug.
    -   `FilterBar`:
        -   Por Colección: `atoms`, `bits`, `mind`.
        -   Por Ciclo Documental: `draft`, `review`, `published`. (No confundir con estatus del proyecto `idea`, `poc`, etc).
-   **Acciones**:
    -   `[primary] New Project`: Abre modal de creación.
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
Donde se crea el texto.
-   **Layout**:
    -   `ChatArea` (Izquierda 60%): Historial de mensajes.
    -   `DraftPreview` (Derecha 40%): Render en tiempo real del Markdown actual.
-   **Acciones**:
    -   `[input] Send Message`: Hablar con el GEM.
    -   `[secondary] Update Context`: Forzar recarga del archivo `.md` del disco.
    -   `[primary] Generate Draft`: Solicitar al GEM escribir el bloque.
    -   `[success] Save to Disk`: Escribir cambios al portafolio.

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

## 4. Referencias Estéticas (Fuente de Verdad)
El sistema **DEBE** leer los estilos y tokens visuales de los archivos ubicados en el portafolio real:
1.  **Reglas Maestras**: `${PORTAFOLIO}/design/DESIGN_BLUEPRINT.md`.
2.  **Teoría Visual**: `${PORTAFOLIO}/design/altepetl digital/Estética Mexica y Huitzilopochtli para Web.pdf`.
3.  **Referencias de Estilo**:
    -   Atoms: `design/altepetl digital/images/atoms_single.png`
    -   Bits: `design/altepetl digital/images/bits_single.png`
    -   Mind: `design/altepetl digital/images/mind_single.png`
