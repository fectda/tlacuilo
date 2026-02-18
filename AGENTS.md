# Tlacuilo AI Agents Registry (Master Index)

Este documento es el **Índice Maestro** de los agentes y sus Fuentes de Verdad.
Cada agente tiene un rol, alcance y restricciones específicas definidas en su propio archivo de documentación.

> [!IMPORTANT]
> **REGLA DE ORO**: Es mandatorio hacer lo que dice la documentación.
> 1.  **No Inventar**: No se puede inventar nada que no esté en la documentación.
> 2.  **Preguntar**: Si se necesita hacer algo que no esté en la documentación, se DEBE DETENER el trabajo y preguntar.
> 3.  **Fuente de Verdad**: Todos los agentes deben obedecer `docs/ARCHITECTURE.md` y `docs/STACK.md`.

## 1. El Orquestador (`@orchestrator`)
- **Archivo**: [`docs/agents/orchestrator.md`](docs/agents/orchestrator.md)
- **Rol**: Planificador Jefe. No escribe código, solo delega, valida y **Diseña Prompts**.
- **Fuentes de Verdad**:
    -   [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): Diagramas de flujo, endpoints y servicios.
    -   [`docs/INFRASTRUCTURE.md`](docs/INFRASTRUCTURE.md): Configuración de Docker, volúmenes y redes.
    -   [`docs/STACK.md`](docs/STACK.md): Tecnologías permitidas (FastAPI, Vue, etc.).
    -   [`docs/NARRATIVE.md`](docs/NARRATIVE.md): Filosofía y propósito del sistema.
    -   [`docs/FUNCTIONAL_CYCLES.md`](docs/FUNCTIONAL_CYCLES.md): Ciclos de vida del contenido.

## 2. Agente de Infraestructura (`@infrastructure`)
- **Archivo**: [`docs/agents/infrastructure.md`](docs/agents/infrastructure.md)
- **Rol**: Ingeniero DevOps.
- **Fuentes de Verdad**:
    -   [`docs/INFRASTRUCTURE.md`](docs/INFRASTRUCTURE.md): Puertos, volúmenes y servicios definidos.
    -   [`docs/DATA_PERSISTENCE.md`](docs/DATA_PERSISTENCE.md): Estrategia de almacenamiento (Local vs Portafolio).

## 3. Agente Backend (`@backend`)
- **Archivo**: [`docs/agents/backend.md`](docs/agents/backend.md)
- **Rol**: Ingeniero de Software (Python/FastAPI).
- **Fuentes de Verdad**:
    -   [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): Contratos de API (Endpoints/Payloads).
    -   [`docs/NARRATIVE.md`](docs/NARRATIVE.md): Contexto del negocio.

## 4. Agente Frontend (`@frontend`)
- **Archivo**: [`docs/agents/frontend.md`](docs/agents/frontend.md)
- **Rol**: Desarrollador UI/UX (Vue 3).
- **Fuentes de Verdad**:
    -   [`docs/FRONTEND_ARCHITECTURE.md`](docs/FRONTEND_ARCHITECTURE.md): Estructura visual, componentes y estados.
    -   [`docs/API_CONTRACTS.md`](docs/API_CONTRACTS.md): Definición de respuestas JSON esperadas del Backend.

---

## 5. Referencia de Personas (Legacy / Context)

> **Nota**: La definición canónica de estas personalidades y sus "Códices Primigenios" se encuentra detallada en **`docs/NARRATIVE.md` -> Sección "Los Ancestros"**. Consultar ese documento para entender el origen de la voz y la estética.

### Tlacuilo Digital (Texto)
-   **Fuentes de Verdad**: 
    -   [`docs/definitions/ATOMS_BITS_STRUCTURE.md`](docs/definitions/ATOMS_BITS_STRUCTURE.md): Estructura Forense (Spec Sheet) para proyectos técnicos.
    -   [`docs/definitions/MIND_STRUCTURE.md`](docs/definitions/MIND_STRUCTURE.md): Estructura Manifiesto (Ensayo) para filosofía.
    -   [`docs/definitions/MATURITY_LEVELS.md`](docs/definitions/MATURITY_LEVELS.md): Clasificación de proyectos (Idea, POC, WIP, Done).
-   **Función**: Escriba Digital y Guardián del Contexto.

### Tlacuilo Ixtli (Imagen)
-   **Fuentes de Verdad**: [`design/DESIGN_BLUEPRINT.md`](design/DESIGN_BLUEPRINT.md) (Especificaciones visuales geométricas).
-   **Función**: Ingeniero Visual (ComfyUI).
