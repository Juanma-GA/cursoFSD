# Motores de búsqueda: Elasticsearch/OpenSearch (comparación conceptual)

Cuarta pieza de la Fase 2: qué problema resuelven los motores de búsqueda que 
ni PostgreSQL ni una base XML nativa (ver 4-ejercicio_xmlBD.md) resuelven 
bien. Igual que con eXist-db, este ejercicio es conceptual, con ejemplos de 
código reales, sin instalación — se retomará de forma práctica más adelante 
(Fase 4 o Fase 6), cuando haya topics reales creados para indexar de verdad.

## Qué problema resuelven que PostgreSQL y eXist-db no resuelven bien

- **PostgreSQL**: puede hacer `WHERE contenido LIKE '%driver%'`, pero es una 
  búsqueda de texto literal, lenta a gran escala, sin entender relevancia 
  (qué resultado es "más" sobre ese tema), sin tolerancia a errores 
  tipográficos, sin ordenar por qué tan bien encaja cada resultado.
- **eXist-db**: puede buscar dentro de la estructura XML con `contains()` 
  (ver Ejemplo 3 de 4-ejercicio_xmlBD.md), pero tampoco está optimizado para 
  ranking de relevancia ni para búsquedas con miles de documentos con 
  rendimiento consistente.
- **Un motor de búsqueda** (Elasticsearch/OpenSearch) está diseñado 
  específicamente para: búsqueda full-text con relevancia (ranking de 
  resultados por qué tan bien encajan), tolerancia a errores tipográficos 
  (fuzzy search), facetas (filtrar por categorías, ej. "topics de la Versión 
  2, estado publicado, que mencionan 'driver'"), y rendimiento consistente 
  con grandes volúmenes de documentos.

Es la pieza que resuelve: "un autor necesita encontrar contenido reutilizable 
entre miles de topics, sin memorizar títulos exactos ni escribir búsquedas 
perfectas".

## Elasticsearch vs OpenSearch: por qué existen dos

En 2021, Elastic (la empresa detrás de Elasticsearch) cambió su licencia de 
Apache 2.0 a una licencia dual (SSPL / Elastic License), que dejó de 
considerarse open source según el estándar OSI. AWS respondió creando 
OpenSearch, un fork (una copia derivada) de la última versión de 
Elasticsearch bajo licencia Apache 2.0 abierta. Desde entonces, ambos 
proyectos han evolucionado por separado durante varios años.

Diferencias relevantes en 2026:
- **Licencia**: Elasticsearch añadió también AGPLv3 en 2024 (de nuevo 
  considerada open source), pero sigue reservando funcionalidades avanzadas 
  para planes de pago. OpenSearch se mantiene en Apache 2.0, gobernado por la 
  Linux Foundation, con más funcionalidades incluidas gratis (seguridad 
  empresarial, replicación entre clusters).
- **Motor de fondo**: ambos usan Apache Lucene por debajo (la misma librería 
  base de indexación y búsqueda) — el rendimiento en búsqueda de texto básica 
  es comparable en la mayoría de casos de uso.
- **Coste**: servicios gestionados de OpenSearch (ej. en AWS) suelen ser más 
  baratos que Elastic Cloud, con funcionalidades de seguridad incluidas que 
  en Elasticsearch requieren suscripción de pago.
- **Para un CCMS de tamaño medio**: la elección entre ambos importa menos que 
  el hecho de usar alguno de los dos — las diferencias relevantes (IA 
  avanzada, vector search a gran escala, SIEM) no son las prioridades de un 
  buscador de topics DITA. OpenSearch suele ser la opción más simple de 
  empezar por licencia y coste.

## Ejemplo 1: cómo se vería indexar un topic

Cuando se crea o actualiza un topic en PostgreSQL, además de guardarlo ahí, 
se envía una copia simplificada (solo lo relevante para buscar) al motor de 
búsqueda:

```python
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

es.index(
    index="topics",
    id="instalar-driver",
    document={
        "titulo": "Instalar el driver",
        "contenido": "Instrucciones para instalar el driver desde el panel de control.",
        "estado": "publicado",
        "version": "V2",
        "autor": "jgutierrez3"
    }
)
```

Esto no sustituye a PostgreSQL — es una copia derivada, optimizada solo para 
búsqueda. La fuente de verdad del contenido sigue siendo PostgreSQL (o 
eXist-db, en la solución mixta vista en 4-ejercicio_xmlBD.md).

## Ejemplo 2: búsqueda full-text con relevancia

```python
resultado = es.search(
    index="topics",
    query={
        "match": {
            "contenido": "instalar driver"
        }
    }
)
```

A diferencia de un `LIKE '%driver%'` en SQL, esto devuelve los resultados 
ordenados por relevancia (qué tan bien encaja cada topic con la búsqueda), 
tolera variaciones de la palabra, y funciona con rendimiento consistente 
aunque haya miles de topics indexados.

## Ejemplo 3: búsqueda con facetas (filtros combinados)

```python
resultado = es.search(
    index="topics",
    query={
        "bool": {
            "must": {"match": {"contenido": "driver"}},
            "filter": [
                {"term": {"estado": "publicado"}},
                {"term": {"version": "V2"}}
            ]
        }
    }
)
```

Esto responde a: "topics que mencionan 'driver', pero solo los publicados, y 
solo de la Versión 2" — la combinación de búsqueda de texto libre + filtros 
exactos es justo lo que se llama "búsqueda por facetas", muy común en 
paneles de administración de contenido.

## Cómo encajaría en la arquitectura de este proyecto

Con esto se completa el patrón de "polyglot persistence" (persistencia 
políglota) visto en 4-ejercicio_xmlBD.md, ahora con tres piezas:

- **PostgreSQL**: fuente de verdad de las relaciones (autores, revisiones, 
  versiones, estados) — lo ya construido en este proyecto.
- **eXist-db** (opcional, ampliación futura): fuente de verdad del contenido 
  XML/DITA en sí, si se adopta la solución mixta.
- **Elasticsearch/OpenSearch**: copia derivada, solo para búsqueda — nunca la 
  fuente de verdad, siempre una réplica optimizada que se puede reconstruir 
  desde PostgreSQL/eXist-db si hiciera falta.

Esto confirma lo ya identificado en el checkpoint de microservicios de la 
Fase 1: el motor de búsqueda es uno de los candidatos naturales a vivir fuera 
del backend principal, como servicio independiente — no porque el backend no 
pueda hablar con él, sino porque su ciclo de vida (indexar, reindexar, 
escalar) es distinto al del resto del sistema.

## Fuentes
Comparativas Elasticsearch vs OpenSearch 2026 (daily.dev, SigNoz, 
tech-insider.org, Oktopeak), documentación de licenciamiento de Elastic y 
OpenSearch Software Foundation (Linux Foundation).
