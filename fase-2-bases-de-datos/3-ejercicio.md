# Ejercicio — Fase 2: Bases de datos

## Objetivo
Sustituir el almacenamiento en memoria (MemoryStore) de la Fase 1 por PostgreSQL 
real, con un esquema diseñado a partir de cómo lo resuelven CCMS comerciales 
reales (IXIASoft, Heretto, Bluestream — ver secciones de investigación en 
`1-README.md`), manteniendo la arquitectura por capas ya construida.

## Parte 1: Instalación y esquema
1. Instalar PostgreSQL en local (nativo o vía Docker, según se decida).
2. Diseñar un esquema que refleje el patrón identificado en la investigación: 
   un topic puede pertenecer a varias versiones a la vez sin duplicarse, y cada 
   cambio a un topic debe quedar registrado como revisión. Tablas mínimas:
   - `topics`: el contenido en sí (o una referencia a él)
   - `versiones` (o `releases`): el contenedor lógico al que pertenece cada 
     estado del contenido
   - Una tabla intermedia **many-to-many** entre topics y versiones (un topic 
     puede vivir sin cambios en varias versiones a la vez — está referenciado, 
     no copiado)
   - `revisiones` / `historial`: registro de cada cambio a un topic concreto, 
     con autor y fecha
   - `autores`: usuarios que crean/modifican contenido

## Parte 2: Migración del backend
3. Adaptar el backend de la Fase 1 en fase-2-bases-de-datos/api, donde 
   storage/ hable con PostgreSQL (vía SQLAlchemy) en vez de memoria. Routers y 
   services no deberían necesitar cambios, o casi ninguno — confirmar 
   explícitamente qué cambia y qué no cambia, para verificar que la separación 
   por capas de la Fase 1 cumplió su propósito.
4. Probar que, tras crear un topic y reiniciar el servidor, el topic sigue ahí 
   (a diferencia del comportamiento en memoria de la Fase 1).

## Parte 3: Comparación conceptual con base de datos XML nativa
5. Mostrar cómo se vería el mismo problema (guardar y consultar un topic) 
   resuelto con eXist-db y XQuery, sin necesidad de instalarlo — solo código de 
   ejemplo y explicación de la diferencia de enfoque frente al modelo relacional.

## Nota sobre alcance
No se implementa el sistema completo de branching/merge de los CCMS comerciales 
(sería un proyecto en sí mismo) — el objetivo es diseñar el esquema relacional 
con esa arquitectura en mente desde el principio, y construir un CRUD simple 
sobre ese esquema ya bien pensado.

## Creación de las tablas con SQLAlchemy

Migración del backend de la Fase 1 (almacenamiento en memoria) a PostgreSQL 
real, replicando `fase-1-backend/api/` en `fase-2-bases-de-datos/api/` y 
sustituyendo solo la capa de almacenamiento por una que habla con la base de 
datos a través del esquema diseñado en `2-construccion_esquema_bd.md`.

### Qué cambió y qué no cambió respecto a la Fase 1

**Copiados sin modificar (byte a byte, confirmado con `diff`):**
- `main.py`
- `schemas.py`
- `routers/__init__.py`
- `routers/topics.py`
- `services/__init__.py`
- `services/topics_service.py`
- `storage/__init__.py`

**Cambiados o nuevos:**
- `storage/memory_store.py` — reescrito para hablar con PostgreSQL vía 
  SQLAlchemy, pero manteniendo exactamente la misma interfaz (`crear()`, 
  `listar()`, `obtener()`, dataclass `Topic`) que ya usaban `routers/` y 
  `services/`. El nombre del archivo se mantiene igual a propósito, para no 
  tener que tocar el `from storage import memory_store` de 
  `services/topics_service.py`.
- `requirements.txt` — se añaden `sqlalchemy` y `psycopg2-binary`.
- `database.py` (nuevo) — configuración de conexión a PostgreSQL.
- `models.py` (nuevo) — las 9 tablas del esquema como clases SQLAlchemy.
- `crear_tablas.py` (nuevo) — script para crear las tablas en la base de 
  datos real.

**Conclusión:** cero cambios en `routers/` y `services/` — toda la migración 
de "memoria" a "PostgreSQL" quedó contenida en la capa de almacenamiento, tal 
como se diseñó en la Fase 1. La separación por capas cumplió su propósito.

### Decisión de diseño: autor por defecto

El esquema exige un `autor_id` en cada revisión (`revisiones.autor_id`, FK 
obligatoria), pero la Fase 1 no tiene login ni gestión de usuarios todavía. 
Se usa un autor de prueba fijo (`Autor de prueba`, 
`autor.prueba@ccms.local`), creado automáticamente en la base de datos la 
primera vez que se guarda un topic. Esto quedará sustituido por un autor real 
cuando se implemente autenticación en una fase posterior.

### database.py: configuración de conexión

```python
DATABASE_URL = "postgresql+psycopg2://postgres:curso123@localhost:5432/ccms"
```

Mismas credenciales que el contenedor Docker `ccms-postgres` descrito en 
`1-README.md` (sección "Instalación de PostgreSQL: nativo vs Docker") — 
usuario `postgres`, password `curso123`, base de datos `ccms`, puerto `5432`.

### Cómo crear las tablas

Con el contenedor `ccms-postgres` corriendo y las dependencias instaladas 
(`pip install -r requirements.txt`), desde `fase-2-bases-de-datos/api/`:

```bash
python crear_tablas.py
```

Esto ejecuta `Base.metadata.create_all(bind=engine)`, que crea las 9 tablas 
si no existen todavía (no falla ni duplica nada si ya estaban creadas).

### Verificación con psql

```bash
docker exec -it ccms-postgres psql -U postgres -d ccms
```

Y dentro de la sesión de psql, `\dt` para listar las tablas. Resultado real 
obtenido durante el desarrollo de este ejercicio:

```
               List of relations
 Schema |       Name        | Type  |  Owner   
--------+-------------------+-------+----------
 public | autores           | table | postgres
 public | baseline_version  | table | postgres
 public | baselines         | table | postgres
 public | estados           | table | postgres
 public | mapa_topic_refs   | table | postgres
 public | objeto_estado     | table | postgres
 public | objetos_contenido | table | postgres
 public | revisiones        | table | postgres
 public | versiones         | table | postgres
(9 rows)
```

Las 9 tablas del esquema quedaron creadas, con las FK esperadas — por 
ejemplo, `\d revisiones` confirma `objeto_id` y `autor_id` como claves 
foráneas hacia `objetos_contenido` y `autores`, y `contenido` como columna 
`text` sin restricción `NOT NULL` (puede quedar en blanco cuando el objeto es 
un ditamap, tal como especifica `2-construccion_esquema_bd.md`).

> **Nota sobre cómo se validó este ejercicio:** en el entorno de desarrollo 
> usado para construir y probar este código (el sandbox de Claude Code), 
> `docker pull postgres` no fue posible por una restricción de red de ese 
> entorno concreto (Docker Hub bloqueado por política de egress de esa 
> sesión) — no relacionado con Docker en tu máquina. Para poder validar el 
> código igualmente, se instaló PostgreSQL 16 de forma nativa en ese sandbox, 
> con las mismas credenciales (`postgres` / `curso123` / base de datos 
> `ccms` / puerto `5432`), y se confirmó que la creación de tablas y el CRUD 
> completo (crear, listar, mejorar) funcionan de extremo a extremo contra esa 
> base de datos real. El código de `database.py`, `models.py` y 
> `storage/memory_store.py` es exactamente el mismo tanto si PostgreSQL corre 
> en Docker como si corre nativo — solo cambia dónde vive el servidor, nunca 
> el código Python. En tu máquina, con el contenedor `ccms-postgres` 
> levantado según las instrucciones de `1-README.md`, el mismo `python 
> crear_tablas.py` y los mismos comandos `docker exec -it ccms-postgres psql 
> ...` funcionarán sin ningún cambio.

### Prueba end-to-end realizada

Con la API levantada (`uvicorn main:app --reload`) contra la base de datos 
real:

```
POST /topics          → 201, topic creado con id=1
GET /topics            → 200, devuelve el topic recién creado
POST /topics/1/mejorar → 200, sugerencia mock sin sobrescribir el original
POST /topics/999/mejorar → 404, "No existe ningún topic con id=999"
```

Y confirmado directamente en la base de datos que los datos quedaron 
repartidos tal como dicta el esquema: una fila en `objetos_contenido` (la 
identidad del topic, sin contenido), una fila en `autores` (el autor de 
prueba, creada automáticamente), y una fila en `revisiones` (ahí sí, con el 
`contenido` real) — igual que se describe en la sección "Renombrado de 
conceptos" de `2-construccion_esquema_bd.md`: el contenido vive en la 
revisión, no en el objeto.

### Qué da SQLAlchemy (ORM) frente a escribir el SQL a mano

En general, para las 9 tablas, el ORM aporta lo mismo: cada tabla se define 
una sola vez como una clase Python, y de ahí sale tanto el `CREATE TABLE` 
como la forma de consultar/insertar datos, sin mantener dos versiones 
separadas (el SQL y el código) sincronizadas a mano. Con SQL puro, cada 
`CREATE TABLE ... REFERENCES ...` es un archivo `.sql` aparte que hay que 
ejecutar en el orden correcto (las tablas que reciben FK antes que las que 
las declaran) y mantener manualmente sincronizado con el código Python que 
las usa.

Diferencias concretas, tabla por tabla:

- **`objetos_contenido` / `autores` / `estados`** (tablas sin FK propias): 
  aquí el ORM aporta sobre todo el mapeo de tipos (`String(20)` → 
  `VARCHAR(20)`, `Integer` PK → `SERIAL`) sin tener que memorizar la sintaxis 
  exacta de PostgreSQL, y `unique=True` (en `autores.email`, 
  `estados.nombre`) genera la restricción `UNIQUE` sin escribir 
  `ALTER TABLE ... ADD CONSTRAINT` aparte.

- **`revisiones` / `versiones` / `objeto_estado` / `baseline_version` / 
  `mapa_topic_refs`** (tablas con una o varias FK): `ForeignKey("tabla.id")` 
  genera la restricción de clave foránea automáticamente, y 
  `Base.metadata.create_all()` calcula solo el orden correcto de creación 
  según esas dependencias — con SQL a mano, ese orden hay que deducirlo y 
  respetarlo uno mismo, o la base de datos rechaza la tabla que use una FK 
  hacia otra que aún no existe. `mapa_topic_refs` es el caso más cargado de 
  FK (a `revisiones`, dos veces a `objetos_contenido`/`versiones`): con el 
  ORM cada una queda declarada junto a su columna, en vez de agrupadas al 
  final del `CREATE TABLE` como en SQL puro.

- **`baselines`**: tiene FK hacia dos tablas distintas (`objetos_contenido` y 
  `revisiones`) — el modelo Python queda como documentación viva de esa 
  relación; no hace falta volver al diagrama Mermaid para recordar qué 
  apunta a qué mientras se escribe código.

- En todas: las consultas se escriben como `db.query(Modelo).filter_by(...)` 
  en vez de componer strings SQL a mano, lo que evita construir SQL por 
  concatenación (fuente común de inyección SQL) — SQLAlchemy parametriza los 
  valores automáticamente.

Lo que el ORM NO cambia: los tipos de datos y restricciones siguen siendo 
decisión de quien diseña el esquema (por eso `2-construccion_esquema_bd.md` 
sigue teniendo una sección "Pendiente de decidir" con NOT NULL/UNIQUE/CHECK 
por definir) — SQLAlchemy solo traduce esa decisión a SQL real, no la toma 
por ti.
