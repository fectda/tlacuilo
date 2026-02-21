# Auditoría de Servicios vs Arquitectura

Este documento rastrea la conformidad estricta de los servicios implementados contra `docs/ARCHITECTURE.md`.

## A. Servicio de Proyectos (`/projects`)

### `GET /api/projects` (Discovery Cycle)
- [ ] **Responsabilidad**: Escanear Portafolio y Memoria Local.
- [ ] **Validación**: Verifica `PORTAFOLIO_PATH` y `projects/`.
- [ ] **Logic**: Cruce de listas + Hidratación automática.
- [ ] **Output**: JSON con `atoms`, `bits`, `mind`. Campos: `id`, `name`, `doc_status`, `missing_files`.

### `POST /api/projects` (Create)
- [ ] **Payload**: `{ name, collection, slug }`.
- [ ] **Validación**: Slug unique (local y portafolio).
- [ ] **Logic**: Crea scaffolding local.
- [ ] **Output**: `{ id, status: "created" }`.

### `POST /api/{col}/{slug}/forget`
- [ ] **Logic**: Borrado recursivo local. NO toca portafolio.

### `POST /api/{col}/{slug}/resurrect`
- [ ] **Logic**: Restaura de local a portafolio. Valida no sobreescritura.

## A. Sincronización de Contexto

### `GET /api/{col}/{slug}/content`
- [ ] **Logic**: Precedencia (Working Copy > Portafolio).

### `GET /api/{col}/{slug}/chat/history`
- [ ] **Logic**: Retorna historial.

### `POST /api/{col}/{slug}/revert`
- [ ] **Logic**: Descarta local, restaura desde Portafolio.

## B. Ciclo de Entrevista

### `POST /api/{col}/{slug}/init`
- [ ] **Logic**:
    - Escenario 1 (Lienzo en Blanco): Si historial vacío -> Trigger AI.
    - Escenario 2 (Deuda): Si último msg User -> Trigger AI.
    - Escenario 3 (Wait): Si último msg AI -> No op.

### `POST /api/{col}/{slug}/message`
- [ ] **Input**: `{ content, system_only, response_system_only }`.
- [ ] **Logic**: 
    - Sanitización de input.
    - Llamada a LLM.
    - **NO** activa `is_working_copy_active`. (Corregido recientemente).

### `POST /api/{col}/{slug}/draft`
- [ ] **Logic**: Genera borrador sin guardar.
