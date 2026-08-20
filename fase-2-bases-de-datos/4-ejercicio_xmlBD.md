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
