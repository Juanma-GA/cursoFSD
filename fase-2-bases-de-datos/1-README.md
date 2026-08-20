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

**Aclaración: DRM es un producto de software, no solo un método**

DRM es un módulo de software concreto de IXIASoft — opcional y vendido/activado 
aparte, no un concepto genérico que todo CCMS implemente igual. Sin el módulo 
DRM activado, IXIASoft CCMS ya tiene branching "out-of-the-box" para versionar 
documentación; DRM es una capa adicional más sofisticada sobre esa base.

Distinción importante:
- **DRM** = producto de software concreto de IXIASoft (módulo opcional, de pago)
- **Branching a nivel de topic / reutilización entre versiones** = el concepto 
  de arquitectura de fondo, trasladable a un diseño propio sin depender de ese 
  producto específico

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

## Comparativa: cómo lo resuelven Heretto y Bluestream (XDocs)

### Patrón común a los tres proveedores (IXIASoft, Heretto, Bluestream)
Los tres usan el mismo concepto de fondo: branching + merge a nivel de 
componente individual (topic), no de documento completo. Las diferencias están 
en la experiencia de usuario y las herramientas de soporte, no en el concepto 
de arquitectura.

### Heretto: historial por recurso + colaboración en tiempo real
- Historial de revisiones por recurso individual (topics, mapas, media), 
  accesible en una pestaña "History", con opción de revertir a versiones 
  anteriores.
- Detalle de diseño revelador: restaurar un mapa a una versión anterior NO 
  restaura automáticamente los topics que contiene a sus versiones anteriores — 
  refleja que un topic es una entidad independiente con su propio ciclo de vida, 
  no "parte" del documento que lo contiene.
- Diferenciador principal: colaboración en tiempo real tipo Google Docs — todo 
  el equipo en el mismo archivo simultáneamente, sin bloqueo de ficheros, sin 
  check-in/check-out. Es un modelo de concurrencia distinto al bloqueo 
  tradicional de ficheros ("file locking") que usan sistemas más clásicos.

### Bluestream XDocs: el mecanismo de merge más explícito
- Permite trabajar de forma independiente en versiones de topics en ramas 
  distintas; al fusionar, el sistema muestra los cambios y posibles conflictos, 
  y el usuario decide qué cambios fusionar — el mismo lenguaje que un merge de 
  Git con conflictos, pero aplicado a componentes XML individuales.
- Integra DITA Merge de DeltaXML, una herramienta especializada en comparar y 
  fusionar XML de forma semántica (entendiendo la estructura, no solo 
  comparando texto línea a línea como un diff genérico).
- Dato de posicionamiento: el propio Bluestream reconoce en un whitepaper que 
  las necesidades de versionado de contenido DITA pueden resolverse con Git 
  (open source) o con un CCMS comercial, dependiendo de la complejidad real del 
  caso — confirmación, desde el propio vendedor, de que la complejidad debe 
  justificar la herramienta.

### Conclusión aplicable al diseño del esquema en PostgreSQL
Los tres convergen en: branch + merge a nivel de topic individual, con 
historial de revisiones por componente. Para el esquema propio, esto sugiere 
como mínimo: una relación many-to-many entre topics y versiones/ramas (un topic 
puede pertenecer a varias líneas de versión a la vez), más una tabla de 
historial/revisiones por topic — el mismo patrón confirmado como estándar de 
facto del sector.

## Instalación de PostgreSQL: nativo vs Docker

### Instalación nativa
El instalador oficial de PostgreSQL para Windows lo instala como un servicio 
del sistema que arranca automáticamente.
- Ventajas: más simple al principio, no requiere conocer Docker, arranca solo.
- Inconvenientes: queda instalado permanentemente, ocupa un servicio en segundo 
  plano continuo, "empezar de cero" implica desinstalar/reinstalar, no está 
  aislado del resto del sistema.

### Vía Docker (contenedor)
PostgreSQL corre dentro de un contenedor: un entorno aislado, ligero, separado 
del sistema operativo, en vez de instalarse directamente en él.
- Ventajas: completamente aislado (borrar y empezar de cero es instantáneo), 
  se pueden tener varias versiones en paralelo sin conflicto, es como se 
  despliega en producción en la mayoría de empresas hoy en día, arranque con 
  un solo comando.
- Inconvenientes: requiere tener Docker instalado, no arranca solo al encender 
  el ordenador (hay que levantarlo), añade una capa conceptual extra.

### Decisión para este curso
Se usa Docker en este ejercicio: en muchos entornos corporativos con permisos 
restringidos, un instalador nativo que requiere admin puede estar bloqueado, 
mientras que Docker Desktop suele funcionar sin problema. Esto además adelanta 
de forma práctica parte de lo que se verá con más profundidad en la Fase 5.

### Instrucciones: levantar PostgreSQL con Docker

1. Instalar Docker Desktop desde https://www.docker.com/products/docker-desktop/

2. Levantar PostgreSQL con un solo comando:

```bash
docker run --name ccms-postgres -e POSTGRES_PASSWORD=curso123 -e POSTGRES_DB=ccms -p 5432:5432 -d postgres
```

Qué hace cada parte:
- `docker run`: crea y arranca un contenedor nuevo
- `--name ccms-postgres`: nombre del contenedor para gestionarlo después
- `-e POSTGRES_PASSWORD=curso123`: variable de entorno con la contraseña del 
  usuario admin de PostgreSQL
- `-e POSTGRES_DB=ccms`: crea automáticamente una base de datos llamada `ccms`
- `-p 5432:5432`: conecta el puerto 5432 de la máquina local con el puerto 5432 
  dentro del contenedor (puerto por defecto de PostgreSQL)
- `-d`: corre el contenedor en segundo plano (detached), sin bloquear la terminal
- `postgres`: imagen oficial de PostgreSQL, descargada automáticamente la 
  primera vez

3. Comandos útiles:

```bash
docker ps                    # ver contenedores corriendo ahora mismo
docker stop ccms-postgres    # parar el contenedor
docker start ccms-postgres   # volver a arrancarlo (sin repetir 'docker run')
docker logs ccms-postgres    # ver qué pasa dentro, útil para depurar
```

4. El backend se conecta a este PostgreSQL exactamente igual que si estuviera 
instalado de forma nativa: desde el código Python, localhost:5432 es 
indistinguible entre ambas opciones — Docker mapea el puerto de forma 
transparente.
