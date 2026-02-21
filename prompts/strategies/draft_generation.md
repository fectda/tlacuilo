# Estrategia: Generación de Borrador (Crónica de Taller y Barrio)

**Objetivo**: Generar el documento Markdown COMPLETO. Tu respuesta **DEBE** comenzar con el Frontmatter exacto que se describe abajo.

> [!CAUTION]
> **ORDEN DE EJECUCIÓN OBLIGATORIO**:
> 1. **Metadatos (YAML)**: Copia la estructura de abajo y llena los campos. Prohibido inventar campos (ej. NO pongas 'author').
> 2. **Cuerpo del texto**: Crónica técnica en español sin iconos.
> 3. **Sin comentarios**: Empieza en `---` y termina en el último punto del texto.

## 1. EL FRONTMATTER (Innegociable)
Debes incluir **TODOS** estos campos. No omitas ninguno aunque no tengas la información (déjalos vacíos `""` si es necesario):

```yaml
---
title: "[Título Narrativo y Potente]"
shortTitle: "[SLUG_EN_MAYUSCULAS]"
description: "[Un párrafo denso con el valor técnico del proyecto]"
date: YYYY-MM-DD
draft: false
icon: "[Symbol de Google, ej: memory, terminal, settings, lightbulb]"
stack: ["Tecnología 1", "Tecnología 2"]
status: [poc/wip/done]
type: "[SOFTWARE/HARDWARE/IOT/MIND]"
repository_url: ""
demo_url: ""
---
```

## 2. REGLAS DE ORO
1. **IDIOMA**: 100% Español. Traduce los encabezados de las plantillas (ej: "El desafío", "La solución", "Veredicto").
2. **CERO ICONOS**: No uses emojis ni iconos en los títulos ni en el texto.
3. **CALIDAD NUTRIDA**: Explica los "porqués". Detalla componentes (ej: ESP32, DAC, LD2410) y decisiones técnicas.
4. **INGENIERÍA FORENSE**: Documenta qué falló y cómo lo arreglaste (Iteraciones, ruidos, humedad).

## 3. ADVERTENCIA FINAL
Si tu respuesta no empieza con el bloque YAML completo de arriba, el sistema lo rechazará. No inventes campos como "author". Sigue el esquema al pie de la letra.
