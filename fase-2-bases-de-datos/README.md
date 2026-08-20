# Fase 2 — Bases de datos

## Resumen

En esta fase se trabaja el modelado y gestión de datos: bases de datos relacionales y no relacionales, diseño de esquemas, consultas y su integración con el backend.

## Checklist de conceptos clave

- [ ] (pendiente de definir)

## Conceptos clave

### Relacional (SQL): PostgreSQL/MySQL
Datos en tablas, con claves primarias/foráneas conectándolas, normalización 
(evitar duplicados repartiendo datos en tablas relacionadas), índices (búsquedas 
rápidas), transacciones ACID (todo se guarda o nada se guarda), y JOINs 
(combinar datos de varias tablas). Ideal para metadatos, usuarios, permisos, 
flujos de trabajo — todo con estructura fija y relaciones claras.

### Documental (NoSQL): MongoDB o similar
Guarda documentos tipo JSON con estructura flexible (cada documento puede tener 
campos distintos). Útil cuando el contenido es semiestructurado y no conviene 
forzarlo a un esquema de tablas fijo desde el principio.

### Bases de datos XML nativas (eXist-db, MarkLogic, BaseX)
Pensadas para almacenar, versionar y consultar XML directamente, con su propio 
lenguaje de consulta (XQuery/XPath), sin aplanarlo antes a tablas relacionales. 
Es la pieza más específica del mundo CCMS/DITA — probablemente la que aparece en 
herramientas comerciales reales del sector.

### Control de versiones de contenido
Git da la intuición (ramas, commits, diffs), pero un CCMS necesita versionar a 
nivel de topic/componente individual, no de fichero completo — un mismo topic 
puede vivir en múltiples manuales a la vez.

### Motores de búsqueda (Elasticsearch/OpenSearch)
Búsqueda full-text, facetas, relevancia — necesario para encontrar contenido 
reutilizable entre miles de topics.

### Bases de datos vectoriales (nivel conceptual)
Se usan para búsqueda semántica ("topics similares en significado"), en 
contraste con la búsqueda por palabra clave de Elasticsearch.

## Investigación: cómo IXIASoft controla versiones a nivel de componente

### La base de datos de fondo: TEXTML Server
IXIASoft no usa una base de datos relacional — usa su propia base de datos XML 
nativa, TEXTML Server. Es el mismo enfoque conceptual que eXist-db: guardar y 
consultar XML directamente, sin aplanarlo a tablas.

### El modelo de versionado: Dynamic Release Management (DRM)
Organiza el contenido en tres niveles jerárquicos:
- **Producto**: nivel superior, con sus propios metadatos.
- **Release**: agrupación lógica dentro de un producto.
- **Versión**: donde vive el contenido real. Un topic siempre se crea dentro de 
  una versión concreta, y el mismo objeto de contenido puede reutilizarse en más 
  de una versión a la vez.

### El mecanismo clave: Branching a nivel de topic, no de manual completo
Permite crear una nueva versión de la documentación basada en la versión actual 
(ej. Versión 1 → Versión 2) sin afectar a la original. La parte importante: no 
se ramifica el manual entero — se ramifica **topic por topic**, solo cuando hace 
falta. Si un topic no cambia entre versiones, sigue siendo literalmente el mismo 
objeto compartido y referenciado desde ambas. Solo al editarlo en el contexto de 
una versión se crea una copia divergente de ese topic concreto — un patrón tipo 
"copy-on-write" aplicado a contenido, no a código.

También permite el camino inverso: aplicar cambios hechos en una versión nueva 
de vuelta a una versión anterior (ej. una funcionalidad añadida en Versión 2 que 
se decide incorporar también en Versión 1).

### El mecanismo técnico DITA que lo hace posible
Usa las **keys y keyrefs de DITA 1.2/1.3**: un topic no se referencia por una 
ruta de fichero fija, sino por una clave indirecta que en cada versión puede 
apuntar a una copia distinta del contenido real. Esto es lo que un sistema de 
ficheros versionado con Git no da de forma nativa — Git versiona el repositorio 
completo por commits, no objetos de contenido individuales con reutilización 
cruzada entre "ramas" de producto.

### Otras capacidades del modelo
Registro automático de todas las revisiones y comentarios, gestión de objetos en 
ramas editables bajo condiciones específicas, reversión a revisiones anteriores, 
comparación de diferencias (diff) entre revisiones, y "Snapshot" del estado 
completo de un documento en un momento concreto.

**Fuentes:** documentación oficial de IXIASOFT/MadCap Software sobre el módulo 
Dynamic Release Management (ixiasoft.com, madcapsoftware.com).

## Ejercicio

_Pendiente de empezar esta fase._
