/**
 * UI Texts for Tlacuilo Frontend
 * All texts must be in Spanish as per docs/FRONTEND_ARCHITECTURE.md
 */

export const UI_TEXTS = {
    APP: {
        TITLE: 'Tlacuilo',
        VERSION: 'v0.1.0'
    },
    COMMON: {
        LOADING: 'Cargando...',
        ERROR: 'Error',
        SUCCESS: 'Éxito',
        SAVE: 'GUARDAR',
        CANCEL: 'CANCELAR',
        CLOSE: 'Cerrar',
        SEARCH: 'Buscar proyectos...',
        RETRY: 'Reintentar',
        SYNC: 'Sincronizar',
        DELETE: 'Eliminar',
        OPEN_FOLDER: 'Abrir Carpeta',
        SEARCH_PLACEHOLDER: 'Buscar proyectos...',
        SHOTS: 'shots',
        IMAGE_PRESENT: 'IMG ✓'
    },
    COMMAND_CENTER: {
        HERO_TITLE: 'Centro de Mando',
        HERO_DESCRIPTION: 'Bienvenido a Tlacuilo. Arquitecta tus colecciones creativas y orquestra flujos agenticos avanzados con precisión clínica.',
        TELEMETRY: 'Telemetría',
        NO_ACTIVITY: 'Aún no hay actividad registrada por el neuro-scanner.',
        SYSTEM_VITALS: 'Signos Vitales del Sistema'
    },
    PROJECT_GRID: {
        SEARCH_SCANNING: 'Escaneando configuración...',
        NEURAL_FAILURE: 'Fallo en el Enlace Neural',
        RETRY_SYNC: 'Reintentar Sincronización',
        ENTITIES: 'ENTIDADES',
        NO_CATALOGED: 'No hay {type} catalogados',
        STATUS: {
            DRAFT: 'BORRADOR',
            PUBLISHED: 'PUBLICADO'
        },
        SECTIONS: {
            atoms: 'Átomos Físicos (Hardware)',
            bits: 'Bits Digitales (Software)',
            mind: 'Mente (Manifiestos)'
        }
    },
    NEW_PROJECT: {
        TITLE: 'Nuevo Proyecto',
        LABEL_NAME: 'Nombre del Proyecto',
        LABEL_SLUG: 'Slug (ID)',
        LABEL_COLLECTION: 'Colección',
        PLACEHOLDER_NAME: 'ej. Motor Cuántico',
        PLACEHOLDER_SLUG: 'motor-cuantico',
        BTN_INITIALIZE: 'Inicializar Proyecto',
        BTN_FORGING: 'Forjando...',
        ERROR_FAILED: 'Error al crear el proyecto',
        COLLECTIONS: {
            atoms: 'Átomos (Hardware)',
            bits: 'Bits (Software)',
            mind: 'Mente (Manifiestos)'
        }
    },
    FILTERS: {
        COLLECTIONS: 'Colecciones:',
        DOC_STATUS: 'Estado Doc:',
        RESET: 'Reiniciar Filtros',
        STATUSES: {
            borrador: 'Borrador',
            revisión: 'Revisión',
            traducción: 'Traducción',
            publicado: 'Publicado'
        }
    },
    SYSTEM_STATUS: {
        ONLINE: 'EN LÍNEA',
        STANDBY: 'EN ESPERA',
        OFFLINE: 'FUERA DE LÍNEA',
        POLLING: 'SONDEANDO'
    },
    PROJECT_COMMON: {
        BACK: 'VOLVER',
        PUBLISH: 'PUBLICAR',
        PROMOTE: 'PROMOVER',
        DISCARD: 'DESCARTAR',
        PUBLISH_TOOLTIP: 'Publicar al repositorio remoto',
        CONFIRM_PUBLISH: '¿Ejecutar PUBLICACIÓN GLOBAL? (Git Ops: Commit & Push al repositorio remoto)',
        CONFIRM_REVERT: '¿Estás seguro de descartar todos los cambios locales y volver a la versión del Portafolio?',
        CONFIRM_PROMOTE: '¿Deseas promover esta copia de trabajo al Portafolio?'
    },
    PROJECT_DIGITAL: {
        MODE_EDIT: 'EDICIÓN',
        MODE_TRANSLATE: 'TRADUCCIÓN',
        STUDIO_LINK: '⌀ IXTLI'
    },
    PROJECT_STUDIO: {
        TITLE: 'IXTLI STUDIO',
        NEW_SHOT: '+ NUEVO SHOT',
        SUGGEST_AI: '✦ SUGERIR CON IA',
        ANALYZING: 'ANALIZANDO...',
        SHOT_LIST: 'Lista de Shots',
        ANALYZING_DOC: 'Tlacuilo Ixtli analizando documento...',
        NO_SHOTS: 'Sin shots aún',
        NO_SHOTS_DESC: 'Usa "Sugerir con IA" para auto-generar una lista de shots desde el documento, o crea uno manualmente.',
        CONFIRM_DELETE_SHOT: '¿Eliminar este shot permanentemente?'
    },
    CREATE_SHOT_MODAL: {
        TITLE: 'Nuevo Slot de Shot',
        LABEL_TITLE: 'Título',
        LABEL_PROTAGONIST: 'Protagonista',
        LABEL_DESCRIPTION: 'Descripción',
        LABEL_TYPE: 'Tipo',
        LABEL_ATMOSPHERE: 'Atmósfera',
        PLACEHOLDER_TITLE: 'ej. Primer plano del chip DAC PCM5102A',
        PLACEHOLDER_PROTAGONIST: 'Único componente que domina el encuadre...',
        PROTAGONIST_HELP: 'El único sujeto físico en cuadro (ej. "press-fit entre PCB y carcasa")',
        PLACEHOLDER_DESCRIPTION: 'Descripción técnica del encuadre...',
        BTN_CREATE: 'Crear Shot'
    },
    SHOT_DETAIL: {
        EMPTY_STATE: 'Selecciona un shot',
        BTN_DELETE: '✕ ELIM',
        SECTION_METADATA: 'Metadatos',
        BTN_EDIT: 'Editar',
        BTN_SAVE: 'Guardar',
        SECTION_REFERENCE: 'Referencia',
        BTN_UPLOAD_REF: 'Subir Referencia',
        BTN_REPLACE_REF: 'Reemplazar Referencia',
        UPLOAD_HELP: 'Suelta o Haz Clic para Subir',
        REFERENCE_DESC: 'La imagen de referencia proporciona el contexto inicial para la generación de Ixtli.',
        SECTION_GALLERY: 'Galería',
        NO_VARIANTS: 'Sin variantes aún.',
        APPROVED_VARIANT: 'Variante Aprobada',
        BTN_APPROVE: 'Aprobar',
        BTN_REFINE: 'Refinar Variante',
        PLACEHOLDER_REFINE: 'Describe el refinamiento...',
        BTN_REFINE_SUBMIT: 'Refinar',
        RESUME_POLLING: 'Reanudar Sondeo',
        LABEL_REFINEMENT: 'Instrucciones de Refinamiento',
        BTN_REGENERATE: '✦ REGENERAR VARIANTE',
        LABEL_VISUAL_PROMPT: 'Prompt Visual',
        LABEL_REF_PHOTO: 'Foto de Referencia',
        LABEL_GEN_VARIANTS: 'Variantes Generadas',
        LABEL_PROCESSING: 'Procesando',
        BTN_CLOSE: '✕ CERRAR',
        RE_UPLOAD_RESTART: '↺ RE-SUBIR Y REINICIAR',
        UPLOAD_GENERATE: '↑ SUBIR Y GENERAR',
        ERROR_COMPLETE_META: '⚠ Completa Focus y Atmosphere antes de subir.',
        STATUS: {
            pending_upload: 'Pendiente de Subida',
            queued: 'En cola en ComfyUI...',
            generated: 'Generado — esperando aprobación',
            approved: 'Aprobado ✓'
        },
        CONFIRM_DELETE_VARIANT: '¿Eliminar esta variante permanentemente?'
    },
    REFINEMENT_MODAL: {
        TITLE: 'INSTRUCCIONES DE REFINAMIENTO',
        HELP_TEXT: 'Especifique detalles técnicos o de tono para que el Bilingual Scribe ajuste la versión en inglés.',
        SUBMIT_HINT: 'Cmd/Ctrl + Enter para enviar',
        BTN_REFINE: 'REFINAR'
    },
    DRAFT_PREVIEW: {
        GENERATING_DRAFT: 'GENERANDO BORRADOR',
        GEM_PROTOCOL: 'Ejecutando Protocolo GEM // Sesión Activa',
        GENERATION_FAILURE: 'FALLO_GENERACIÓN',
        LOCALIZATION_FAILURE: 'FALLO_LOCALIZACIÓN',
        VALIDATION_ERROR: 'ERROR_VALIDACIÓN',
        BTN_RETRY: 'REINTENTAR',
        BTN_UNDERSTOOD: 'ENTENDIDO',
        BTN_CLOSE: 'CERRAR',
        BTN_GENERATE: '[ GENERAR BORRADOR ]',
        BTN_PREVIEW: '[ PREVISUALIZAR ]',
        BTN_EDIT: '[ EDITAR ]',
        BTN_DISCARD: '[ DESCARTAR ]',
        BTN_SAVING: 'GUARDANDO...',
        BTN_SAVE: 'GUARDAR',
        SCHEMA_OK: '[ SCHEMA_OK ]',
        SCHEMA_ERROR: '[ SCHEMA_ERROR ]',
        NO_DATA: 'NO HAY DATOS DISPONIBLES',
        NO_DATA_DESC: 'Genera un borrador o entra en modo edición',
        MODE_INSERT: 'MODO: INSERTAR',
        MODE_VIEW: 'MODO: VISTA',
        CHARS: 'Caracteres',
        MARKDOWN: 'Markdown'
    }
}
