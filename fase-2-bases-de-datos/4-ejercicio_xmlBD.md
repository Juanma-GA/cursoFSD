# Comparación conceptual: eXist-db + XQuery vs PostgreSQL relacional

Tercera parte del ejercicio de la Fase 2 (ver 3-ejercicio.md): comparar 
conceptualmente cómo se resolvería el mismo problema (guardar y consultar un 
topic) con una base de datos XML nativa, sin necesidad de instalarla.

## La diferencia de enfoque, en una frase

Con PostgreSQL, el XML de un topic se guarda como texto dentro de una columna 
(`revisiones.contenido`) — la base de datos no entiende su estructura interna, 
solo lo trata como una cadena de texto. Con eXist-db, el XML se guarda TAL 
CUAL, como un documento real, y la base de datos entiende su estructura 
interna de forma nativa: puede consultar y modificar elementos y atributos 
concretos sin tener que leer todo el texto y volver a parsearlo en el backend.

## Ejemplo 1: guardar un topic como documento XML

En eXist-db, un topic DITA se guarda directamente como un archivo XML dentro 
de una colección (el equivalente a una "carpeta" de documentos):

```xquery
xquery version "3.0";

let $contenido :=
  <topic id="instalar-driver">
    <title>Instalar el driver</title>
    <body>
      <p>Instrucciones para instalar el driver desde el panel de control.</p>
    </body>
  </topic>
let $resultado := xmldb:store("/db/ccms/topics", "instalar-driver.xml", $contenido)
return $resultado
```

`xmldb:store()` guarda el documento XML completo, con su estructura de 
etiquetas intacta, en la colección `/db/ccms/topics`. No hay ninguna 
traducción a filas y columnas — el documento se persiste exactamente como es.

## Ejemplo 2: consultar el contenido de un topic concreto

```xquery
xquery version "3.0";

let $topic := doc("/db/ccms/topics/instalar-driver.xml")
return $topic/topic/body/p/text()
```

`doc()` carga el documento por su ruta. La expresión 
`$topic/topic/body/p/text()` es XPath: navega directamente por la jerarquía 
del XML (topic → body → p → texto) para extraer solo el contenido de ese 
párrafo concreto, sin tener que traer ni parsear el documento entero en el 
backend.

## Ejemplo 3: buscar topics por contenido (equivalente a un WHERE)

```xquery
xquery version "3.0";

for $topic in collection("/db/ccms/topics")/topic
where contains($topic/body/p, "driver")
order by $topic/title
return $topic/title/text()
```

Esta es una expresión FLWOR (`for`/`where`/`order by`/`return` — el 
equivalente funcional de SQL en XQuery). `collection()` recorre TODOS los 
documentos de esa carpeta, `where contains(...)` filtra por contenido dentro 
del XML (equivalente a un `WHERE columna LIKE '%driver%'` en SQL, pero 
buscando dentro de la estructura, no en una columna de texto plano), y 
`order by` ordena el resultado.

## Ejemplo 4: modificar solo el título, sin tocar el resto del documento

```xquery
xquery version "1.0";

let $doc := doc('/db/ccms/topics/instalar-driver.xml')/topic
return update value $doc/title with 'Cómo instalar el driver'
```

Esto es lo más distinto frente al modelo relacional: eXist-db puede 
actualizar un único elemento dentro de un documento XML existente, sin 
reescribir el documento entero ni tener que hacer un `UPDATE` sobre una 
columna de texto completa. Con PostgreSQL, cambiar solo el título implicaría 
reescribir toda la columna `contenido` (o haber modelado el título como una 
columna aparte desde el principio).

## Comparación directa con el enfoque de este proyecto

| Aspecto | PostgreSQL (usado en este proyecto) | eXist-db (XML nativo) |
|---|---|---|
| Dónde vive el XML | Como texto plano en `revisiones.contenido` | Como documento real, estructura intacta |
| Consultar una parte del contenido | Requiere traer todo el texto y parsear en el backend (Python) | XPath consulta directamente la estructura, sin traer todo el documento |
| Modificar solo un elemento | Reescribir la columna completa | Actualizar el nodo concreto, sin tocar el resto |
| Relaciones (topics, versiones, autores, FK) | Nativo y maduro (el punto fuerte de este proyecto) | Posible pero menos natural — no es su fortaleza |
| Lenguaje de consulta | SQL (declarativo sobre tablas) | XQuery/XPath (declarativo sobre árboles XML) |
| Validación de estructura DITA | Responsabilidad del backend | Puede validarse contra un esquema (schema) al guardar, de forma nativa |

## Por qué el checkpoint de la Fase 2 tiene sentido visto esto

La pregunta del checkpoint original era: ¿por qué un CCMS DITA suele necesitar 
algo más que "una tabla SQL con una columna de texto XML"?

La respuesta, con estos ejemplos delante: porque el modelo relacional 
(PostgreSQL) es excelente para lo que este proyecto ya construyó — relaciones 
entre topics, versiones, autores, revisiones, estados — pero trata el 
contenido XML en sí como una caja negra de texto. Una base XML nativa hace lo 
inverso: es excelente entendiendo y consultando la estructura interna del 
propio XML (DITA), pero modela relaciones de negocio (autores, workflow, 
estados) de forma menos natural que una base relacional.

En un CCMS real, ambos mundos suelen convivir: por eso IXIASoft usa TEXTML 
Server (XML nativo) como base de todo, mientras que otras arquitecturas de 
CCMS optan por PostgreSQL para las relaciones de negocio y dejan que el 
propio XML viva como texto, apoyándose en el backend (o en una capa de 
búsqueda como Elasticsearch, vista en la Fase 2) para todo lo que necesite 
entender su estructura interna.

## Fuentes
Documentación oficial de eXist-db (exist-db.org/exist/apps/doc), Wikibooks 
XQuery (en.wikibooks.org/wiki/XQuery).

## Preguntas frecuentes: otras bases XML, XQuery vs XPath, y solución mixta

### ¿MarkLogic, BaseX y eXist-db son lo mismo?

No son lo mismo, pero sí son de la misma categoría: las tres son bases de 
datos XML nativas que implementan XQuery/XPath. Diferencias:

- **eXist-db**: open source, gratuita, accesible para aprender y para 
  proyectos pequeños/medianos.
- **BaseX**: open source y gratuita, muy ligera y rápida, popular en 
  humanidades digitales (procesamiento de textos, TEI).
- **MarkLogic**: comercial (de pago), pensada para escala empresarial grande 
  — clustering, alta disponibilidad, búsqueda semántica integrada, seguridad 
  a nivel de documento. Habitual en clientes corporativos grandes.

Misma relación que existe entre PostgreSQL (open source) y Oracle Database 
(comercial, empresarial): mismo paradigma, distinto tamaño/precio de producto.

### ¿XQuery y XPath son lo mismo?

No, pero están estrechamente relacionados — XQuery incluye XPath dentro de sí.

- **XPath**: lenguaje para navegar por la estructura de un XML (ej. 
  `$topic/topic/body/p/text()`) — el "camino" hacia un dato concreto.
- **XQuery**: lenguaje más completo que incluye XPath para navegar, pero 
  añade capacidad de construir consultas complejas (FLWOR: for/where/order 
  by/return), transformar resultados, y generar XML nuevo como salida.

Analogía: XPath es como escribir una ruta de carpetas; XQuery es el programa 
completo que usa esas rutas para hacer algo con los datos.

### ¿Se puede tener una solución mixta (PostgreSQL + eXist-db a la vez)?

Sí — se llama "polyglot persistence" (persistencia políglota): usar la base 
de datos adecuada para cada tipo de dato, en vez de forzar todo a un único 
motor. Es habitual en sistemas reales, no una rareza.

Reparto posible en este CCMS:
- **PostgreSQL**: autores, estados, revisiones (metadatos: quién, cuándo), 
  versiones, relación topic↔estado — todo lo relacional ya construido.
- **eXist-db**: el contenido XML/DITA real de cada topic y ditamap — en vez 
  de guardarlo como texto plano en `revisiones.contenido`, se guardaría como 
  documento en eXist-db, y la fila de `revisiones` en PostgreSQL guardaría 
  solo una referencia (ej. la ruta del documento) en vez del texto completo.

El backend hablaría con ambas bases desde `storage/` — mismo patrón ya usado 
("una capa de storage habla con la persistencia"), solo que reparte el 
trabajo entre dos motores según el tipo de dato.

### ¿TEXTML es una base de datos de IXIASoft?

Sí — es la base de datos XML nativa propia de IXIASoft, propietaria (no 
usable fuera de su ecosistema), que sirve de motor de persistencia bajo su 
CCMS. Es a IXIASoft lo que eXist-db es en este proyecto: la pieza que guarda 
y consulta el XML de forma nativa. Diferencia: la de este proyecto es open 
source y genérica; la de IXIASoft es cerrada y viene empaquetada dentro de su 
producto comercial.

### ¿Qué implicaría cambiar de PostgreSQL a eXist-db en este proyecto?

**Se mantendría:**
- Routers y services de FastAPI — la interfaz hacia frontend/Oxygen no 
  cambia.
- El diseño conceptual del esquema (objetos_contenido, revisiones, versiones, 
  autores...) sigue teniendo sentido como modelo mental, aunque cambie cómo 
  se implementa.

**Cambiaría por completo:**
- psycopg2/SQLAlchemy desaparecen — se necesitaría una librería cliente de 
  eXist-db para Python (bibliotecas REST que hablan con su API HTTP).
- `models.py` (clases SQLAlchemy con columnas) deja de tener sentido tal 
  cual — las "tablas" pasarían a ser colecciones de documentos XML, y las 
  relaciones (ej. topic↔versión) se modelarían como atributos/referencias 
  dentro del propio XML, o se mantendrían en un sistema relacional aparte 
  (la solución mixta de arriba).
- Todas las consultas (`db.query(Modelo).filter_by(...)`) se reescribirían 
  como XQuery.
- `crear_tablas.py` se sustituiría por la creación de colecciones (carpetas 
  de documentos) en eXist-db.

**Recomendación para este proyecto:** no sustituir PostgreSQL por eXist-db 
por completo — se perdería la solidez relacional ya construida (revisiones, 
versiones, autores, estados), que es donde PostgreSQL es más fuerte. Lo que 
sí tendría sentido explorar más adelante (ampliación real de arquitectura, no 
en la Fase 2) es la solución mixta: mantener PostgreSQL para lo relacional 
tal como está, y añadir eXist-db específicamente para el contenido XML/DITA, 
sustituyendo solo la columna `revisiones.contenido` por una referencia a un 
documento en eXist-db. Posible ejercicio de ampliación en la Fase 4 
(arquitectura).
