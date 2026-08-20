# Fase 1 — Backend

## Resumen

En esta fase se trabaja el desarrollo del lado servidor: cómo construir una API, gestionar rutas, peticiones y respuestas, lógica de negocio, autenticación y buenas prácticas de backend.

## Checklist de conceptos clave

- [ ] (pendiente de definir)

## Conceptos clave

### Lenguaje/framework: FastAPI
Se usa FastAPI en vez de Django (más pesado, pensado para apps con mucha UI 
server-side) o Node.js (otro ecosistema entero). FastAPI es moderno, tipado, y 
genera documentación de API automática — útil para explicar la arquitectura a 
terceros.

### Arquitectura por capas
- **Rutas/controladores**: reciben la petición HTTP, no deciden nada.
- **Lógica de negocio/servicios**: aquí vive el "qué hacer" — validar permisos, 
  aplicar reglas del workflow.
- **Acceso a datos/repositorios**: hablan con la base de datos, nada más.

Se separa así por mantenibilidad (cambiar de base de datos solo afecta a la capa 
de repositorios) y testeo (se puede probar la lógica de negocio sin BD real).

### Autenticación vs autorización
- **Autenticación** = "¿quién eres?" (login, verificar contraseña o token)
- **Autorización** = "¿qué puedes hacer, ya que sé quién eres?" (rol de autor, 
  revisor o publisher; permisos sobre un proyecto concreto)

Crítico en un CCMS: un autor no debería poder publicar directamente, un revisor 
no debería poder borrar topics de otro proyecto, etc.

### API Keys vs OAuth vs JWT
- **API Key**: clave fija que identifica a una aplicación cliente, sin usuario 
  individual detrás (así se conecta Oxygen al LLM).
- **OAuth**: protocolo para delegar acceso sin compartir contraseñas (ej. "iniciar 
  sesión con Google").
- **JWT** (JSON Web Token): token firmado que el backend entrega tras el login, 
  reenviado por el cliente en cada petición para demostrar quién es sin volver 
  a autenticarse cada vez.

Para el CCMS: probablemente API Key para la integración con Oxygen (aplicación-a-
aplicación), y JWT para sesiones de usuarios humanos en el panel de administración.

### Procesamiento asíncrono / colas de trabajo (Celery, RQ)
Una llamada al LLM o una generación de PDF puede tardar segundos o minutos. Si el 
backend espera bloqueado a que termine, la interfaz se congela y otros usuarios no 
pueden ser atendidos. Con una cola de trabajo, el backend responde de inmediato 
("tarea en proceso") y un worker separado hace el trabajo pesado en segundo plano, 
avisando cuando termina.

### Monolito vs microservicios vs "monolito modular"
Un microservicio es un sistema completo (backend propio, a veces BD propia) 
dedicado a una sola responsabilidad, comunicándose con otros por red — añade 
complejidad real (más piezas, más comunicación que puede fallar, más monitorización). 
Para un CCMS de tamaño medio, un **monolito bien modularizado** (un solo backend 
organizado internamente en módulos: autoría, workflow, publicación, búsqueda) 
casi siempre es la opción correcta. Desconfiar de quien proponga microservicios 
"porque es lo moderno" sin una razón concreta de escala o equipo.

## Ejercicio

API con FastAPI en `api/` para gestionar topics de un CCMS, organizada en capas 
(rutas / lógica de negocio / almacenamiento), con un endpoint que simula la mejora 
de legibilidad de un topic mediante un LLM.

### Por qué esta arquitectura

**Separación en tres capas (routers / services / storage).** Cada capa tiene una 
única responsabilidad y solo conoce a la capa inmediatamente inferior:

- `routers/` traduce HTTP a llamadas de Python y viceversa: recibe la petición, 
  la valida con Pydantic, llama al servicio, y convierte el resultado (o el error) 
  en una respuesta HTTP con su código de estado. No decide nada de negocio.
- `services/` contiene el "qué hacer": crear un topic, listarlos, generar la 
  sugerencia de mejora. No sabe qué es FastAPI ni qué es un código 404 — por eso, 
  cuando no encuentra un topic, lanza una excepción de Python normal 
  (`TopicNoEncontrado`) y es el router quien decide traducirla a un 404.
- `storage/` es la única capa que sabe *cómo* se guardan los datos. Hoy es un 
  diccionario en memoria; en la Fase 2, cuando se sustituya por una base de datos 
  real, en teoría solo debería cambiar este archivo — routers y services no 
  deberían enterarse de qué motor de almacenamiento hay detrás.

Esta separación es la misma idea ya apuntada en la sección "Arquitectura por capas" 
más arriba: se paga con algo más de archivos, pero a cambio cada pieza se puede 
entender, probar y cambiar por separado.

**`schemas.py` (Pydantic) separado del modelo de dominio (`storage.Topic`).** 
Aunque en este ejercicio ambos tienen los mismos campos, se mantienen como cosas 
distintas a propósito: `schemas.py` es el contrato público de la API (lo que 
viaja por HTTP), mientras que `Topic` en `storage/` es la representación interna. 
Si en el futuro se quisiera ocultar un campo interno o cambiar cómo se guarda 
sin romper el contrato de la API, esta separación ya está lista para eso.

**Almacenamiento en memoria (diccionario + contador de id).** Es intencionadamente 
lo más simple posible: nada de ficheros ni base de datos todavía, porque eso es 
justo lo que se trabajará en la Fase 2. El objetivo aquí es fijar bien la 
arquitectura por capas antes de introducir la complejidad de la persistencia real. 
Como contrapartida, los datos se pierden cada vez que se reinicia el servidor — 
es una limitación conocida y aceptada para este ejercicio.

**`POST /topics/{id}/mejorar` no sobrescribe el topic.** Se simula la respuesta 
de un LLM (sin llamar a ningún modelo real) y se devuelve como una sugerencia 
aparte (`contenido_original` + `contenido_mejorado`), sin guardarla automáticamente. 
Esto imita el flujo real de Oxygen con un LLM: el modelo sugiere, un humano revisa 
y decide si acepta el cambio — guardar automáticamente lo que sugiere un modelo 
sin revisión sería una mala práctica editorial. La función que genera la mejora 
está aislada en `services/topics_service.py` (`_mock_mejora_legibilidad`) 
precisamente para que, cuando se conecte un LLM real, sea el único punto del 
código que haya que sustituir.

### Estructura

```
fase-1-backend/api/
├── main.py                    # ensambla la app y registra los routers
├── schemas.py                 # modelos Pydantic: contrato de entrada/salida de la API
├── requirements.txt
├── routers/
│   └── topics.py              # capa HTTP: rutas /topics
├── services/
│   └── topics_service.py      # lógica de negocio (crear, listar, mejorar)
└── storage/
    └── memory_store.py        # almacenamiento en memoria (dataclass Topic + dict)
```

### Endpoints

| Método | Ruta                     | Qué hace                                                   |
|--------|--------------------------|-------------------------------------------------------------|
| POST   | `/topics`                | Crea un topic (`titulo` + `contenido`)                     |
| GET    | `/topics`                | Lista todos los topics                                     |
| POST   | `/topics/{id}/mejorar`   | Simula una mejora de legibilidad del contenido (mock LLM)  |

### Cómo levantar el proyecto en local

Desde la carpeta `fase-1-backend/api/`:

```bash
python -m venv venv
source venv/bin/activate      # en Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

La API queda disponible en `http://localhost:8000`. FastAPI genera documentación 
interactiva automática en `http://localhost:8000/docs`, donde se pueden probar 
los tres endpoints directamente desde el navegador.

Ejemplos con `curl`:

```bash
curl -X POST http://localhost:8000/topics \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Instalar el driver", "contenido": "  instalar   el driver   desde el panel  "}'

curl http://localhost:8000/topics

curl -X POST http://localhost:8000/topics/1/mejorar
```

## Preguntas frecuentes del ejercicio

### ¿Por qué necesito schemas.py si ya tengo los routers?

Son cosas distintas aunque parezca que se solapan. El router (routers/topics.py) 
define **qué URL responde a qué función** — la puerta de entrada. Pero necesita 
saber **qué forma tienen los datos** que entran y salen por esa puerta, y eso es 
lo que hace schemas.py mediante clases Pydantic:

```python
# schemas.py
from pydantic import BaseModel

class TopicCreate(BaseModel):
    titulo: str
    contenido: str

class TopicResponse(BaseModel):
    id: int
    titulo: str
    contenido: str
```

Y el router lo usa así:

```python
# routers/topics.py
@router.post("/topics", response_model=TopicResponse)
def crear_topic(topic: TopicCreate):
    ...
```

Lo que da esto gratis, sin escribir lógica manual:
1. **Validación automática**: si el JSON recibido no cumple el schema (falta un 
   campo, tipo incorrecto), FastAPI rechaza la petición con un 422 antes de que 
   el código propio se ejecute.
2. **Documentación automática**: los campos que aparecen en /docs salen 
   directamente de los schemas.
3. **Contrato separado del modelo interno**: TopicCreate (lo que se recibe) y 
   TopicResponse (lo que se devuelve) pueden diferir — por ejemplo, TopicResponse 
   incluye el id, que no existe todavía al crear. Mantener el schema público 
   separado del modelo de dominio (Topic en storage/) da libertad para que 
   evolucionen por separado.

Resumen: el router decide a dónde va la petición; el schema decide qué forma 
deben tener los datos que viajan por ahí.

### ¿Cómo se crea el "storage temporal"?

No es una base de datos ni nada especial — es una estructura de datos de Python 
que vive en la memoria del proceso mientras el servidor está corriendo 
(storage/memory_store.py):

```python
# storage/memory_store.py
from dataclasses import dataclass

@dataclass
class Topic:
    id: int
    titulo: str
    contenido: str

class MemoryStore:
    def __init__(self):
        self._topics: dict[int, Topic] = {}
        self._siguiente_id = 1

    def crear(self, titulo: str, contenido: str) -> Topic:
        topic = Topic(id=self._siguiente_id, titulo=titulo, contenido=contenido)
        self._topics[topic.id] = topic
        self._siguiente_id += 1
        return topic

    def listar(self) -> list[Topic]:
        return list(self._topics.values())
```

La clave: ese diccionario `self._topics` es una variable Python normal que vive 
en RAM mientras uvicorn está corriendo. Al parar o reiniciar el servidor, se 
destruye y todos los topics desaparecen — no hay fichero ni base de datos real 
detrás. Es deliberadamente simple para centrar el ejercicio en la arquitectura 
por capas antes de meter persistencia real. En la Fase 2, este MemoryStore se 
sustituirá por un repositorio que hable con PostgreSQL (o una BD XML nativa), 
sin que routers ni services cambien una sola línea — porque solo dependen de la 
interfaz (crear, listar), no de cómo se implementa por dentro.
