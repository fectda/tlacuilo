# Estrategia: Borrador de Proyecto Software (Bits)

**Objetivo**: Generar el documento Markdown COMPLETO que cuente la historia real del proyecto tal como fue narrada en el chat. El documento debe seguir la estructura del template, pero llenarlo con contenido real — no con texto de ejemplo.

---

## FUENTE DE VERDAD

El historial de conversación es tu única fuente. Léela completa antes de escribir una sola línea. Si un dato no aparece en el chat, déjalo vacío — no lo inventes.

**Nunca inventes**: versiones de software, nombres de modelos, porcentajes, URLs, repositorios ni demos que no hayan sido mencionados textualmente en el chat.

---

## IDIOMA

Todo el documento se escribe en **español**. Los títulos del template están en inglés como referencia estructural, pero los H2 y H3 del documento final deben estar en español. Traduce y adapta los títulos al proyecto (ej. "The Challenge" → "El Desafío de Publicar 50 Proyectos", "Architecture & Specs" → "Arquitectura y Especificaciones").

---

## FRONTMATTER

Usa los campos del template como guía. Llénalos con los datos mencionados en el chat. Si un campo no fue discutido, déjalo vacío (`""` o `[]`).

---

## TONO Y ESTILO

La voz de este documento es la del usuario en el chat: directa, honesta, sin pulir. Si dijo "pasé días enteros haciendo que corrigieran", escríbelo así — no lo suavices a "el proceso de desarrollo requirió iteraciones adicionales". Si algo falló, nómbralo. Si algo fue frustrante, dilo.

**Prosa como base**: Usa párrafos narrativos como columna vertebral. Las listas son recurso auxiliar — úsalas solo para pasos secuenciales, specs técnicas compactas o métricas puntuales. Si puedes decirlo en un párrafo fluido, no lo conviertas en lista.

**Elementos disponibles**: El portafolio soporta blockquotes, code blocks, tablas e inline code. Úsalos con criterio cuando agreguen claridad real.

---

## CÓMO MAPEAR EL CONTENIDO DEL CHAT AL DOCUMENTO

Lee las secciones del template (`## ESTRUCTURA DE REFERENCIA`) e identifica su propósito por su descripción — no por el nombre exacto, porque puede cambiar.

### La sección del PROBLEMA (primer H2 del template):
Narra en prosa el dolor real. Qué fallaba, por qué el proceso anterior era insostenible, qué escala lo hacía imposible.

### La sección de la SOLUCIÓN (segundo H2 del template):
**Esta sección NO describe el stack técnico** — para eso existe la sección de specs. Esta sección narra el *viaje de decisiones*: qué se intentó, qué falló, qué se aprendió en el camino.

Preguntas que debe responder esta sección:
- ¿Qué enfoque se intentó primero y por qué no funcionó?
- ¿Qué obstáculos concretos aparecieron?
- ¿Cómo se llegó a la solución final? ¿Fue un cambio de estrategia, un descubrimiento, o resignación pragmática?

Si hubo agentes, habla del intento y del fracaso con nombres concretos. Si hubo semanas de trabajo frustrante, cuéntalo. Si la solución "funciona pero no es perfecta", dilo exactamente así.

La subsección de pasos (si existe en el template): escribe 1-2 frases de contexto del flujo real, luego los pasos numerados.

### La sección de ARQUITECTURA / SPECS TÉCNICAS (tercer H2):
**Único lugar donde va la lista del stack**: frontend, backend, infra, modelos, CI/CD. Conciso y directo.

### La sección de RESULTADOS (último H2):
Solo métricas que aparecen en el chat. Lecciones aprendidas en prosa, con el tono honesto del usuario. Veredicto real: ¿funcionó? ¿Qué limitaciones tiene hoy?

---

## PROCESO

1. Lee toda la conversación de principio a fin.
2. Extrae: el origen del problema, las decisiones de diseño, los fracasos concretos, los tiempos reales, el veredicto.
3. Llena el frontmatter con esos datos.
4. Escribe cada sección en prosa primero. Agrega listas solo donde los datos lo pidan naturalmente.
5. Empieza directamente con `---`. Sin introducciones ni saludos.
