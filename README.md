# Tlacuilo: El Arquitecto del Portafolio

> "Ingeniería de Piedra y Luz"

**Tlacuilo** es una herramienta local de gestión de contenido y orquestación de IA diseñada para operar el portafolio personal. Funciona como un puente entre la escritura técnica (Markdown), la generación de contenido asistida por IA (LLM) y la estilización visual (Stable Diffusion/ComfyUI).

## Módulos Principales

### 1. Command Center (Gestión)
Panel central para visualizar y administrar los proyectos (`atoms`, `bits`, `mind`). Permite crear nuevas entradas y verificar el estado general del portafolio.

### 2. El Arquitecto (Edición)
Entorno de escritura Markdown asistido por un agente de IA especializado.
- **Modo Ingeniero**: Para documentación técnica precisa (`atoms`/`bits`).
- **Modo Filósofo**: Para ensayos reflexivos (`mind`).

### 3. Tlacuilo Studio (Visualización)
Interfaz para la generación y curaduría de imágenes.
- **Input**: Fotografías reales de hardware/piezas.
- **Proceso**: Estilización mediante ComfyUI para encajar en la estética "Obsidiana Telemetría".
- **Output**: Activos visuales listos para publicación.

### 4. Deploy Console (Publicación)
Integración con Git para versionar y desplegar cambios al repositorio remoto con un solo clic.

## Documentación y Referencias

El sistema se rige por la documentación ubicada en `docs/`. **Esta es la fuente de verdad.**

### Arquitectura y Diseño
-   [NARRATIVE.md](docs/NARRATIVE.md): Filosofía y Ciclo de Vida Documental.
-   [ARCHITECTURE.md](docs/ARCHITECTURE.md): Diagramas de sistema y API Specs.
-   [FRONTEND_ARCHITECTURE.md](docs/FRONTEND_ARCHITECTURE.md): Pantallas, UI Flows y Referencias Estéticas.
-   [INFRASTRUCTURE.md](docs/INFRASTRUCTURE.md): Docker, Servicios y Puertos.
-   [STACK.md](docs/STACK.md): Tecnologías (FastAPI, Vue, ComfyUI).

### Flujos y Procesos
-   [FUNCTIONAL_CYCLES.md](docs/FUNCTIONAL_CYCLES.md): Guía paso a paso de los ciclos de construcción.
-   [SYNCHRONIZATION.md](docs/SYNCHRONIZATION.md): Protocolos de hidratación y manejo de conflictos.
-   [DATA_PERSISTENCE.md](docs/DATA_PERSISTENCE.md): Estrategia de memoria (`.tlacuilo/`) y guardado.
-   [WORKFLOWS.md](docs/WORKFLOWS.md): Payloads técnicos de ComfyUI.
-   [CURRENT_WORKFLOW.md](docs/CURRENT_WORKFLOW.md): Referencia del problema legacy.

### Personas y Estándares
-   `AGENTS.md`: Directivas maestras para los GEMs.
-   `prompts/`: Definición de las Personas.
    -   [tlacuilo.md](prompts/tlacuilo.md): Tlacuilo Digital.
    -   [tlacuilo_ixtli.md](prompts/tlacuilo_ixtli.md): Tlacuilo Ixtli.
-   `references/`: Reglas de negocio.
    -   [STATUSES.md](references/STATUSES.md): Madurez del proyecto.
    -   [structure_technical.md](references/structure_technical.md): Guía STAR.
    -   [structure_mind.md](references/structure_mind.md): Guía Manifiesto.

## Estética y Filosofía
El sistema sigue la línea de diseño **"Huitzilopochtli Wireframe"**:
- **Interfaz**: Oscura (#050505), Monospaciada, Alto Contraste.
- **Colores**: Rojo Hematita (Acción), Turquesa (Datos), Hueso (Texto).
- **Principios**: Eficiencia Radical, Sin Adornos Innecesarios ("No Magic").
