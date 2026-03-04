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

**Guía por sección:**

- `## El Desafío` → El dolor inicial, por qué el flujo anterior era insostenible. Solo prosa.
- `## La Solución` → El razonamiento detrás de la arquitectura: por qué se tomaron esas decisiones, qué se intentó, qué se descartó y por qué. **NO es una lista de componentes** — eso va en Arquitectura. Narra el proceso de diseño, incluyendo lo que falló (ej. los agentes).
  - `### Mecánicas` → Pasos secuenciales del flujo una vez decidido. **Escribe 1-2 frases de contexto** antes de la lista numerada.
- `## Arquitectura y Especificaciones` → El único lugar para la lista técnica: frontend, backend, infra, modelos, CI/CD. No repetir lo que ya está en La Solución.
- `## Resultados` → Métricas reales del chat + lecciones aprendidas en prosa + veredicto honesto.

**Frontmatter**: Copia los campos de la ESTRUCTURA DE REFERENCIA. Llénalos con lo que el usuario mencionó en el chat. Si no fue discutido, déjalo `""`. **Nunca inventes versiones, nombres de modelos ni specs técnicas** que no aparezcan textualmente en el chat.




---

## PROCESO

1. Lee toda la conversación de principio a fin.
2. Identifica: el origen del problema, las decisiones clave, los obstáculos reales, los tiempos, los fallos con los agentes y el veredicto final.
3. Escribe el frontmatter con los datos extraídos.
4. Para cada sección, redacta primero en prosa. Agrega una lista solo si los datos lo piden naturalmente (pasos, specs técnicas).
5. Empieza directamente con `---`. Sin introducciones ni saludos.
