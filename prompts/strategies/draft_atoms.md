# Estrategia: Borrador de Proyecto Hardware/Físico (Atoms)

**Objetivo**: Generar el documento Markdown COMPLETO que cuente la historia real del proyecto tal como fue narrada en el chat. El documento debe seguir la estructura del template, pero llenarlo con contenido real — no con texto de ejemplo.

---

## FUENTE DE VERDAD

El historial de conversación es tu única fuente. Léela completa antes de escribir una sola línea. Si un dato no aparece en el chat, déjalo vacío — no lo inventes.

**Nunca inventes**: materiales, medidas, especificaciones técnicas, costos, tiempos de fabricación ni resultados que no hayan sido mencionados textualmente en el chat.

---

## FRONTMATTER

Usa los campos del template como guía. Llénalos con los datos mencionados en el chat. Si un campo no fue discutido, déjalo vacío (`""` o `[]`).

---

## TONO Y ESTILO

Escribe como alguien que construyó el objeto con sus manos y lo describe sin adornos: honesto, técnico, directo. Si algo se rompió, se quemó o no quedó bien, dilo así. Si el resultado tiene limitaciones reales (fricciones, tolerancias, duración de batería), nómbralas.

**Prosa como base**: Usa párrafos narrativos como columna vertebral de cada sección. Las listas son recurso auxiliar — úsalas para pasos de construcción secuenciales, materiales o componentes. Si puedes describir algo en prosa fluida, hazlo.

**Elementos disponibles**: El portafolio soporta blockquotes, code blocks, tablas e inline code. Úsalos con criterio cuando agreguen claridad real.

---

## CÓMO MAPEAR EL CONTENIDO DEL CHAT AL DOCUMENTO

Lee el template (`## ESTRUCTURA DE REFERENCIA`) para conocer las secciones disponibles. Identifica su propósito por su descripción e instrucciones internas — no por el nombre exacto, porque puede cambiar. Luego mapea así:

- **La sección sobre el problema / por qué se construyó**: Narra en prosa el problema físico o de necesidad real. Qué faltaba, por qué no compraste algo ya hecho, cuál era la restricción (espacio, costo, disponibilidad, toxicidad).

- **La sección sobre cómo se resolvió / diseño**: Narra el razonamiento de diseño y fabricación en prosa: por qué se eligió ese material, esa forma, esa técnica. Qué se intentó primero y falló.
  - La subsección del proceso de construcción: Escribe 1-2 frases de contexto, luego los pasos clave (diseño → fabricación → ensamble).

- **La sección de fallos y soluciones / retos**: Narra los problemas de fabricación con honestidad. Qué no encajó, qué se quemó, qué medida estuvo mal, cómo se resolvió. Esta sección es donde está el aprendizaje real.

- **La sección de veredicto / resultado final**: Responde con honestidad: ¿funciona? ¿Es robusto y reproducible? ¿Qué limitaciones tiene hoy? Qué harías diferente en la siguiente versión.

---

## PROCESO

1. Lee toda la conversación de principio a fin.
2. Identifica en el chat: el problema físico original, las decisiones de diseño y material, los fracasos de fabricación, los tiempos y el veredicto honesto.
3. Llena el frontmatter con los datos encontrados.
4. Para cada sección del template, redacta primero en prosa. Agrega listas solo donde los datos lo pidan naturalmente (pasos de construcción, lista de materiales).
5. Empieza directamente con `---`. Sin introducciones ni saludos previos.
