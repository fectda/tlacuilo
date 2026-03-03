# Tlacuilo: El Arquitecto del Portafolio

> "Ingeniería de Piedra y Luz"

**Tlacuilo** es una herramienta local de gestión de contenido, orquestación de IA y producción visual diseñada para operar el portafolio personal **Altepetl Digital**. Actúa como intermediario entre el sistema de archivos local (donde vive la verdad), los modelos de lenguaje (donde vive la asistencia) y la generación de imágenes (donde vive la estética).

---

## Módulos Principales

### 1. Command Center (Gestión)
Panel central de control. Escanea el portafolio y la memoria local mediante el **Discovery Cycle**: detecta proyectos nuevos, sincroniza estados, identifica memorias huérfanas y permite actuar sobre ellas (`forget` / `resurrect`).

### 2. El Arquitecto — Tlacuilo Digital (Edición)
Entorno de escritura asistida por agente de IA. Implementa el **Ciclo de Entrevista** completo:
- **Arranque de sesión** (`/init`): Construye el contexto inicial y dispara el primer mensaje.
- **Mensajería transaccional** (`/message`): Chat persistente con historial filtrado.
- **Generación de borrador** (`/draft`): Propone un documento Markdown consolidado para revisión.
- **Persistencia** (`/persist`): Guarda el borrador aprobado en la copia de trabajo.
- **Promoción** (`/promote`): Mueve el archivo al Portafolio y cierra la sesión española.
- **Reversión** (`/revert`): Descarta cambios y restaura la última versión oficial.
- **Modo Ingeniero**: Para documentación técnica (`atoms` / `bits`).
- **Modo Filósofo**: Para ensayos reflexivos (`mind`).

### 3. Localización — The Bilingual Scribe (Inglés)
Flujo de traducción al inglés integrado en El Arquitecto:
- **Lectura** (`GET /translate`): Obtiene la versión en inglés con reglas de precedencia espejo.
- **Generación** (`POST /translate/draft`): Traduce desde cero o refina un borrador existente con ciclo de auto-corrección estructural.
- **Persistencia** (`POST /translate/persist`): Guarda el borrador en inglés validado.

### 4. Tlacuilo Studio — Ixtli (Visualización)
Interfaz de generación y curaduría de imagen bajo la estética **"Obsidiana Telemetría"**:
- **Gestión de Shot List** (CRUD de tomas): crear, listar, editar, eliminar.
- **Sugerencia de tomas con IA** (`/suggest`): El agente analiza el `.md` y propone shots.
- **Pipeline de generación** (`/upload` → `/status` → `/image`): Sube foto de referencia, Vision LLM genera el `visual_prompt`, ComfyUI produce 4 variantes.
- **Ciclo de corrección** (`/correct`): Itera sobre una imagen base con instrucción del usuario.
- **Aprobación** (`/approve`): Marca una variante como definitiva.

### 5. Deploy Console (Publicación)
Cierra el ciclo completo: valida que existan las versiones ES y EN, actualiza el `doc_status` a `publicado` y ejecuta `git add / commit / push` automáticamente sobre el portafolio.

---

## Stack Tecnológico

| Capa | Tecnología |
|---|---|
| **Frontend** | Vue 3 + Vite + TailwindCSS |
| **Backend** | Python 3.11 + FastAPI + Pydantic |
| **Infraestructura** | Docker + Docker Compose |
| **LLM (Texto)** | Ollama (local) |
| **Imágenes** | ComfyUI |
| **Git** | GitPython (automatizado) |

---

## Infraestructura

El sistema corre completamente en Docker. El único punto de entrada autorizado es:

```bash
./run.sh
```

Este script carga el `.env`, valida la ruta del portafolio y levanta los contenedores en modo detached.

| Servicio | Puerto | Descripción |
|---|---|---|
| `backend` | `8000` | API FastAPI |
| `frontend` | `5173` | App Vue 3 (HMR en dev) |

> **Regla de Oro**: NUNCA ejecutar `docker compose up` directamente. Siempre usar `./run.sh`.

---

## Estructura de Directorios

```
tlacuilo/
├── backend/         # API FastAPI (Python)
│   └── app/
│       ├── api/     # Endpoints por módulo
│       ├── services/# Lógica de negocio
│       └── clients/ # ComfyUI, Ollama
├── frontend/        # App Vue 3
│   └── src/
│       ├── views/   # CommandCenter, ProjectDigital, ProjectStudio
│       ├── components/
│       └── stores/
├── prompts/         # Prompts as Code
│   ├── system/      # Personas (Digital, Global, Ixtli)
│   └── strategies/  # Estrategias por ciclo
├── projects/        # Memoria local (chats, estados, shots)
├── docs/            # Fuente de Verdad Documental
└── run.sh           # Punto de entrada del sistema
```

---

## Documentación

El sistema se rige por la documentación en `docs/`. **Esta es la fuente de verdad.**

| Documento | Contenido |
|---|---|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Ciclos, API Specs y contratos de respuesta |
| [FRONTEND_ARCHITECTURE.md](docs/FRONTEND_ARCHITECTURE.md) | Pantallas, UI Flows y flujos de navegación |
| [STACK.md](docs/STACK.md) | Tecnologías y decisiones de diseño |
| [INFRASTRUCTURE.md](docs/INFRASTRUCTURE.md) | Docker, servicios y puertos |
| [NARRATIVE.md](docs/NARRATIVE.md) | Filosofía y Ciclo de Vida Documental |
| [FUNCTIONAL_CYCLES.md](docs/FUNCTIONAL_CYCLES.md) | Guía paso a paso de los ciclos |
| [SYNCHRONIZATION.md](docs/SYNCHRONIZATION.md) | Protocolos de hidratación y manejo de conflictos |
| [DATA_PERSISTENCE.md](docs/DATA_PERSISTENCE.md) | Estrategia de memoria y guardado |
| [WORKFLOWS.md](docs/WORKFLOWS.md) | Payloads técnicos de ComfyUI |

### Definiciones de Negocio
| Documento | Contenido |
|---|---|
| [MATURITY_LEVELS.md](docs/definitions/MATURITY_LEVELS.md) | Estados de madurez del proyecto (`idea → done`) |
| [ATOMS_BITS_STRUCTURE.md](docs/definitions/ATOMS_BITS_STRUCTURE.md) | Plantilla STAR para proyectos técnicos |
| [MIND_STRUCTURE.md](docs/definitions/MIND_STRUCTURE.md) | Plantilla para ensayos (Manifiesto) |

### Personas y Prompts
| Archivo | Rol |
|---|---|
| `prompts/system/tlacuilo_digital.md` | El Escriba Fiel (Español) |
| `prompts/system/tlacuilo_global.md` | The Bilingual Scribe (Inglés) |
| `prompts/system/tlacuilo_ixtli.md` | Director Visual (Imágenes) |

---

## Estética y Filosofía

El sistema sigue la línea de diseño **"Huitzilopochtli Wireframe"**:
- **Interfaz**: Oscura (`#050505`), Monospaciada, Alto Contraste.
- **Colores**: Rojo Hematita (Acción), Turquesa (Datos), Hueso (Texto).
- **Imágenes**: Estética "Obsidiana Telemetría" — fondo negro, chiaroscuro dramático, sin adornos.
- **Principios**: Eficiencia Radical, Sin Adornos Innecesarios ("No Magic").
