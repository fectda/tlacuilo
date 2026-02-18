# Narrativa y Flujo de Trabajo: "Ingeniería de Piedra y Luz"

Este documento define la filosofía central y el flujo de trabajo deseado para el proyecto Tlacuilo, una herramienta para gestionar el portafolio personal "Altepetl Digital".

## Filosofía
No estamos creando un simple CMS. Estamos construyendo una herramienta para un **"Científico de Barrio"**.
-   **Eficiencia Radical**: Si el flujo actual es manual y tedioso, es un fallo de diseño.
-   **Ingeniería de Piedra y Luz**: La combinación de lo material (Hardware/Atoms) y lo digital/etéreo (Software/Bits/Mind).
-   **No Magic**: La automatización sirve al humano, no al revés.

## El Objetivo Central: Ciclo de Vida de la Documentación
Tlacuilo existe para **gestionar y automatizar el flujo de la documentación**, no solo para mostrar estatus de proyectos.

El sistema debe orquestar este ciclo vital:
1.  **Borrador (Draft)**: Creación inicial con asistencia de Tlacuilo Digital.
2.  **Revisión (Review)**: Edición humana y refinamiento.
3.  **Traducción (Translation)**: Automatización de la versión en inglés.
4.  **Publicación (Published)**: Despliegue al repositorio.
5.  **Iteración**: Capacidad de retomar un proyecto `Published` y volver a editarlo (Ciclo continuo).

## Distinción Crítica: Proyecto vs. Documentación
-   **Estatus del Proyecto** (`idea`, `poc`, `wip`, `done`): Es un metadato del objeto real. Tlacuilo solo lo *muestra*.
-   **Estatus de Documentación** (El verdadero trabajo de Tlacuilo): Es el estado del archivo `.md` y sus assets.

## El Flujo Deseado (Tlacuilo)

Queremos una herramienta unificada que simplifique este proceso, integrando la gestión de archivos, la asistencia de redacción y la generación de imágenes en una sola interfaz local.

### 1. Gestión de Proyectos (La Base)
-   Lista los proyectos existentes.
-   Permite iniciar nuevos flujos de documentación.

### 2. Flujo de Contenido (Tlacuilo Digital)
**El Conversador y Guardián del Contexto**:
1.  **Interfaz de Chat**: Tlacuilo provee la interfaz para hablar con los GEMs (Tlacuilo Digital).
2.  **Persistencia de Memoria**: Tlacuilo **GUARDA** el historial del chat en el contexto del proyecto.
    -   *Valor*: Si retomo un proyecto 6 meses después, el GEM tiene todo el contexto de las decisiones anteriores.
3.  **Ciclo de Automatización**:
    -   El usuario habla -> Tlacuilo Digital genera borrador -> Usuario revisa -> Tlacuilo automatiza traducción y commit.

### 3. Flujo de Imágenes (Tlacuilo Ixtli)
**Integración Profunda con ComfyUI**:
1.  **Input**: Foto real del hardware ("Dirty").
2.  **Proceso**: Tlacuilo Ixtli procesa la imagen para limpiarla y estilizarla ("Obsidiana Telemetría").
3.  **Resultado**: Imagen lista para `public/`.

## Objetivo Final
Eliminar la fricción entre la **Ejecución Técnica** (hacer el proyecto) y la **Documentación** (contar la historia). Tlacuilo es el escriba que permite al ingeniero centrarse en construir.
