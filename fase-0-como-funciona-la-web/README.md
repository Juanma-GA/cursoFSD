# Fase 0 — Cómo funciona la web

## Resumen

En esta fase se trabaja el funcionamiento básico de la web: cómo se comunican un cliente (navegador) y un servidor, qué es una petición HTTP, qué son los verbos y códigos de estado, y cómo se estructura una aplicación en capas (frontend que consume una API backend).

## Checklist de conceptos clave

- [ ] (pendiente de definir)

## Ejercicio

Mini proyecto de tres capas: "hola mundo" servido por una API en Python (FastAPI) y consumido desde una página HTML con JavaScript mediante `fetch()`.

Estructura:

```
fase-0-como-funciona-la-web/
├── api/          # API en Python con FastAPI
│   ├── main.py
│   └── requirements.txt
└── frontend/     # página HTML + JS que consume la API
    └── index.html
```

### Cómo levantar la API

Desde la carpeta `fase-0-como-funciona-la-web/api/`:

```bash
python -m venv venv
source venv/bin/activate      # en Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

La API quedará disponible en `http://localhost:8000`. Puedes probar el endpoint directamente en el navegador o con curl:

```bash
curl http://localhost:8000/hola
# {"mensaje": "hola mundo"}
```

### Cómo levantar el frontend

Desde la carpeta `fase-0-como-funciona-la-web/frontend/`, abre `index.html` directamente en el navegador, o sirve la carpeta con un servidor estático simple:

```bash
python -m http.server 5500
```

Y visita `http://localhost:5500`. Con la API corriendo en `http://localhost:8000`, la página hará la petición y mostrará el mensaje `hola mundo` en pantalla.

> Nota: la API tiene CORS habilitado (`allow_origins=["*"]`) precisamente para permitir que el frontend, servido desde otro origen/puerto, pueda llamarla desde el navegador.

## Qué estás viendo en las DevTools

Si abres las DevTools del navegador (pestaña **Network**/Red) mientras cargas `index.html`, verás una petición a `http://localhost:8000/hola`. Esto es lo que está pasando:

- **El endpoint que se llama**: `GET http://localhost:8000/hola`. Es la URL exacta que el `fetch()` del frontend usa para pedirle datos al backend. "Endpoint" es simplemente la dirección concreta de la API que responde a esa petición.

- **Verbos HTTP**: son la "acción" que le decimos al servidor que queremos hacer. En este ejercicio usamos `GET`, que significa "quiero leer/obtener datos" (no modificamos nada en el servidor). Otros verbos comunes que verás más adelante son `POST` (crear algo nuevo), `PUT`/`PATCH` (actualizar algo existente) y `DELETE` (borrar algo).

- **Códigos de estado**: son un número que el servidor devuelve junto con la respuesta para decir cómo ha ido la petición. En las DevTools verás `200 OK`, que significa "todo ha ido bien, aquí tienes los datos". Otros códigos habituales: `404 Not Found` (esa ruta no existe), `500 Internal Server Error` (algo falló en el servidor), `400 Bad Request` (la petición estaba mal formada).

- **El cuerpo de la respuesta (Response)**: si haces clic en la petición a `/hola` dentro de la pestaña Network, en la sección "Response" verás el JSON exacto que devuelve la API: `{"mensaje": "hola mundo"}`. Ese es el dato que JavaScript recoge con `fetch(...).then(r => r.json())` y vuelca en el HTML.

## Notas y aclaraciones (repaso con dudas reales)

### FastAPI vs Uvicorn — no son lo mismo
- **FastAPI**: framework donde se define la lógica ("cuando alguien pida /hola, responde esto"). 
  Es código puro, no sabe hablar con la red por sí solo.
- **Uvicorn**: servidor ASGI, el programa que escucha peticiones de red de verdad y se las pasa 
  a FastAPI para que las procese. Sin uvicorn, el código FastAPI es solo un archivo Python que 
  no está escuchando nada.
- Analogía: FastAPI escribe el guion de qué contestar; Uvicorn es quien descuelga el teléfono.

### Instalar ≠ ejecutar
- `pip install -r requirements.txt` solo descarga las librerías. No arranca nada.
- `python -m uvicorn main:app --reload` es lo que arranca el servidor de verdad.
- `main:app` significa: "abre el archivo main.py y usa la variable `app` que hay dentro" 
  (esa variable es el objeto FastAPI con los endpoints ya definidos).

### ¿Dónde vive el servidor y por qué el puerto 8000?
- El servidor corre en tu propio ordenador mientras el proceso de uvicorn siga vivo en la terminal.
- `127.0.0.1` / `localhost` significa "esta misma máquina" — por eso solo tú puedes acceder 
  a él ahora mismo, no ha salido a internet.
- El puerto es cómo el sistema operativo distingue a qué programa va dirigida cada petición 
  de red. 8000 es solo el valor por defecto de uvicorn, no tiene nada de especial ni obligatorio.

### ¿Por qué el navegador entiende el fetch() sin instalar nada?
- Todo navegador moderno trae un motor de JavaScript incorporado de fábrica (ej. V8 en Chrome).
- HTML = estructura, CSS = estilo, JavaScript = comportamiento/lógica — las tres las entiende 
  cualquier navegador de forma nativa, sin instalación adicional.
- `fetch()` es una función que ya trae el navegador, cuya misión es hacer una petición HTTP 
  a una URL y traer la respuesta — el mismo mecanismo con el que el navegador pidió el propio 
  HTML, solo que ahora lo dispara código JS en vez de una URL tecleada a mano.

### Frontend↔Backend vs Backend↔Base de datos: NO usan el mismo "idioma"
- **Frontend ↔ Backend**: hablan por HTTP (GET, POST, JSON). Es un protocolo universal porque 
  cualquier cliente desconocido (navegador, app, Oxygen) debe poder hablar con la API sin saber 
  cómo está construida por dentro.
- **Backend ↔ Base de datos**: hablan el protocolo específico de esa base de datos, mediante 
  una librería/driver (ej. psycopg2, SQLAlchemy para PostgreSQL) — no hay verbos HTTP ni fetch(), 
  es una conexión de bajo nivel optimizada para esa tarea, no pensada para ser "universal".

### Flujo completo: guardar un topic en el CCMS
1. Frontend → Backend (HTTP POST con JSON) → "guarda este topic con este contenido"
2. Backend recibe el POST, valida el JSON
3. Backend → Base de datos (protocolo específico, ej. SQL INSERT) → aquí queda persistido de verdad
4. Backend → Frontend (respuesta HTTP 200) → "guardado correctamente"
