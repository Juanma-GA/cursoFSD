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

### Aclaración: por qué "transversal" significa "estructuralmente 
imposible de saltarse", no "una norma a recordar"

**El riesgo del enfoque frágil**: si cada service individual (proyectos, 
tareas, publicación, ServiLog, etc.) tuviera, dentro de su propio código, 
una línea que filtra manualmente por proyecto_id o comprueba permisos, 
bastaría que UN solo servicio lo olvide para que un dato de un proyecto 
Navantia se filtre hacia una consulta de un proyecto interno ATEXIS, o 
viceversa — el aislamiento dependería de que cada desarrollador se acuerde 
de aplicarlo en cada sitio, en cada endpoint nuevo que se añada en el 
futuro.

**El enfoque robusto que implementa core/**: `proyecto_context.py` y 
`seguridad.py` son dependencias de FastAPI (Depends) que se inyectan ANTES 
de que cualquier router ejecute su lógica de negocio:
- `proyecto_context.py` extrae de qué proyecto/cliente habla la petición 
  (del JWT o de la URL), y todas las consultas que pasen por storage/ a 
  partir de ahí quedan automáticamente acotadas a ese contexto — sin que el 
  desarrollador de cada servicio tenga que acordarse de nada.
- `seguridad.py` cumple el mismo papel para JWT+RBAC: ningún router puede 
  ejecutarse sin pasar primero por la comprobación de permiso, verificada 
  en un único sitio en vez de repetida (y potencialmente mal repetida) en 
  cada uno de los 16 servicios.

Es la diferencia entre "una norma que hay que recordar" y "una regla que el 
sistema hace estructuralmente imposible saltarse".

**Por qué config.py es de naturaleza distinta, aunque viva en la misma 
carpeta**: no intercepta peticiones como las dos piezas anteriores — es el 
único lugar donde viven valores que cambian según el entorno (URLs de los 
dos IdPs, credenciales de BD, endpoints de OpenSearch), siguiendo el mismo 
patrón .env practicado en la Fase 5 del curso. Está en core/ porque, como 
las otras dos, es algo que todo el resto del sistema necesita consultar sin 
pertenecer a ningún servicio concreto.

### Pendiente de verificar antes de escribir lógica real

Confirmar con un ejemplo de código (aunque sea solo la firma de una 
función, no la lógica completa) cómo un router típico (ej. el de tareas) 
importaría y usaría proyecto_context.py y seguridad.py como dependencias de 
FastAPI — para asegurar que la estructura hace estructuralmente imposible 
que un router se salte estas comprobaciones, y que esto no depende de que 
cada desarrollador se acuerde de añadirlas.

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

### Qué construye cada subcarpeta del frontend

- **`pages/`**: cada archivo corresponde a una pantalla completa del 
  mockup (Inicio, Proyectos, Navegador, Publisher, ServiLog...) — el nivel 
  más alto, lo que el usuario ve al navegar a una URL concreta.
- **`components/`**: piezas de interfaz reutilizadas en más de una pantalla 
  (Topbar, Sidebar, DataTable, StatusBadge). Deliberadamente pequeño: cada 
  página construye su propio contenido específico, sin forzar una librería 
  de componentes completa que aún no se ha diseñado — evita construir para 
  necesidades hipotéticas, mismo criterio ya aplicado en otras partes del 
  proyecto.
- **`services/`**: NOTA — mismo nombre que el `services/` del backend, 
  pero significado distinto. Aquí es el equivalente de api.js de la Fase 3 
  del curso: la capa que centraliza las llamadas fetch() hacia el backend 
  — no lógica de negocio, solo "cómo hablar con la API".
- **`stores/`**: pieza nueva respecto al curso (donde App.jsx guardaba 
  estado directamente con useState). Un store es un lugar centralizado 
  para estado que varias páginas necesitan compartir — ej. quién es el 
  usuario logueado, o en qué proyecto/cliente está trabajando ahora mismo 
  (el aislamiento por proyecto es transversal también en el frontend, no 
  solo en el backend). Cuando el estado deja de ser propio de una sola 
  página, useState dentro de un componente ya no basta.
- **`hooks/`**: funciones reutilizables que encapsulan lógica de React 
  repetida entre páginas (ej. "cargar datos con loading/error" — mismo 
  patrón visto en App.jsx con useEffect/cargando/error de la Fase 3, ahora 
  extraído para no repetirlo en cada página que lo necesite).
- **`types/`**: definiciones de la forma de los datos en el frontend 
  (TypeScript) — equivalente, del lado cliente, a lo que schemas/ es del 
  lado backend.

## Aclaración: OpenSearch ya es pieza activa, no pendiente de decidir

**OpenSearch (instancia única) no es una decisión abierta** — quedó cerrada 
en `solucion_arquitectura_ccms.md` (sección "OpenSearch (no Elasticsearch) 
— búsqueda avanzada"), marcada `oss` (verde, activa) en el diagrama de 
arquitectura. Esta estructura de carpetas ya lo refleja: `busqueda_service.py` 
existe como un servicio de primera clase, con el mismo trato que cualquier 
otro servicio activo (`proyectos_service.py`, `tareas_service.py`...) — su 
comentario describe una responsabilidad real ("indexación incremental a 
OpenSearch + consulta de facetas"), sin ninguna anotación de "candidato" ni 
"futuro".

**Matiz importante, para no confundir "activo" con "código ya escrito"**: 
ahora mismo `busqueda_service.py` es, igual que el resto de archivos de 
esta estructura, un archivo con un único comentario — todavía no existe 
código de conexión real a OpenSearch, porque esta fase del proyecto era 
explícitamente "solo estructura, sin lógica de implementación". Eso es 
distinto de eXist-db: `busqueda_service.py` no lleva ninguna marca de 
"candidato" porque su activación ya está decidida y solo falta 
implementarla; `exist_db_client.py` sí lleva la marca "CANDIDATO REAL, no 
activo todavía" en su propio comentario, porque ahí lo pendiente no es 
solo escribir el código — es decidir si se activa.

Lo que **sí** sigue siendo opcional/futuro sin caso de uso activo es 
únicamente el **clúster con réplicas** de OpenSearch (la ruta de escalado 
futura, distinta de la instancia única ya activa) y el LLM local — ninguno 
de los dos tiene carpeta ni módulo en esta estructura, a propósito.

## Lo que NO se ha decidido en esta estructura (a propósito)

- No hay carpeta ni módulo para el LLM local ni para el **clúster con 
  réplicas** de OpenSearch (no la instancia única, que ya está activa — ver 
  aclaración arriba) — ambos siguen "opcional/futuro" en la arquitectura, 
  sin caso de uso activo; añadir estructura de código para ellos ahora 
  sería anticipar una decisión no tomada.
- `exist_db_client.py` existe como archivo (para que la interfaz de 
  `validacion/` quede completa) pero no se activa ni se conecta a nada 
  todavía — es "candidato real", no "implementado". **Confirmado que sigue 
  así**: se preguntó explícitamente y la respuesta fue mantenerlo como 
  candidato sin activar — solo se documentó cómo se desplegaría *si* se 
  activa en el futuro (ver "Infraestructura física" más abajo).
- No se ha decidido si `idp_navantia_saml.py` o `idp_navantia_oidc.py` es 
  el que finalmente se usa — ambos quedan como esqueleto hasta que Navantia 
  confirme el protocolo.

## Infraestructura física: dónde viven las bases de datos

Todo lo documentado hasta aquí es **código** (`routers/`, `services/`, 
`storage/`, `models/`) — pero el código necesita algo corriendo detrás para 
conectarse. Esa infraestructura física **empieza a existir como marcador**, 
no como algo funcional todavía: `docker-compose.yml` ya declara los tres 
servicios de base de datos (imagen base únicamente, sin puertos, variables 
de entorno reales ni volúmenes) y `backend/.env.example` ya lista las 
variables que hará falta rellenar — pero nada de esto es todavía 
infraestructura levantable: no hay `.env` real, no hay configuración 
funcional en `docker-compose.yml`, y no hay instalación nativa documentada 
para producción. Lo que sigue es la decisión de **cómo** se desplegará cada 
base de datos cuando llegue el momento de completar esos marcadores.

### Aclaración importante: "sin desplegar" no significa lo mismo para las 
tres bases de datos

A las tres les falta la infraestructura física corriendo (contenedor 
levantado, `.env` real con credenciales) — eso es común a las tres. Pero la 
similitud termina ahí:

**PostgreSQL — activo, con código funcionando, solo falta levantarlo 
físicamente.** `backend/storage/` (los 13 módulos) ya tiene lógica real 
pensada para hablar con PostgreSQL vía SQLAlchemy. `backend/database.py` ya 
está preparado para leer credenciales de un `.env`. Los 17 archivos de 
`integration/` en `tests/` están diseñados para probar el ciclo completo 
HTTP→router→service→storage→SQLite. Si mañana se levanta el contenedor de 
PostgreSQL y se crea el `.env` real, el sistema funciona de verdad para 
todo lo relacionado con PostgreSQL — no falta nada más.

**eXist-db — candidato, sin ningún código de aplicación todavía.** 
`exist_db_client.py` no tiene lógica real, solo un comentario. Ningún 
`service` de los 16 lo llama. `test_exist_db_client.py` se omitió 
deliberadamente de la estructura de tests porque no hay nada que probar. A 
diferencia de PostgreSQL, si mañana se levanta el contenedor de eXist-db, 
**no pasa nada** — porque no existe ningún código que sepa hablar con él 
todavía. Falta, además de la infraestructura física, todo el código de 
aplicación: la lógica de `exist_db_client.py`, la llamada desde 
`validacion/` que resolvería conref/conkeyref, y los tests 
correspondientes.

**Resumen**: "PostgreSQL sin desplegar" = falta solo el último paso 
(infraestructura). "eXist-db sin activar" = falta todo (infraestructura Y 
código de aplicación) — su justificación técnica es sólida (ver sección de 
justificación de eXist-db más arriba en este documento), pero eso no 
implica que esté listo para construirse ya. Mismo criterio ya aplicado en 
el checkpoint de microservicios del curso: una justificación válida no es 
lo mismo que una necesidad medida y actual.

### PostgreSQL — decisión activa y aplicable ya

- **Desarrollo/pruebas**: contenedor Docker, mismo patrón ya practicado en 
  el curso — `fase-2-bases-de-datos` lo levantó con 
  `docker run --name ccms-postgres ...` (ver `1-README.md` de esa fase), y 
  `fase-5-herramientas-vibe-coder` movió las credenciales de `database.py` 
  a un `.env` fuera de Git (con `.env.example` como plantilla pública). 
  `backend/database.py` de esta estructura ya está pensado para leer esas 
  credenciales de un `.env` (mismo patrón). **Ya existen** el servicio 
  `postgres` en `docker-compose.yml` (imagen `postgres:16`, sin 
  configuración funcional) y `backend/.env.example` (con 
  `POSTGRES_HOST`/`PORT`/`USER`/`PASSWORD`/`DB`, valores de ejemplo 
  genéricos) — **no existe todavía** el `.env` real con credenciales, ni 
  puertos/volúmenes reales en el `docker-compose.yml`.
- **Producción**: instalación **nativa** en el servidor, no en contenedor 
  — decisión explícita del proyecto, no el valor por defecto del curso (que 
  usaba Docker sin más). PostgreSQL ya está en uso en este proyecto, así 
  que esta decisión es aplicable ya, no condicionada a nada.
- **Razón técnica**: PostgreSQL se beneficia de instalación optimizada 
  directamente sobre el sistema operativo (gestión de memoria, rendimiento 
  de E/S) frente a correr dentro de una capa de contenedor adicional en 
  producción.

### eXist-db — misma decisión de despliegue, pero sigue sin activar

Esto es una decisión de **cómo se desplegaría eXist-db si se activa en el 
futuro** — no implica activarlo ahora. `exist_db_client.py` sigue siendo 
exactamente lo que era: un archivo esqueleto marcado "candidato real, no 
activo todavía", sin lógica real ni conexión — confirmado explícitamente: 
sigue como candidato sin activar. La implementación real sigue pendiente de 
confirmar si hace falta de verdad.

- **Desarrollo/pruebas**: contenedor Docker, mismo patrón que PostgreSQL. 
  **Ya existe** el servicio `existdb` en `docker-compose.yml` (imagen 
  `existdb/existdb:6`), marcado explícitamente con el comentario 
  `# candidato, no activo` junto a su bloque — sin puertos, variables de 
  entorno ni volúmenes reales, y sin ninguna variable en 
  `backend/.env.example` todavía (no hace falta hasta que se active).
- **Producción**: instalación **nativa** en el servidor, no en contenedor 
  — misma razón técnica que PostgreSQL (gestión de memoria/E·S optimizada 
  fuera de una capa de contenedor adicional), por ser también una base de 
  datos con ese mismo perfil de carga.

### OpenSearch — confirmado, mismo criterio que PostgreSQL/eXist-db

Se preguntó explícitamente en vez de asumir: **nativo en producción**, 
igual que PostgreSQL y eXist-db — criterio uniforme para las tres bases de 
datos, no solo para las dos relacionales/XML.

- **Desarrollo/pruebas**: contenedor Docker, mismo patrón que las otras dos. 
  **Ya existen** el servicio `opensearch` en `docker-compose.yml` (imagen 
  `opensearchproject/opensearch:2`) y `OPENSEARCH_HOST`/`OPENSEARCH_PORT` 
  en `backend/.env.example` — sin puertos, credenciales ni volúmenes reales 
  todavía.
- **Producción**: instalación **nativa** en el servidor, no en contenedor 
  — misma razón técnica (rendimiento optimizado directamente sobre el 
  sistema operativo). Se descarta mantener Docker/Kubernetes en producción 
  pese a que la futura ruta de escalado (clúster con réplicas) sea 
  precisamente el escenario donde un orquestador de contenedores suele 
  preferirse por facilidad de gestión — decisión consciente, no por 
  defecto.

**Estado real de `docker-compose.yml` y `backend/.env.example` tras este 
cambio**: ambos archivos existen físicamente, con los tres servicios/
variables ya declarados como marcadores — pero ninguno es funcional 
todavía (sin puertos mapeados, sin variables de entorno reales resueltas, 
sin volúmenes, y sin `.env` real con credenciales). Levantar el entorno de 
desarrollo de verdad sigue pendiente de completar esa configuración.

## `backend/tests/` — por qué no es el patrón flat de la Fase 5

`fase-5-herramientas-vibe-coder/api/test_topics.py` bastaba con un único 
archivo: una API con 3 endpoints y un solo servicio no necesita más. Aquí 
hay 16 servicios, una capa transversal de seguridad (aislamiento por 
proyecto + RBAC + JWT) que ningún test de la Fase 5 tenía que probar, y 
autenticación federada con dos IdP — un único archivo se volvería 
inmanejable y, peor, mezclaría "¿funciona la lógica de este servicio?" con 
"¿está bloqueado el acceso indebido?" en el mismo sitio, dificultando ver 
de un vistazo si la pieza de seguridad está cubierta.

Por eso `tests/` se divide en tres categorías, no dos ni una:

```
tests/
├── conftest.py          # fixtures compartidas por toda la suite
├── pytest.ini
├── unit/                # lógica de negocio en aislamiento — storage/ mockeado
│   ├── services/         # un archivo por servicio, 1:1 con backend/services/
│   └── validacion/
├── integration/          # ciclo completo request→router→service→storage→SQLite
│   └── (un archivo por router, 1:1 con backend/routers/)
└── security/              # la capa transversal, probada aparte y con evidencia real
```

- **`unit/`**: prueba `services/` con `storage/` mockeado — sin tocar 
  ninguna base de datos, ni siquiera SQLite. Apropiado para lógica que no 
  depende de cómo se guardan los datos: la máquina de estados de workflow, 
  las reglas de RBAC, el cálculo de campos derivados del índice de 
  extracción. Existe como capa separada por dos razones concretas: 
  **rapidez** (sin engine SQLite que crear ni tablas que poblar en cada 
  test, es la capa que se ejecuta en segundos y por tanto la que se corre 
  constantemente mientras se escribe lógica de negocio) y **no depender de 
  infraestructura** (no necesita que `Base.metadata.create_all()` ni el 
  monkeypatch de `SessionLocal` de `conftest.py` funcionen para dar 
  señal — puede ejecutarse aunque la capa de persistencia esté a medio 
  construir). Un archivo por servicio, mismo nombre que en 
  `backend/services/` — misma razón de trazabilidad 1:1 ya aplicada a 
  `storage/`/`models/`/`schemas/` en el resto de este documento.
- **`integration/`**: es el patrón de la Fase 5, adaptado — `TestClient` + 
  SQLite en memoria + `monkeypatch` de `SessionLocal`, pero monkeypateando 
  **cada uno de los 13 módulos de `storage/`** (allí solo existía 
  `memory_store.py`) en vez de uno solo. Un archivo por router, prueba el 
  ciclo completo (HTTP → router → service → storage → SQLite) tal como lo 
  haría un cliente real.
- **`security/`**: **la categoría más importante de las tres**, pedida 
  explícitamente porque el aislamiento transversal (`core/proyecto_context.py`, 
  `core/seguridad.py`) no está ligado a ningún dominio concreto — mezclarlo 
  dentro de `test_tareas_api.py` o `test_servilog_api.py` lo dejaría 
  parcialmente probado en unos sitios sí y en otros no, sin que quedara 
  nunca claro si de verdad está cubierto en todas partes. Aquí se prueba 
  una vez, a fondo, con evidencia real y no solo documentada:
  - `test_proyecto_context.py`: **la pieza más crítica de toda la suite**. 
    Prueba específicamente el caso de un usuario **autenticado y con 
    permiso válido**, pero del proyecto A, intentando acceder a datos del 
    proyecto B — no el caso trivial de "sin autenticación, rechazado". Es 
    ese escenario concreto el que de verdad demuestra si el aislamiento 
    transversal funciona, porque un fallo ahí es **silencioso**: no un 
    error visible en pantalla, sino una fuga real de datos entre Navantia 
    y el uso interno de ATEXIS, indistinguible de un funcionamiento 
    correcto hasta que alguien audita el contenido devuelto. Probado a 
    través de varios routers distintos, no solo uno, para confirmar que la 
    dependencia es transversal de verdad y no una comprobación puntual en 
    un único endpoint.
  - `test_seguridad_jwt.py`: petición sin JWT, con JWT expirado, o con JWT 
    manipulado — rechazadas antes de ejecutar ninguna lógica de negocio.
  - `test_rbac_permisos.py`: una operación no permitida por el rol se 
    bloquea leyendo el catálogo real (decisión C), no una constante.
  - `test_auth_federacion.py`: `AuthFed` normaliza correctamente una 
    aserción de cualquiera de los 2 IdP, y rechaza una no reconocida.

**Lo que falta**: como el resto del proyecto en esta fase, son archivos 
con un comentario, sin lógica de test real todavía — y sin 
`test_exist_db_client.py`, porque eXist-db sigue siendo candidato sin 
activar (no tiene sentido testear una integración que aún no existe). El 
workflow de GitHub Actions para CI (ver `fase-5-herramientas-vibe-coder/
README.md` para el patrón ya practicado) queda explícitamente para cuando 
haya al menos un test real que ejecutar — no generado en esta revisión.
