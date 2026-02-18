# Definición de Estatus de Proyecto

La idea es clasificar la madurez del proyecto para que no se juzguen todos con la misma vara. Estos estatus definen en qué etapa del ciclo de vida se encuentra cada entrada del portafolio.

## 1. Idea (Semilla)
-   **Qué es**: Solo existe en tu cabeza o en un papel. No hay código ni prototipo físico.
-   **Ejemplo**: El "AI Scrum Master" (antes de hoy).
-   **Valor**: Muestra visión y creatividad.

## 2. PoC (Proof of Concept / Prueba de Concepto)
-   **Qué es**: Funciona, pero es feo o inestable. Un experimento rápido para validar si es posible.
-   **Ejemplo**: El "PC Drawer" cuando solo era una caja de madera con ventiladores pegados con cinta.
-   **Valor**: Muestra capacidad de validación rápida.

## 3. WiP (Work in Progress / En Construcción)
-   **Qué es**: Ya pasaste la validación, ahora lo estás construyendo bien. Está incompleto pero sólido.
-   **Ejemplo**: El "Grinch" (tiene estructura pero le falta piel) o "Project Voice" (funciona pero tiene latencia).
-   **Valor**: Muestra ejecución y perseverancia.

## 4. Done (Terminado / Operativo)
-   **Qué es**: Ya está en producción, lo usas diario y no se rompe.
-   **Ejemplo**: La "Bomba de Agua V3" o el "Marl Flow".
-   **Valor**: Muestra cierre y calidad.

---

### Nota de Implementación
El campo `status` en el Frontmatter de los archivos Markdown debe corresponder exactamente a uno de estos valores (en minúsculas): `idea`, `poc`, `wip`, `done`.
