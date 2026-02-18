# Escenarios de Sincronización y Alineación

Tlacuilo debe manejar la discrepancia entre la "Verdad Externa" (Portafolio) y la "Memoria Interna" (`data/`). Aquí se definen los protocolos para los tres escenarios principales.

## Escenario A: Proyecto Existente, Tlacuilo Nuevo
**Caso**: Existe `atoms/teclado/index.md` en el portafolio, pero NO existe `data/atoms/teclado/`.
**Cuándo ocurre**: Al iniciar Tlacuilo por primera vez o al añadir archivos manualmente.

**Protocolo (Hidratación)**:
1.  **Detección**: El scanner de proyectos encuentra la carpeta en el portafolio.
2.  **Acción**:
    -   Tlacuilo crea silenciosamente la carpeta `data/atoms/teclado/`.
    -   Inicializa `chat_history.json` vacío.
    -   Lee el `.md` actual e inyecta un "System Message" invisible en el historial: *"Contexto inicial cargado desde archivo existente: [Resumen/Contenido]"*.
3.  **Resultado**: El GEM "sabe" lo que hay en el archivo, aunque no haya chateado antes.

## Escenario B: Memoria Huérfana
**Caso**: Existe `data/atoms/fantasma/` con historial de chat, pero NO existe `atoms/fantasma/index.md` en el portafolio.
**Cuándo ocurre**: El usuario borró manualmente la carpeta del proyecto en el sistema de archivos.

**Protocolo (Limpieza/Rescate)**:
1.  **Detección**: Al listar proyectos, Tlacuilo ve datos en `data/` sin par en el portafolio.
2.  **Acción (UI)**: Muestra el proyecto marcado como "⚠️ Missing Files".
3.  **Opciones al Usuario**:
    -   *Opción 1 (Olvido)*: Borrar la memoria interna (Eliminar `data/atoms/fantasma/`).
    -   *Opción 2 (Resurrección)*: Regenerar el archivo `.md` base a partir del último estado conocido en la memoria.

## Escenario C: Sincronización Normal
**Caso**: Existen tanto el archivo `.md` como la memoria en `data/`.
**Cuándo ocurre**: Operación diaria normal.

**Protocolo (Alineación)**:
1.  **Carga**: Se leen ambos.
2.  **Verificación**: Tlacuilo confía ciegamente en el `.md` como la verdad actual del contenido. La memoria (`data/`) solo aporta el contexto conversacional.
3.  **Conflicto**: Si el usuario editó el `.md` manualmente fuera de Tlacuilo, el GEM recibe el nuevo contenido como contexto actualizado en la siguiente interacción. *"Veo que editaste el archivo manualmente..."*.

## Regla de Oro
**El Portafolio manda.** Tlacuilo nunca sobreescribe el Portafolio automáticamente al arrancar. Solo escribe cuando el usuario explícitamente ejecuta una acción de "Guardar" o "Generar".
