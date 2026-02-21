# Estrategia: Generación de Borrador (Crónica de Taller y Barrio)

**Objetivo**: Generar el documento Markdown COMPLETO. Tu respuesta **DEBE** comenzar exactamente con el bloque de Frontmatter (YAML). No escribas introducciones, ni saludos, ni comentarios.

> [!CAUTION]
> **ORDEN DE PRIORIDAD INMUTABLE**:
> 1. **VERDAD TÉCNICA (CHAT)**: Usa solo lo que Eduardo te dijo. (Ej: Eduardo usa ESP32 y sensor LD2410. Ignora cualquier referencia a Arduino o LD440).
> 2. **ESTAS REGLAS**: El Frontmatter es obligatorio y completo.
> 3. **FORMATO**: Empieza en `---` y termina en el último punto del texto.

## 1. EL FRONTMATTER (Debe ser lo primero en tu respuesta)
Copia este bloque y llena los datos reales:

```yaml
---
title: "[Título Narrativo]"
shortTitle: "[SLUG_MAYUSCULAS_SIN_ESPACIOS]"
description: "[Un párrafo técnico denso]"
date: YYYY-MM-DD
draft: false
icon: "[Symbol de Google]"
stack: ["Tecnología 1", "Tecnología 2"]
status: [poc/wip/done]
type: "[SOFTWARE/HARDWARE/IOT/MIND]"
repository_url: ""
demo_url: ""
---
```

## 2. ESTRUCTURA NARRATIVA (En Español)
Traduce los encabezados pero mantén la esencia de ingeniería:
- `## El Desafío`: El problema técnico.
- `## La Solución`: Arquitectura y materiales reales.
- `## Proceso de Armado`: Pasos de fabricación.
- `## Retos y Aprendizajes`: Qué falló y cómo se arregló.
- `## Veredicto`: Conclusión técnica.

## 3. ADVERTENCIA FINAL
Si tu respuesta no empieza con `---` seguido del YAML anterior, el sistema la borrará. **CERO ALUCINACIONES**: No inventes ferias ni sensores que no estén en la plática.
