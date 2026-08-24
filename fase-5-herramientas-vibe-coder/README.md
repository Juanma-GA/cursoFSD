# Fase 5 — Herramientas / vibe coder

## Resumen

En esta fase se trabaja el uso de herramientas modernas de desarrollo asistido por IA (vibe coding): asistentes de código, flujos de trabajo con IA, prompting efectivo y buenas prácticas al programar con estas herramientas.

## Checklist de conceptos clave

- [ ] (pendiente de definir)

## Conceptos clave

### Control de versiones con Git/GitHub
Ya practicado extensamente: ramas de feature, pull requests, merges, y 
resolución de un problema real de configuración (rama "default" mal 
establecida en el repo, corregida en fase-1-backend). El porqué de fondo — 
por qué no se trabaja directo sobre main en un proyecto real — se vivió de 
primera mano: cada PR dio la oportunidad de revisar un diff antes de 
integrarlo, separando "trabajo en progreso" de "lo que ya funciona y está 
validado".

### Docker
También practicado en profundidad: contenedor ccms-postgres, pgAdmin, y 
resolución de un problema real de red entre contenedores 
(host.docker.internal). El concepto de fondo — "funciona en mi máquina" deja 
de ser un problema — se confirmó al comprobar que el backend habla igual con 
PostgreSQL esté donde esté corriendo (nativo o en Docker), porque el 
contenedor aísla el entorno.

### Variables de entorno y gestión de secretos
Contenido nuevo a resolver en el ejercicio práctico: actualmente database.py 
tiene la contraseña de PostgreSQL escrita directamente en el código 
(hardcodeada) — se corrige moviendo las credenciales a un archivo separado 
que nunca se sube a Git.

### Testing básico
Contenido completamente nuevo. Un test unitario es código que verifica 
automáticamente que otro código hace lo que se espera, sin probarlo a mano 
cada vez (a diferencia de las pruebas manuales hechas hasta ahora vía 
Swagger UI o curl). Un CCMS con lógica de workflow (estados, permisos, 
versionado) los necesita porque un cambio pequeño en un sitio puede romper 
una regla de negocio en otro sin que se note a simple vista.

### CI/CD (nivel conceptual, con práctica ligera)
"Desplegar automáticamente" significa que, al subir código a main, un 
sistema externo (no manualmente) ejecuta pasos predefinidos — típicamente: 
correr los tests, y si pasan, desplegar la nueva versión. Reduce errores 
humanos porque elimina el paso "me acordé de probarlo antes de subirlo" — el 
sistema lo hace siempre, sin excepción.

#### Aclaración: qué significan CI y CD exactamente

**CI = Continuous Integration (Integración Continua).** Cada vez que se sube 
código (vía PR o push), un sistema automático construye e integra ese código 
con el resto del proyecto, y ejecuta comprobaciones (tests, linters) para 
detectar problemas cuanto antes — antes de que ese código se mezcle de 
verdad con el trabajo de los demás. En vez de integrar todo el trabajo de 
golpe tras semanas aisladas (con conflictos masivos), se integra 
constantemente, en piezas pequeñas, detectando roturas al momento.

**CD tiene dos significados distintos:**
- **Continuous Delivery (Entrega Continua)**: el código, tras pasar todos 
  los checks automáticos, queda listo para desplegarse en cualquier 
  momento — pero el despliegue final a producción sigue siendo una decisión 
  humana.
- **Continuous Deployment (Despliegue Continuo)**: un paso más allá — si 
  todo pasa los checks automáticos, se despliega a producción sin 
  intervención humana.

**Alcance de este ejercicio**: se implementa solo la parte de CI (ejecutar 
tests automáticamente en cada push) — la parte de CD no aplica todavía 
porque no existe ningún servidor de producción desplegado, solo el entorno 
local. Es un matiz importante: "CI/CD" se suele decir como una sola cosa, 
pero en este proyecto, por ahora, solo se implementa la mitad (CI).

## Ejercicio

### Variables de entorno: sacar las credenciales de PostgreSQL del código

Primer paso práctico de esta fase: corregir que `api/database.py` tuviera 
las credenciales de PostgreSQL escritas directamente en el código.

**Antes:**
```python
DATABASE_URL = "postgresql+psycopg2://postgres:curso123@localhost:5432/ccms"
```
La contraseña real (`curso123`) quedaba visible en el código fuente, y por 
tanto en el historial de Git en cuanto se hiciera commit — cualquiera con 
acceso al repositorio (o a una copia pública de él) vería la contraseña de 
la base de datos.

**Después:**
```python
load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
```
Las credenciales ahora viven en un archivo `.env` (fuera de Git), leído en 
tiempo de ejecución con `python-dotenv`. El código ya no contiene ningún 
valor real — solo los nombres de las variables que necesita.

### Por qué `.env` nunca debe subirse a Git, pero `.env.example` sí

- **`.env`**: contiene las credenciales reales (usuario, contraseña, host, 
  puerto, nombre de la base de datos) del entorno de quien lo creó. Si se 
  sube a Git, esas credenciales quedan expuestas para siempre en el 
  historial del repositorio, aunque después se borre el archivo — un 
  `git log`/`git show` de un commit antiguo las seguiría mostrando. Por eso 
  se añade a `.gitignore`: Git lo ignora por completo, nunca llega a 
  proponerse en un commit.
- **`.env.example`**: contiene los mismos nombres de variable, pero con 
  valores de ejemplo genéricos (`tu_usuario`, `tu_password`...), sin ningún 
  dato real. Este archivo sí se sube a Git, precisamente para que cualquiera 
  que clone el repositorio sepa qué variables de entorno necesita crear en 
  su propio `.env` local, sin exponer las credenciales de nadie.

### Verificación

Se instaló `python-dotenv`, se creó `api/.env` con las credenciales reales, 
se creó `api/.env.example` con valores de ejemplo, y se añadió `api/.gitignore` 
con la entrada `.env`. Se levantó el servidor (`uvicorn main:app`) y se 
comprobó que sigue conectando correctamente a PostgreSQL y sirviendo 
`/topics` con datos reales, exactamente igual que antes del cambio — el 
único comportamiento distinto es de dónde vienen las credenciales, no cómo 
funciona la conexión.

### Tests con pytest para la API de topics

Se añadió `api/test_topics.py` con 4 tests sobre los endpoints de `/topics`, 
usando `pytest` y el `TestClient` de FastAPI (basado en `httpx`).

**Cómo ejecutarlos:**
```bash
cd fase-5-herramientas-vibe-coder/api
python3 -m pytest -v
```

**Qué verifica cada test:**
- `test_crear_topic_devuelve_201_con_id_asignado`: hace `POST /topics` y 
  comprueba que responde 201 con un `id` asignado y el `titulo`/`contenido` 
  enviados.
- `test_listar_topics_incluye_el_topic_recien_creado`: crea un topic y 
  comprueba que `GET /topics` lo incluye en la lista devuelta.
- `test_mejorar_topic_existente_devuelve_sugerencia`: crea un topic y llama 
  a `POST /topics/{id}/mejorar`, comprobando que devuelve 200 con el 
  contenido original y una sugerencia mejorada (limpieza de espacios, 
  mayúscula inicial, punto final — ver `_mock_mejora_legibilidad` en 
  `services/topics_service.py`).
- `test_mejorar_topic_inexistente_devuelve_404`: llama a 
  `POST /topics/999999/mejorar` (un id que no existe) y comprueba que 
  responde 404. Nota: actualmente no existe un endpoint `GET /topics/{id}` 
  individual (solo `GET /topics` en lista) — el único endpoint que trata un 
  id inexistente como error es `mejorar`, así que es el que se usa para 
  probar el caso 404.

### Estrategia de base de datos para los tests

Los tests usan **SQLite en memoria** (`sqlite:///:memory:`), no la 
PostgreSQL real de Docker (`ccms`).

Cómo se consigue sin tocar el código de producción: `storage/memory_store.py` 
hace `from database import SessionLocal` al importarse — no usa el sistema 
de dependencias de FastAPI (`Depends`) para inyectar la sesión de base de 
datos, la importa directamente. Por eso, en un *fixture* de pytest, se crea 
un engine y una `sessionmaker` de SQLite en memoria, se crean las 9 tablas 
en él (`Base.metadata.create_all`), y se sustituye en caliente 
`memory_store.SessionLocal` por esa fábrica de sesiones de test 
(`monkeypatch.setattr`) antes de cada test — el código de `main.py`, 
`routers/` y `services/` no se entera del cambio, sigue llamando a 
`memory_store` exactamente igual.

**Por qué SQLite en memoria y no una PostgreSQL de test separada:**
- **Velocidad y aislamiento total**: cada test crea su propia base de datos 
  vacía en memoria (fixture con scope de función) y la descarta al 
  terminar — no hay estado compartido entre tests, ni riesgo de que el 
  orden de ejecución afecte al resultado, ni necesidad de limpiar filas a 
  mano.
- **No depende de que Docker esté levantado**: los tests pasan igual esté o 
  no corriendo el contenedor `ccms-postgres` — de hecho, se comprobó que los 
  4 tests pasan con el servicio de PostgreSQL completamente parado. Esto 
  importa especialmente de cara a CI (ver sección de CI/CD más abajo): un 
  runner de GitHub Actions no tiene por qué tener PostgreSQL preinstalado ni 
  levantar un contenedor extra solo para poder ejecutar los tests.
- **Nunca hay riesgo de tocar datos reales**: al ser una base de datos 
  completamente distinta (no la `ccms` de Docker), es estructuralmente 
  imposible que un test borre o corrompa contenido real por error.
- **Por qué es aceptable aquí**: el esquema de este proyecto 
  (`objetos_contenido`, `revisiones`, etc.) usa tipos de columna genéricos 
  (`Integer`, `String`, `Text`, `DateTime`, claves foráneas) sin nada 
  específico de PostgreSQL (sin `JSONB`, arrays, `ILIKE`...), así que SQLite 
  se comporta de forma equivalente para lo que estos tests comprueban. Si en 
  el futuro se usara alguna función específica de PostgreSQL, ahí sí haría 
  falta una PostgreSQL de test separada (o Docker en el propio CI) para que 
  los tests reflejen fielmente el comportamiento real.

### Aclaración: cómo se aísla la base de datos de test (con analogía)

Los tests no copian ni usan ningún dato de la PostgreSQL real de Docker — 
empiezan con una base de datos completamente vacía y nueva, creada desde 
cero en cada ejecución. Cada test crea sus propios datos de prueba (ej. un 
POST /topics con datos inventados), igual que se haría a mano con Swagger — 
esto es intencionado: un test no debe depender de qué datos existan en el 
Docker real en ese momento.

**Dónde vive esa base de datos**: `sqlite:///:memory:` vive en la RAM del 
propio proceso de pytest, igual que MemoryStore (Fase 1) vivía en la RAM de 
uvicorn — no hay ningún archivo en disco ni conexión a Docker. Al terminar 
el test, esa base de datos desaparece por completo.

**Analogía del mecanismo (monkeypatch)**: main.py/routers/services son como 
un electricista que siempre enchufa su taladro al mismo enchufe de pared 
(SessionLocal, la conexión a la base de datos) — no sabe ni le importa de 
dónde viene la corriente. Para los tests, en vez de recablear la casa 
entera (reescribir el código de producción), se desconecta momentáneamente 
ese enchufe de la red real y se conecta a una pila portátil (SQLite en 
memoria) — el electricista sigue enchufando su taladro exactamente igual, 
sin enterarse del cambio.

**El mecanismo técnico real, paso a paso:**
1. `storage/memory_store.py` hace `from database import SessionLocal` al 
   importarse — obtiene la "fábrica de conexiones" desde database.py.
2. Normalmente esa SessionLocal apunta a PostgreSQL real (Docker).
3. En el test, antes de ejecutar cualquier petición de prueba, se crea una 
   SessionLocal distinta, apuntando a SQLite en memoria.
4. `monkeypatch.setattr(memory_store, "SessionLocal", session_local_de_test)` 
   sustituye temporalmente esa variable, solo durante ese test.
5. Cuando el test hace POST /topics, la petición pasa por 
   routers → services → storage/memory_store.py, que llama a SessionLocal() 
   como siempre — solo que ahora, por el monkeypatch, apunta a la base de 
   datos temporal en RAM.

**Por qué es mejor que modificar database.py a mano**: nunca se toca ni un 
carácter del código de producción — el cambio ocurre completamente desde el 
archivo de test, y se deshace automáticamente al terminar cada test 
(monkeypatch de pytest revierte el cambio solo). Como storage/ es la única 
pieza que habla con la base de datos, es la única pieza que hace falta 
redirigir para testear.

### Cómo se ve un test que pasa frente a uno que falla

Se rompió deliberadamente `test_crear_topic_devuelve_201_con_id_asignado` 
(comprobando un título distinto al que realmente se envía) para ver la 
salida de un fallo real, y después se corrigió de vuelta.

**Salida con el test roto (`1 failed, 3 passed`):**
```
test_topics.py::test_crear_topic_devuelve_201_con_id_asignado FAILED     [ 25%]
test_topics.py::test_listar_topics_incluye_el_topic_recien_creado PASSED [ 50%]
test_topics.py::test_mejorar_topic_existente_devuelve_sugerencia PASSED  [ 75%]
test_topics.py::test_mejorar_topic_inexistente_devuelve_404 PASSED       [100%]

=================================== FAILURES ===================================
________________ test_crear_topic_devuelve_201_con_id_asignado _________________

client = <starlette.testclient.TestClient object at 0x7f052db70090>

    def test_crear_topic_devuelve_201_con_id_asignado(client):
        respuesta = client.post(
            "/topics",
            json={"titulo": "Instalar el driver", "contenido": "Pasos para instalar el driver."},
        )

        assert respuesta.status_code == 201
        datos = respuesta.json()
        assert datos["id"] is not None
>       assert datos["titulo"] == "Un título completamente distinto"
E       AssertionError: assert 'Instalar el driver' == 'Un título co...ente distinto'
E
E         - Un título completamente distinto
E         + Instalar el driver

test_topics.py:57: AssertionError
=========================== short test summary info ============================
FAILED test_topics.py::test_crear_topic_devuelve_201_con_id_asignado - Assert...
==================== 1 failed, 3 passed, 1 warning in 0.74s ====================
```
pytest señala exactamente qué test falló, en qué línea, y muestra un diff 
(`-`/`+`) entre lo esperado y lo recibido — no hace falta añadir ningún 
`print()` manual para depurarlo.

**Salida tras corregir el test (`4 passed`):**
```
test_topics.py::test_crear_topic_devuelve_201_con_id_asignado PASSED     [ 25%]
test_topics.py::test_listar_topics_incluye_el_topic_recien_creado PASSED [ 50%]
test_topics.py::test_mejorar_topic_existente_devuelve_sugerencia PASSED  [ 75%]
test_topics.py::test_mejorar_topic_inexistente_devuelve_404 PASSED       [100%]

========================= 4 passed, 1 warning in 0.63s =========================
```
Un test que pasa no imprime nada de contexto adicional — solo `PASSED` y el 
resumen final; el detalle (traceback, diff) solo aparece cuando algo falla.

### Aclaración: cómo leer la salida de un test que falla, línea por línea

**Resumen rápido por test**: cada línea (`FAILED`/`PASSED`) indica de un 
vistazo cuál test tiene el problema, sin necesidad de leer nada más si solo 
se quiere saber si algo falló.

**El código del test con el fallo señalado**: pytest muestra el test 
completo, con un símbolo `>` justo antes de la línea exacta donde ocurrió el 
fallo — las líneas anteriores (ej. `status_code == 201`) sí pasaron, solo 
esa línea concreta falló.

**El diff (la parte más útil)**:
```
E - Un título completamente distinto
E + Instalar el driver
```
El `-` es lo que el test esperaba (lo escrito en el assert); el `+` es lo 
que realmente devolvió la API. En este ejemplo concreto, la API funcionó 
correctamente — el error estaba en el test (esperaba algo incorrecto a 
propósito para esta demostración), no en el código de producción.

**El resumen final** (`1 failed, 3 passed, 1 warning in 0.74s`): útil con 
muchos tests, sin necesidad de leer cada detalle para saber el resultado 
global.

**Cuando el test se corrige**, la salida se reduce a solo PASSED por cada 
test, sin ningún detalle adicional — pytest solo se vuelve verboso cuando 
algo falla, porque solo entonces hay algo que explicar.

**La ventaja frente a depurar a mano**: no hace falta ningún print() ni 
comparar visualmente en Swagger si algo "se ve bien" — pytest da 
automáticamente la línea exacta, el valor esperado, y el valor real, uno al 
lado del otro.

### CI: workflow de GitHub Actions que ejecuta los tests automáticamente

Se añadió `.github/workflows/tests.yml` en la raíz del repositorio: un 
workflow de GitHub Actions que ejecuta los 4 tests de pytest en cada push a 
`main` (y en cada pull request contra `main`), sin intervención manual — la 
pieza de CI descrita conceptualmente más arriba, ahora implementada de 
verdad.

**No hace falta levantar ningún servicio de base de datos**: el workflow no 
incluye ningún bloque `services:` de PostgreSQL. Como los tests usan SQLite 
en memoria (ver "Estrategia de base de datos para los tests" más arriba), 
todo lo que necesitan ya está disponible con solo instalar 
`requirements.txt` — no hay que levantar un contenedor Docker de PostgreSQL 
dentro del runner, ni esperar a que esté listo, ni configurar credenciales 
de test en secrets de GitHub. Si los tests dependieran de PostgreSQL real, 
el workflow necesitaría bastante más: un bloque `services:` con la imagen 
de `postgres`, variables de entorno con las credenciales de esa base de 
datos de test, y probablemente un paso de espera activa hasta que el 
servicio esté listo para aceptar conexiones — nada de eso hace falta aquí.

### Fallo real de CI y su corrección: create_engine() sin variables de entorno

La primera ejecución del workflow falló con 
`ValueError: invalid literal for int() with base 10: 'None'` dentro de 
`database.py`. Causa: `.env` está en `.gitignore` a propósito (nunca se sube 
a Git — ver la sección de variables de entorno más arriba), así que en el 
runner de GitHub Actions no existe ningún `.env`, y 
`os.getenv("POSTGRES_PORT")` devolvía `None` — `create_engine()` fallaba al 
intentar construir la URL de conexión con un puerto `None`.

**Solución aplicada**: valores por defecto en `database.py`, con 
`os.getenv("VAR", "valor_por_defecto")` en vez de `os.getenv("VAR")`:
```python
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "ccms")
```
No se tocó `tests.yml` con un bloque `env:` adicional — solo se aplicó la 
opción de los valores por defecto en `database.py`, por dos razones:
- Es una única fuente de verdad: si mañana se renombra o se añade una 
  variable, solo hay que tocar `database.py`, no mantener sincronizados dos 
  sitios (el código y el workflow) con los mismos nombres de variable.
- Arregla el problema en cualquier entorno sin `.env`, no solo en GitHub 
  Actions — por ejemplo, si alguien clona el repo y ejecuta los tests antes 
  de crear su propio `.env`, ya no falla igual.

Esos valores por defecto (`localhost`, `postgres`/`postgres`, `ccms`) **no 
son las credenciales reales** del contenedor Docker (`curso123`) — son 
valores genéricos que solo sirven para que `create_engine()` pueda 
construir la cadena de conexión sin lanzar una excepción al importar el 
módulo. `create_engine()` no conecta de verdad en ese momento (SQLAlchemy 
crea el engine de forma perezosa, sin abrir conexión hasta que se usa), y 
en los tests nunca llega a usarse esa conexión real de todos modos: 
`test_topics.py` sustituye `SessionLocal` por SQLite en memoria vía 
`monkeypatch` antes de que se ejecute ninguna petición (ver "Estrategia de 
base de datos para los tests" más arriba) — por eso unos valores por 
defecto que no apuntan a nada real son suficientes.

**Verificación en local**: se confirmó que, con el `.env` real presente, 
`DATABASE_URL` sigue construyéndose con las credenciales reales de Docker 
exactamente igual que antes del cambio, y los 4 tests siguen pasando. 
Simulando además el escenario de CI (renombrando `.env` temporalmente para 
que no exista, y devolviéndolo a su sitio después), `DATABASE_URL` se 
construye con los valores por defecto sin lanzar ningún error, y los 4 
tests también pasan — sin necesitar Docker ni PostgreSQL real corriendo en 
ningún caso. El `.env` real no se modificó ni se subió a Git en ningún 
momento de esta corrección.

### Aclaración: por qué os.getenv(..., "valor") arregla esto

`os.getenv("NOMBRE")`, con un solo argumento, significa "busca esta 
variable, y si no existe, devuelve None". En la máquina local, con .env 
presente, esto funciona sin problema. En GitHub Actions, sin .env, devuelve 
literalmente None — y más adelante, cuando SQLAlchemy intenta convertir el 
puerto a número con `int(components["port"])`, falla porque no se puede 
convertir None a entero (de ahí el error `invalid literal for int() with 
base 10: 'None'`).

`os.getenv("NOMBRE", "valor_por_defecto")`, con un segundo argumento, 
significa "si no existe, usa este valor de repuesto en vez de devolver 
None". Con esto, en GitHub Actions, POSTGRES_PORT pasa a valer "5432" (texto 
válido, convertible a número) en vez de None.

### El valor por defecto es arbitrario — solo evita el None, la conexión nunca se usa

Estos valores (`localhost`, `5432`, `postgres`...) no necesitan ser 
"correctos" ni funcionales de verdad: `create_engine()` en SQLAlchemy es 
"perezoso" (lazy) — solo construye el objeto que describe cómo conectarse, 
sin abrir ninguna conexión real hasta que alguien ejecuta una consulta. Como 
`monkeypatch` sustituye `SessionLocal` por SQLite antes de que cualquier 
test dispare una consulta, ese engine de PostgreSQL con credenciales de 
relleno nunca llega a usarse — es un objeto construido pero nunca conectado.

Por qué usar valores "con sentido" en vez de texto aleatorio, aunque no sea 
obligatorio: legibilidad (se explican solos a quien lea el código sin 
contexto), y un mejor mensaje de error si por accidente alguien intentara 
usar ese engine de verdad fuera de tests (fallaría con un error de conexión 
claro, no con una confusión de tipos). Matiz técnico real: el puerto 
específicamente debe ser algo convertible a número con int() — un valor 
como "xyz123" fallaría igual que None. El resto de valores (host, usuario, 
contraseña, nombre de BD) sí podrían ser prácticamente cualquier texto sin 
romper nada, porque no pasan por esa conversión numérica.

### Cómo ver este workflow ejecutándose en GitHub

1. En la página del repositorio en GitHub, la pestaña **Actions** está en 
   la barra superior, junto a "Code", "Issues", "Pull requests"... — es la 
   pestaña donde GitHub lista todas las ejecuciones de workflows.
2. Cada push a `main` (o cada pull request contra `main`) aparece ahí como 
   una fila nueva, con el mensaje del commit, cuándo se ejecutó, y un 
   icono de estado:
   - 🟢 **Verde (check)**: todos los tests pasaron.
   - 🔴 **Rojo (cruz)**: al menos un test falló, o el workflow no pudo 
     completarse (ej. un error instalando dependencias).
   - 🟡 **Amarillo (círculo)**: la ejecución está en curso todavía.
3. Ese mismo icono aparece también junto al commit en el historial normal 
   de commits, y junto al pull request si el push viene de uno — no hace 
   falta entrar en Actions para tener una primera señal de si algo falló.
4. **Para ver el detalle si algo falla**: clic en la ejecución concreta 
   (dentro de la pestaña Actions) → clic en el job `pytest` → se despliega 
   la lista de pasos (Checkout, Instalar Python, Instalar dependencias, 
   Ejecutar tests) y se puede expandir cada uno. El paso "Ejecutar tests 
   con pytest" muestra la misma salida que se vería en local (`FAILED`/
   `PASSED`, el diff con `-`/`+`, la línea exacta del fallo) — exactamente 
   el mismo formato ya explicado más arriba, solo que ejecutado por GitHub 
   en vez de en la propia máquina.

## Checkpoint resuelto: desplegar y aislar el LLM local

Pregunta del checkpoint: ¿cómo explicarle a IT de ATEXIS, en sus términos, 
cómo se desplegaría y aislaría el componente del LLM local?

Un .env resuelve solo una pieza (dónde guardar credenciales sin exponerlas 
en el código) — la pregunta real de IT es más amplia: dónde vive físicamente 
el LLM, qué recursos necesita, y cómo se evita que un fallo ahí afecte al 
resto del sistema.

### 1. Dónde corre: contenedor Docker dedicado

El LLM local se empaqueta en su propia imagen Docker, corriendo en un 
contenedor separado del backend FastAPI — mismo patrón ya usado con 
ccms-postgres. Diferencia real: este contenedor necesita acceso a GPU 
(recursos de hardware específicos), la razón técnica identificada en la 
Fase 4 de por qué vive separado del backend.

### 2. Qué pasa si falla, se satura, o hay que actualizarlo

Al vivir en su propio contenedor:
- IT puede reiniciarlo, actualizarlo, o moverlo de servidor sin tocar el 
  backend ni la base de datos.
- Si se cae, el resto del CCMS (crear topics, listar, workflow) sigue 
  funcionando — solo falla la función de "mejorar con IA", degradación 
  aislada, no caída total.
- Puede escalar de forma independiente (más VRAM, más instancias) sin 
  replicar todo el backend.

### 3. Aislamiento de red y seguridad (residencia de datos)

El requisito "los datos no salen de España" se traduce en: el contenedor del 
LLM no tiene salida a internet — solo acepta conexiones desde el backend, en 
la misma red interna/privada de Docker (o de la infraestructura de ATEXIS), 
sin ninguna ruta hacia servicios externos. Se configura explícitamente 
(reglas de red de Docker, o firewall de la máquina), no es un comportamiento 
por defecto.

### 4. Credenciales y configuración

La URL interna del LLM y cualquier clave de API interna entre backend y LLM 
viven en variables de entorno (.env), nunca hardcodeadas — mismo patrón 
practicado en esta fase con las credenciales de PostgreSQL. En un entorno 
corporativo real, estas credenciales probablemente vivirían en un gestor de 
secretos centralizado (Vault, o el que use la organización), no en un .env 
suelto por servidor — ampliación mencionada en la teoría de seguridad de la 
Fase 4.

### Resumen para IT

"El LLM corre en su propio contenedor Docker, separado del backend, con 
acceso a GPU dedicada. Solo acepta conexiones desde la red interna donde 
vive el backend, sin salida a internet — así se garantiza que los datos no 
salen de España. Si el LLM falla o necesita actualizarse, se reinicia o 
reemplaza sin afectar al resto del CCMS, porque el backend le habla a través 
de una API interna, no está integrado en el mismo proceso. Las credenciales 
de esa comunicación interna viven en variables de entorno, nunca en el 
código."
