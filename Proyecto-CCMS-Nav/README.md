# Proyecto CCMS-Nav

CCMS real para Navantia (documentación DITA de mantenimiento de los 
submarinos S80), con uso interno de ATEXIS además del propio deliverable 
de cliente. Se construye aplicando lo aprendido en el curso `cursoFSD` de 
este mismo repositorio — no es un ejercicio aparte, es la continuación 
directa de las fases anteriores sobre un caso real.

## Estructura de la carpeta

- **`aacf/`**: framework de requisitos corporativos de ATEXIS — las reglas, 
  la gobernanza, el sistema de diseño y los estándares de seguridad/
  cumplimiento que debe respetar cualquier aplicación construida en la 
  empresa. Se aplica en la parte de este proyecto bajo gobernanza interna 
  ATEXIS (ver `especificacion/tensiones_pendientes_tras_aacf_analisis.md`, 
  decisión A).
- **`especificacion/`**: los documentos de partida del proyecto real —
  el mockup navegable de la interfaz (`Mockup CCMS S80 v04.html`), el 
  listado definitivo de requisitos (`Requisitos Bloque CCMS v01.docx`), y 
  el análisis ya resuelto de las tensiones detectadas entre el mockup, los 
  requisitos y el framework `aacf/` 
  (`tensiones_pendientes_tras_aacf_analisis.md`).
- *(pendiente de completar a medida que avance el proyecto: arquitectura, 
  esquema de datos, estructura de carpetas del código)*

## Relación con el curso

Este proyecto reutiliza y adapta las decisiones de arquitectura ya 
validadas en las fases del curso (`fase-1-backend` a 
`fase-5-herramientas-vibe-coder`), en vez de partir de cero. La referencia 
principal de arquitectura base es 
[`fase-4-arquitectura-sistemas`](../fase-4-arquitectura-sistemas/), 
adaptada donde los requisitos reales de Navantia lo exigen.
