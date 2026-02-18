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
        SAVE: 'Guardar',
        CANCEL: 'Cancelar',
        CLOSE: 'Cerrar',
        SEARCH: 'Buscar proyectos...',
        RETRY: 'Reintentar',
        SYNC: 'Sincronizar',
        DELETE: 'Eliminar',
        OPEN_FOLDER: 'Abrir Carpeta',
        SEARCH_PLACEHOLDER: 'Buscar proyectos...'
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
    }
}
