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
