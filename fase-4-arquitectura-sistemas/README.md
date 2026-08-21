# Fase 4 — Arquitectura de sistemas

## Resumen

En esta fase se trabaja el diseño de sistemas a mayor escala: patrones de arquitectura, escalabilidad, despliegue, infraestructura y buenas prácticas de sistemas distribuidos.

## Checklist de conceptos clave

- [ ] (pendiente de definir)

## Conceptos clave

### Arquitectura de 3 capas
Presentación (frontend React) / lógica de negocio (backend FastAPI) / datos 
(PostgreSQL, y potencialmente eXist-db). Mantenerlas separadas permite 
cambiar una pieza sin romper las demás — ya demostrado en la Fase 2, cuando 
la migración de memoria a PostgreSQL no requirió tocar routers ni services.

### REST vs GraphQL vs gRPC
Ya visto en el checkpoint de microservicios de la Fase 1. Para un CCMS, REST 
casi siempre es suficiente y más fácil de mantener. GraphQL aportaría valor 
solo si el frontend necesitara combinar datos de muchas fuentes distintas en 
una sola pantalla. gRPC solo tendría sentido para comunicación interna entre 
microservicios de alta frecuencia — ya descartados como innecesarios para 
esta escala.

### Diseño de arquitectura para CCMS: piezas ya construidas o exploradas
- Repositorio de contenido (BD XML nativa o relacional + almacenamiento de 
  ficheros): diseñado y comparado en la Fase 2 (construccion_esquema_bd.md, 
  4-ejercicio_xmlBD.md).
- Capa de integración con herramientas de autoría (Oxygen, vía API): patrón 
  de API Key ya conocido del proyecto previo.
- Capa de integración con el LLM (local, on-premise): el mock construido en 
  la Fase 1 (POST /topics/{id}/mejorar), ahora a pensar en su versión real.
- Motor de workflow (borrador → revisión → aprobado → publicado): tabla 
  `estados` diseñada en la Fase 2.
- Pipeline de publicación (DITA-OT, generación de PDF/HTML/help): nuevo en 
  esta fase.
- Motor de búsqueda y reutilización: Elasticsearch/OpenSearch, ya comparado 
  conceptualmente en 5-ejercicio_busquedas.md de la Fase 2.

### Seguridad y residencia de datos
Cómo se traduce en arquitectura un requisito como "los datos no pueden salir 
de España" — ya aplicado de facto con el LLM local en el proyecto de Oxygen; 
en esta fase se entiende el porqué técnico: dónde vive físicamente cada 
servidor, qué tráfico sale a internet y cuál no.

### Escalabilidad y caché (nivel conceptual)
No es prioridad en un CCMS interno de tamaño medio, pero es necesario saber 
reconocer cuándo un proveedor vende complejidad innecesaria — mismo criterio 
aplicado en el checkpoint de microservicios de la Fase 1.

## Ejercicio

_Pendiente de empezar esta fase._
