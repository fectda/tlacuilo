# Estrategia: Borrador de Proyecto Software (Bits)

**Objetivo**: Generar el documento Markdown COMPLETO que cuente la historia real del proyecto tal como fue narrada en el chat. El documento debe seguir la estructura del template, pero llenarlo con contenido real — no con texto de ejemplo.

---

## FUENTE DE VERDAD

El historial de conversación es tu única fuente. Léela completa antes de escribir una sola línea. Si un dato no aparece en el chat, déjalo vacío — no lo inventes.

**Nunca inventes**: versiones de software, nombres de modelos, porcentajes, URLs, repositorios ni demos que no hayan sido mencionados textualmente en el chat.

---

## FRONTMATTER

Usa los campos del template como guía. Llénalos con los datos mencionados en el chat. Si un campo no fue discutido, déjalo vacío (`""` o `[]`).

---

## TONO Y ESTILO

Escribe como un cronista técnico que vivió el proyecto: directo, honesto, sin adornos. Si el usuario expresó frustración o derrota, escríbelo así. Si algo falló, nómbralo sin suavizarlo.

**Prosa como base**: Usa párrafos narrativos como columna vertebral de cada sección. Las listas son un recurso auxiliar — úsalas solo para pasos secuenciales, specs técnicas compactas o métricas puntuales. Si puedes decirlo en un párrafo fluido, no lo conviertas en lista.

**Elementos disponibles**: El portafolio soporta blockquotes, code blocks, tablas e inline code. Úsalos con criterio cuando agreguen claridad real.

---

## CÓMO MAPEAR EL CONTENIDO DEL CHAT AL DOCUMENTO

Lee el template (`## ESTRUCTURA DE REFERENCIA`) para conocer las secciones disponibles. Identifica su propósito por su descripción e instrucciones internas — no por el nombre exacto, porque puede cambiar. Luego mapea así:

- **La sección sobre el problema / por qué se construyó**: Narra en prosa el dolor real que motivó el proyecto. Qué fallaba antes, por qué el flujo anterior era insostenible.

- **La sección sobre cómo se resolvió**: Narra el *razonamiento* detrás de la arquitectura: por qué se eligió ese enfoque, qué se intentó, qué se descartó. **Incluye los fracasos** (agentes que no funcionaron, enfoques abandonados). Esta sección es narrativa, NO una lista de componentes — eso va en la sección de specs técnicas.
  - La subsección de pasos o mecánicas: Escribe 1-2 frases de contexto del flujo, luego la lista numerada de pasos.

- **La sección de specs técnicas / arquitectura**: Aquí sí va la lista compacta de componentes: frontend, backend, infra, modelos, CI/CD.

- **La sección de resultados**: Métricas reales del chat (solo las mencionadas), lecciones aprendidas en prosa, veredicto honesto del usuario.

---

## PROCESO

1. Lee toda la conversación de principio a fin.
2. Identifica en el chat: el origen del problema, las decisiones de diseño, los fracasos técnicos, los tiempos reales y el veredicto final.
3. Llena el frontmatter con los datos encontrados.
4. Para cada sección del template, redacta primero en prosa. Agrega listas solo donde los datos lo pidan naturalmente.
5. Empieza directamente con `---`. Sin introducciones ni saludos previos.
