# Estructura de carpetas del código — Proyecto CCMS-Nav

Estructura de carpetas generada en `Proyecto-CCMS-Nav/output/app/`, sin 
lógica de implementación — solo carpetas y archivos con un comentario 
breve indicando su responsabilidad, para revisar la organización antes de 
escribir código real. Cada decisión de organización cita qué parte de 
`solucion_arquitectura_ccms.md` o de `aacf/` la sustenta.

## Forma general: `backend/` + `frontend/`, patrón aacf adaptado

```
app/
├── backend/
├── frontend/
├── docker-compose.yml
└── README.md
```

Sigue el golden-path de `aacf/templates/web-app.md` (proyecto dividido en 
`frontend/`/`backend/`, `docker-compose.yml` en la raíz) — pero **dentro** 
de `backend/` se usa la nomenclatura `routers/`/`services/`/`storage/` ya 
validada en el curso (`fase-1-backend` en adelante), no `api/`/`db/` de la 
plantilla aacf genérica: el patrón del curso ya demostró, migración tras 
migración (Fase 1 → Fase 2 → Fase 3), que routers y services no necesitan 
tocarse cuando cambia la capa de almacenamiento — es el patrón que este 
proyecto reutiliza explícitamente, según pidió el encargo.

## Aclaración: diferencia entre models/, schemas/ y storage/

**`models/` — cómo se ven los datos por dentro de la base de datos.** Son 
las clases SQLAlchemy (ej. ObjetoContenido, Revision, Version de la Fase 2 
del curso) que definen columnas, tipos, claves primarias y foráneas. 
Responden a la pregunta: "¿qué forma tiene una fila de la tabla revisiones 
en PostgreSQL?". No tienen ninguna lógica — son solo la traducción entre 
tablas SQL y clases Python, tal como se vio con el ORM.

**`schemas/` — cómo se ven los datos por fuera, cruzando la red.** Son las 
clases Pydantic (ej. TopicCreate/TopicResponse de la Fase 1 del curso) que 
definen qué forma debe tener el JSON que entra y sale por la API. Responden 
a la pregunta: "¿qué campos se esperan recibir en un POST /topics, y qué 
campos se devuelven en la respuesta?". Son distintos de models/ aunque a 
veces se parezcan mucho: el contrato público de la API no tiene por qué 
coincidir exactamente con cómo se guarda internamente (ej. TopicCreate no 
lleva id porque aún no existe; Revision en la BD sí tiene columnas que 
nunca se expondrían directamente en un JSON, como claves internas de 
auditoría).

**`storage/` — quién sabe hablar de verdad con la base de datos.** Es la 
capa que usa models/ para ejecutar consultas reales (SELECT, INSERT, 
UPDATE) contra PostgreSQL — recuerda memory_store.py en la Fase 1, y su 
evolución a hablar con PostgreSQL en la Fase 2 sin que routers/services 
tuvieran que cambiar una línea. Responde a la pregunta: "¿cómo se consigue, 
guarda o actualiza estos datos, sea cual sea el motor detrás?".

### La cadena completa de una petición

1. Llega un POST /topics → schemas/ valida que el JSON tiene la forma 
   esperada (TopicCreate)
2. routers/ pasa esos datos a services/
3. services/ decide la lógica de negocio (permisos, aislamiento por 
   proyecto/cliente) y llama a storage/
4. storage/ traduce eso a una operación real usando models/ (la clase 
   SQLAlchemy correspondiente), y la ejecuta contra PostgreSQL
5. La respuesta vuelve por el mismo camino, y schemas/ (TopicResponse en 
   este caso) define qué forma tiene el JSON de vuelta

### Resumen en una frase cada una

- `models/` = la forma de los datos DENTRO de la base de datos (SQLAlchemy)
- `schemas/` = la forma de los datos EN LA API (Pydantic, lo que viaja por 
  HTTP)
- `storage/` = el código que CONECTA ambas cosas, ejecutando las 
  operaciones reales

## `backend/` — capas por responsabilidad

### `routers/` — traducción HTTP, sin lógica

Un router por recurso, uno por cada pantalla/funcionalidad principal del 
mockup (`solucion_arquitectura_ccms.md`, sección "Mapeo funcionalidad del 
mockup → pieza de backend"): `proyectos`, `contenido`, `bookmap`, 
`checkout`, `versiones`, `tareas`, `workflow`, `publicacion`, `servilog`, 
`busqueda`, `reports`, `admin`, `auditoria`, `comentarios`, `auth`. Mismo 
principio que en el curso: un router solo traduce HTTP↔servicio, nunca 
decide reglas de negocio.

### `services/` — lógica de negocio (capa con más detalle, a petición)

Un servicio por cada pieza identificada en el diagrama de arquitectura, 
simetría 1:1 con `routers/` salvo excepciones justificadas:

- **`proyectos_service.py`**: aplica la decisión A (aislamiento 
  multi-cliente) a nivel de gestión de proyectos — alta, listado.
- **`contenido_service.py`** / **`bookmap_service.py`**: separados porque 
  el mockup los trata como pantallas distintas (Navegador vs. Editor de 
  bookmap) con acciones distintas (consulta/CRUD vs. reordenar estructura).
- **`checkout_service.py`**: check-out/check-in — la pieza que habla con 
  el mecanismo `smartcms://` documentado en "Integración con XMetaL" de 
  `solucion_arquitectura_ccms.md`.
- **`versiones_service.py`**: versiones/baselines/diff.
- **`tareas_service.py`** / **`workflow_service.py`**: separados porque 
  son conceptos distintos en el esquema — `tareas` agrupa objetos con 
  asignación/reclamación; `workflow` es la máquina de estados 
  (`estados`/`objeto_estado`) sobre esos objetos.
- **`publisher_service.py`**: orquesta el encolado (habla con la tabla-cola, 
  RT-PUB-1.3); el procesamiento en sí vive en `worker/`, no aquí — mismo 
  principio de separación proceso-web / proceso-worker ya defendido en el 
  curso para tareas largas.
- **`servilog_service.py`** / **`indice_extraccion_service.py`**: 
  separados a propósito. `servilog_service` es el catálogo SIR en sí 
  (mismo storage que cualquier objeto DITA, RT-SL-1.1); 
  `indice_extraccion_service` es la pieza derivada (RT-SL-2.1 a 2.7) que 
  alimenta los extractos — mezclar ambos en un servicio ocultaría la 
  distinción "fuente de verdad vs. copia derivada" que sostiene toda la 
  arquitectura de este proyecto.
- **`busqueda_service.py`**: indexación incremental a OpenSearch + consulta 
  de facetas — nunca escribe en Postgres, solo lee de él.
- **`reports_service.py`**: enlaces rotos/huérfanos/cobertura — consumidor 
  de `validacion/` y del índice de extracción, no dueño de su propio dato.
- **`rbac_service.py`**: aplica la decisión C — lee el catálogo de roles/
  permisos como datos, nunca compara contra una constante en código.
- **`admin_service.py`** / **`auditoria_service.py`**: separados porque el 
  panel de Administración del mockup ya los trata como pestañas distintas 
  (Usuarios/Roles vs. Auditoría), con ciclo de vida de datos distinto 
  (configuración editable vs. log append-only).
- **`comentarios_service.py`**: pequeño pero propio — RF-CMS-7.5, tabla 
  nueva sin equivalente en el esquema del curso.

### `storage/` — acceso a datos, simetría con `services/`

Un módulo de storage por agregado de datos, replicando el patrón del curso: 
`services/` nunca importa SQLAlchemy directamente, solo llama a `storage/`. 
La consulta de OpenSearch **no** tiene módulo de storage propio — vive 
directamente en `services/busqueda_service.py`, porque OpenSearch mismo es 
el "storage" en ese caso (copia derivada, no hay una capa Postgres que 
envolver ahí).

### `models/` — un archivo por agregado, no un único `models.py`

**Desviación deliberada del patrón literal del curso** (que usaba un único 
`models.py`): aquí el esquema es mucho mayor — las 9 tablas base de 
`fase-2-bases-de-datos/2-construccion_esquema_bd.md` más `proyecto`, el 
catálogo RBAC (4 tablas), `tareas`/`comentarios`/`auditoria`, y las 7 
tablas del índice de extracción (RT-SL-2.2) — un único archivo dejaría de 
ser navegable. Se agrupan por agregado de dominio, no por tabla individual.

### `schemas/` — contratos Pydantic, un archivo por router

Espejo de `routers/`, siguiendo la misma razón de separación por dominio 
que `models/`.

### `auth/` — federación de identidad (decisión B)

Pieza completamente nueva frente al curso (que solo tenía un IdP). 
`federacion.py` es `AuthFed` del diagrama de arquitectura: normaliza 
cualquiera de las dos aserciones a un JWT interno único. Los dos adaptadores 
de Navantia (`idp_navantia_saml.py` / `idp_navantia_oidc.py`) existen ambos, 
sin decidir todavía cuál se usará — la sección "IdP de Navantia: dos 
escenarios posibles" de `solucion_arquitectura_ccms.md` documenta ambos 
caminos en detalle para no bloquear el desarrollo mientras Navantia confirma 
el protocolo.

### `core/` — piezas transversales, no atadas a un solo recurso

**`proyecto_context.py` es la pieza más importante de esta carpeta**: la 
decisión A de `tensiones_pendientes_tras_aacf_analisis.md` exige aislamiento 
"no solo un filtro de UI" — eso significa que el aislamiento por proyecto/
régimen de gobernanza no puede vivir dentro de un único servicio, tiene que 
ser una dependencia que atraviese *todos* los routers. `seguridad.py` 
cumple el mismo papel para JWT+RBAC (cada endpoint los necesita, según 
`rules/atexis-hard-rules.md` de aacf). `config.py` cumple HR0/HR8 de aacf 
("nada hardcodeado, todo configurable").

### `validacion/` — ampliada frente al curso, con eXist-db como candidato

Cuatro módulos, no uno: DTD/XSD 1.3, Schematron, integridad referencial 
(keyref/conref/href), y `exist_db_client.py`. Este último está marcado en 
el propio comentario del archivo como **"candidato real, no activo 
todavía"** — exactamente el estatus fijado en `solucion_arquitectura_ccms.md` 
tras confirmar (RF-SL-1.3, RT-SL-1.1, RT-SL-2.7) que el índice de 
extracción de ServiLog se deriva de XML DITA con semántica estructural 
propia. Existe como archivo para que la interfaz quede prevista, no para 
que se implemente ya.

### `worker/` — proceso separado de publicación

Deliberadamente fuera de `services/`: el diagrama de arquitectura dibuja 
`Worker` como una caja distinta de `Services`, consumiendo la tabla-cola 
en su propio proceso — mismo principio que el checkpoint de microservicios 
de `fase-1-backend/README.md` ya fijó para tareas largas que no deben 
bloquear peticiones web.

## `frontend/` — un dashboard, no una implementación

Estructura calcada de `aacf/templates/web-app.md` 
(`components/`/`pages/`/`services/`/`stores/`/`hooks/`/`types/`). Las 13 
páginas en `pages/` corresponden una a una a las pantallas del mockup 
(`Mockup CCMS S80 v04.html`) — incluyendo `Login` y `TopicDetalle`, que no 
están en la barra de navegación pero sí son pantallas reales del mockup. 
`components/` lleva solo un puñado de piezas verdaderamente compartidas 
(Topbar, Sidebar, DataTable, StatusBadge) — el resto de composición vive en 
cada página, sin adelantar decisiones de diseño de componentes que no se 
han tomado todavía.

## Lo que NO se ha decidido en esta estructura (a propósito)

- No hay carpeta ni módulo para el LLM local ni para el clúster de 
  OpenSearch — ambos siguen "opcional/futuro" en la arquitectura, sin caso 
  de uso activo; añadir estructura de código para ellos ahora sería 
  anticipar una decisión no tomada.
- `exist_db_client.py` existe como archivo (para que la interfaz de 
  `validacion/` quede completa) pero no se activa ni se conecta a nada 
  todavía — es "candidato real", no "implementado".
- No se ha decidido si `idp_navantia_saml.py` o `idp_navantia_oidc.py` es 
  el que finalmente se usa — ambos quedan como esqueleto hasta que Navantia 
  confirme el protocolo.
