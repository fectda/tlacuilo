# Tlacuilo AI Agents Registry (Master Index)

Este documento es el **Índice Maestro** de los agentes y sus Fuentes de Verdad.
Cada agente tiene un rol, alcance y restricciones específicas definidas en su propio archivo de documentación.

---

> [!CAUTION]
> ## PROTOCOLO DE ARRANQUE OBLIGATORIO — LEER ANTES DE CUALQUIER ACCIÓN
>
> **Todo agente, en toda sesión, sin excepción, DEBE ejecutar los siguientes pasos ANTES de escribir una sola línea de código o responder con una propuesta técnica:**
>
> ### Paso 1 — Leer los documentos de arquitectura base
> ```
> docs/ARCHITECTURE.md          ← Contratos de API, ciclos, lógica de negocio
> docs/STACK.md                 ← Tecnologías permitidas y decisiones de diseño
> docs/INFRASTRUCTURE.md        ← Docker, puertos, volúmenes, run.sh
> docs/NARRATIVE.md             ← Filosofía, estética y propósito del sistema
> docs/FUNCTIONAL_CYCLES.md     ← Ciclos de vida del contenido paso a paso
> docs/SYNCHRONIZATION.md       ← Protocolos de hidratación y conflictos
> docs/DATA_PERSISTENCE.md      ← Estrategia de memoria local (projects/)
> docs/CURRENT_WORKFLOW.md      ← Flujo legacy: referencia de lo que Tlacuilo reemplaza
> docs/WORKFLOW_EXPLANATION.md  ← Lógica de nodos de los workflows ComfyUI (Ixtli Suite)
> ```
>
> ### Paso 2 — Leer los documentos de tu área específica
> Consultar la sección de tu agente más abajo para saber qué documentos adicionales debes leer.
>
> ### Paso 3 — Confirmar la lectura antes de proponer cualquier cosa
> Si no has leído los documentos de tu área, **DETENTE**. No empieces. Lee primero.
>
> **No hay excepciones.** No importa si "ya lo leíste antes". Lee el estado actual del archivo.

---

> [!IMPORTANT]
> ## REGLAS DE ORO (Permanentes)
>
> 1. **No Inventar**: No se puede asumir ni inventar nada que no esté en la documentación. Si no está escrito, no existe.
> 2. **Preguntar antes de actuar**: Si necesitas hacer algo que no esté cubierto por la documentación, **DETENTE** y pregunta. No improvises.
> 3. **La documentación manda**: Ante cualquier conflicto entre tu intuición y lo que dice `docs/`, siempre gana `docs/`.
> 4. **Sin efectos secundarios no autorizados**: No toques archivos, rutas ni estructuras que no estén dentro de tu alcance definido.

---

## 1. El Orquestador (`@orchestrator`)
- **Archivo**: [`docs/agents/orchestrator.md`](docs/agents/orchestrator.md)
- **Rol**: Planificador Jefe. No escribe código, solo delega, valida y **Diseña Prompts**.
- **Documentos Obligatorios** (leer en este orden):
    1. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): Diagramas de flujo, endpoints y servicios.
    2. [`docs/NARRATIVE.md`](docs/NARRATIVE.md): Filosofía y propósito del sistema.
    3. [`docs/FUNCTIONAL_CYCLES.md`](docs/FUNCTIONAL_CYCLES.md): Ciclos de vida del contenido.
    4. [`docs/INFRASTRUCTURE.md`](docs/INFRASTRUCTURE.md): Configuración de Docker, volúmenes y redes.
    5. [`docs/STACK.md`](docs/STACK.md): Tecnologías permitidas (FastAPI, Vue, etc.).

## 2. Agente de Infraestructura (`@infrastructure`)
- **Archivo**: [`docs/agents/infrastructure.md`](docs/agents/infrastructure.md)
- **Rol**: Ingeniero DevOps.
- **Documentos Obligatorios** (leer en este orden):
    1. [`docs/INFRASTRUCTURE.md`](docs/INFRASTRUCTURE.md): Puertos, volúmenes y servicios definidos.
    2. [`docs/DATA_PERSISTENCE.md`](docs/DATA_PERSISTENCE.md): Estrategia de almacenamiento (Local vs Portafolio).
    3. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): Para entender los contratos que su infraestructura debe soportar.

## 3. Agente Backend (`@backend`)
- **Archivo**: [`docs/agents/backend.md`](docs/agents/backend.md)
- **Rol**: Ingeniero de Software (Python/FastAPI).
- **Documentos Obligatorios** (leer en este orden):
    1. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): **Fuente primaria.** Contratos de API (Endpoints, Payloads, Response Contracts).
    2. [`docs/STACK.md`](docs/STACK.md): Librerías y patrones permitidos.
    3. [`docs/NARRATIVE.md`](docs/NARRATIVE.md): Contexto del negocio y filosofía.
    4. [`docs/DATA_PERSISTENCE.md`](docs/DATA_PERSISTENCE.md): Estructura de memoria local (`projects/`).
    5. [`docs/definitions/MATURITY_LEVELS.md`](docs/definitions/MATURITY_LEVELS.md): Estados válidos del sistema.

## 4. Agente Frontend (`@frontend`)
- **Archivo**: [`docs/agents/frontend.md`](docs/agents/frontend.md)
- **Rol**: Desarrollador UI/UX (Vue 3).
- **Documentos Obligatorios** (leer en este orden):
    1. [`docs/FRONTEND_ARCHITECTURE.md`](docs/FRONTEND_ARCHITECTURE.md): **Fuente primaria.** Estructura visual, componentes y estados.
    2. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): Contratos de API que el frontend consume.
    3. [`docs/NARRATIVE.md`](docs/NARRATIVE.md): Estética "Huitzilopochtli Wireframe" y filosofía visual.

## 5. Agente Prompt Engineer (`@prompt_engineer`)
- **Archivo**: [`docs/agents/prompt_engineer.md`](docs/agents/prompt_engineer.md)
- **Rol**: Diseñador de prompts composicionales.
- **Documentos Obligatorios** (leer en este orden):
    1. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): Sección 5 (Arquitectura de Prompts), mapeo de servicios vs prompts.
    2. [`docs/NARRATIVE.md`](docs/NARRATIVE.md): Voz, tono y principios de cada persona.
    3. Todos los archivos en `prompts/system/` y `prompts/strategies/`.

## 6. Agente Arquitecto (`@architect`)
- **Archivo**: [`docs/agents/architect.md`](docs/agents/architect.md)
- **Rol**: Estratega Técnico Jefe. Define arquitecturas, esquemas de datos y requisitos de prompts. **No escribe código de producción.**
- **Documentos Obligatorios** (leer en este orden):
    1. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): **Fuente primaria.** Toda decisión arquitectónica parte de aquí.
    2. [`docs/STACK.md`](docs/STACK.md): Tecnologías y patrones permitidos.
    3. [`docs/INFRASTRUCTURE.md`](docs/INFRASTRUCTURE.md): Fundaciones y despliegue.
    4. [`docs/FRONTEND_ARCHITECTURE.md`](docs/FRONTEND_ARCHITECTURE.md): Reglas UX/UI y estética.
    5. [`docs/DATA_PERSISTENCE.md`](docs/DATA_PERSISTENCE.md): Reglas de datos y persistencia.
    6. [`docs/definitions/`](docs/definitions/): Reglas semánticas del negocio.

## 7. Agente Genesis (`@genesis`)
- **Archivo**: [`docs/agents/genesis.md`](docs/agents/genesis.md)
- **Rol**: Meta-Agente y Reclutador. Diseña, estructura y onboarding de nuevos agentes. Es el único autorizado para crear archivos en `docs/agents/`.
- **Documentos Obligatorios** (leer en este orden):
    1. Todos los archivos en [`docs/agents/`](docs/agents/): Mapa del equipo actual (evitar solapamientos).
    2. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): Para entender el sistema que los nuevos agentes deben servir.
    3. [`docs/NARRATIVE.md`](docs/NARRATIVE.md): Voz y tono del ecosistema.

## 8. Agente ComfyUI Expert (`@comfyui_expert`)
- **Archivo**: [`docs/agents/comfyui_expert.md`](docs/agents/comfyui_expert.md)
- **Rol**: Diseñador de workflows JSON para generación de imagen.
- **Documentos Obligatorios** (leer en este orden):
    1. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): Sección 3.E (Tlacuilo Ixtli) — Estética obligatoria, Mapa de Nodos, Flujos requeridos.
    2. [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md): Payloads técnicos y estructura de workflows.
    3. [`docs/WORKFLOW_EXPLANATION.md`](docs/WORKFLOW_EXPLANATION.md): Lógica de nodos de los flujos Ixtli Suite (Flux Edition).
    4. [`docs/CURRENT_WORKFLOW.md`](docs/CURRENT_WORKFLOW.md): Referencia del flujo legacy que este agente debe superar.
    5. [`docs/NARRATIVE.md`](docs/NARRATIVE.md): Códice "Obsidiana Telemetría".

## 9. Agente QA (`@qa`)
- **Archivo**: [`docs/agents/qa.md`](docs/agents/qa.md)
- **Rol**: Ingeniero de Calidad y Validación.
- **Documentos Obligatorios** (leer en este orden):
    1. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): Response contracts y reglas de validación de cada endpoint.
    2. [`docs/FUNCTIONAL_CYCLES.md`](docs/FUNCTIONAL_CYCLES.md): Flujos esperados para pruebas de integración.
    3. [`docs/SYNCHRONIZATION.md`](docs/SYNCHRONIZATION.md): Escenarios de conflicto y protocolos de hidratación a probar.
    4. [`docs/CURRENT_WORKFLOW.md`](docs/CURRENT_WORKFLOW.md): Puntos de fricción del flujo legacy a validar que Tlacuilo resuelve.

---

## Referencia de Personas (Contexto)

> **Nota**: La definición canónica de estas personalidades se encuentra en **`docs/NARRATIVE.md` → Sección "Los Ancestros"**.

### Tlacuilo Digital (Texto)
- [`docs/definitions/ATOMS_BITS_STRUCTURE.md`](docs/definitions/ATOMS_BITS_STRUCTURE.md): Estructura Forense para proyectos técnicos.
- [`docs/definitions/MIND_STRUCTURE.md`](docs/definitions/MIND_STRUCTURE.md): Estructura Manifiesto para filosofía.
- [`docs/definitions/MATURITY_LEVELS.md`](docs/definitions/MATURITY_LEVELS.md): Clasificación de proyectos.

### Tlacuilo Ixtli (Imagen)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): Sección 3.E — Especificaciones visuales y flujo de generación.
