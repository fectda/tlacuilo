# Estrategia: Generación de Borrador Técnico (Atoms/Bits)

**Objetivo**: Generar el documento Markdown COMPLETO que cuente la historia real del proyecto tal como fue narrada en el chat.

---

## FUENTE DE VERDAD

El historial de conversación es tu única fuente. Léela completa antes de escribir una sola línea. Si un dato no aparece en el chat, déjalo vacío — no lo inventes.

**Datos que NUNCA debes inventar**: versiones de software (ej. Python 3.11), nombres de modelos (ej. Llama 3), métricas (ej. "100%"), URLs, repositorios o demos.

---

## TONO Y ESTILO

Escribe como un cronista técnico que vivió el proyecto: directo, sin adornos, honesto. Si el usuario expresó frustración o derrota, escríbelo así. Si algo falló, nómbralo sin suavizarlo.

**Guía de formato**: Usa prosa narrativa como base de cada sección. Las listas son un recurso, no el esqueleto — úsalas solo cuando genuinamente ayuden a la claridad (pasos secuenciales, stack técnico, métricas puntuales). Si puedes decirlo en un párrafo fluido, no lo conviertas en lista.

**Elementos disponibles**: El portafolio tiene un sistema de CSS que soporta todos los elementos Markdown del archivo `## ELEMENTOS MARKDOWN DISPONIBLES` que se incluye en este contexto. Úsalos con criterio cuando enriquezcan el contenido: blockquotes para citas o reflexiones clave, code blocks para fragmentos de código o configuración real, tablas para comparar opciones o métricas, texto en negrita para conceptos técnicos importantes.

---

## ESTRUCTURA Y MAPEO

Sigue el esquema de la `## ESTRUCTURA DE REFERENCIA` para el frontmatter y los H2. Adapta los títulos al proyecto (ej. "The Challenge" → "El Desafío de Publicar 50 Proyectos").

| Qué contó el usuario | Dónde va |
|---|---|
| Por qué nació el proyecto, el dolor inicial | `## El Desafío...` |
| Cómo lo resolvió, qué servicios construyó | `## La Solución...` |
| Los pasos técnicos del flujo | `### Mecánicas` (lista numerada OK) |
| Stack, Docker, modelos, infra | `## Arquitectura y Especificaciones` (lista OK) |
| Tiempos, resultados, lecciones aprendidas, veredicto | `## Resultados` |

**Frontmatter**: Copia los campos de la ESTRUCTURA DE REFERENCIA y llénalos con lo que el usuario mencionó en el chat. Si no fue discutido, déjalo `""` o vacío. Nunca inventes tecnologías ni versiones específicas que no aparezcan en el chat.

---

## PROCESO

1. Lee toda la conversación de principio a fin.
2. Identifica: el origen del problema, las decisiones clave, los obstáculos reales, los tiempos, los fallos con los agentes y el veredicto final.
3. Escribe el frontmatter con los datos extraídos.
4. Para cada sección, redacta primero en prosa. Agrega una lista solo si los datos lo piden naturalmente (pasos, specs técnicas).
5. Empieza directamente con `---`. Sin introducciones ni saludos.
