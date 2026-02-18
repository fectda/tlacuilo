# Flujo de Trabajo Actual (Legacy)

Este documento describe el **proceso manual actual** para la creación de contenido y gestión de imágenes en el portafolio. Este flujo presenta fricciones significativas que el proyecto Tlacuilo busca resolver.

## 1. Creación de Contenido (Texto)

### Proceso Manual
El usuario interactúa con un GEM (Gemini) en una interfaz externa (navegador web), copiando y pegando prompts manualmente.

1.  **Inicialización**:
    -   El usuario inicia una conversación con el GEM.
    -   El GEM responde: *"Sistema v7.0... ¿Atoms, Bits o Mind?"*.

2.  **Definición de Contexto**:
    -   El usuario indica el tipo de proyecto (`atoms`, `bits`, etc.).
    -   Si es un proyecto existente, el usuario abre el archivo `.md` local, copia todo el contenido y lo pega en el chat para darle contexto al GEM.

3.  **Entrevista y Redacción**:
    -   Se inicia un ciclo de preguntas y respuestas (Iteración Socrática).
    -   El usuario responde dudas sobre el proyecto.
    -   El LLM propone secciones de texto.

4.  **Generación y Migración**:
    -   El usuario solicita: *"Genera el MD final en Español"*.
    -   El LLM genera el bloque de código Markdown.
    -   El usuario copia el bloque -> Cambia de ventana al editor de código -> Pega en el archivo `src/content/.../archivo.md`.

5.  **Refinamiento y Traducción**:
    -   El usuario hace correcciones manuales finales en el archivo en Español.
    -   El usuario copia nuevamente todo el texto final -> Vuelve al chat -> Pide: *"Traduce esto al Inglés"*.
    -   Copia el resultado -> Crea/Abre el archivo en `en/` -> Pega el contenido.

## 2. Generación de Imágenes

### Proceso Desconectado
El usuario utiliza una herramienta separada ("Nano Banana") via otra instancia de chat para procesar las fotos.

1.  **Captura y Transferencia**:
    -   El usuario toma fotos del hardware real.
    -   Las sube al chat de la IA generadora de imágenes.

2.  **Prompting Manual**:
    -   El usuario copia las guías de estilo (`DESIGN_BLUEPRINT.md`) y el prompt de "Tlacuilo Ixtli".
    -   Lo pega en el chat de imagen.
    -   Sube la foto de referencia.

3.  **Gestión de Archivos**:
    -   La IA genera la imagen procesada.
    -   **Problema**: A menudo incluye marcas de agua o alteraciones no deseadas.
    -   El usuario descarga la imagen a su disco duro local (carpeta `Downloads`).
    -   Manualmente mueve el archivo a la carpeta del proyecto en `public/atoms/{proyecto}/`.
    -   Renombra el archivo manualmente para que coincida con la convención.

## Puntos de Fricción Identificados
-   **Cambio de Contexto**: Saltos constantes entre Editor de Código, Navegador (Chat Texto), Navegador (Chat Imagen) y Explorador de Archivos.
-   **Pérdida de Contexto**: El Chat de Imagen no sabe nada del contexto del Chat de Texto.
-   **Trabajo Manual**: Copiar/Pegar prompts, mover archivos, renombrar.
-   **Desconexión**: La publicación (Git Push) es un paso extra manual en la terminal, desconectado de la finalización del contenido.
