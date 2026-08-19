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

## Explicación del ejercicio

Este mini-proyecto de tres capas monta, en pequeño, el mismo esquema cliente-servidor que tendrá cualquier aplicación del curso. La capa `api/` es una aplicación FastAPI que define un único endpoint, `GET /hola`, cuya lógica es simplemente devolver el JSON `{"mensaje": "hola mundo"}`; ese código por sí solo no escucha nada de la red, solo describe qué debe pasar cuando llega esa petición. Uvicorn es quien realmente levanta un servidor y se pone a escuchar en `localhost:8000`, recibiendo las peticiones HTTP entrantes y pasándoselas a FastAPI para que las resuelva. La capa `frontend/` es un HTML sencillo con JavaScript que, al cargarse en el navegador, ejecuta un `fetch()` contra `http://localhost:8000/hola` y, cuando llega la respuesta, vuelca el mensaje recibido en la página. El flujo completo para probarlo es: instalar las librerías de `requirements.txt` → levantar el servidor con `uvicorn main:app --reload` → abrir `index.html` en el navegador (o servirlo con un servidor estático) → el JavaScript del frontend hace el `fetch()` a la API → el navegador muestra en pantalla el mensaje `hola mundo` que llegó como JSON. Es, en miniatura, la misma separación cliente/servidor que se usará en el resto del curso, solo que aquí no hay base de datos ni lógica de negocio, únicamente el "hola mundo" para ver el flujo completo funcionando de punta a punta.

## Tipos de frameworks de API y servidores

### Frameworks de API (por estilo de arquitectura)

**REST** (el usado en este curso)
- Recursos por URL, verbos HTTP, normalmente JSON.
- Ventajas: estándar universal, fácil de entender, cacheable.
- Inconvenientes: puede requerir varias llamadas para datos relacionados.

**GraphQL**
- El cliente pide exactamente los campos que necesita, un único endpoint.
- Ventajas: evita sobre/infra-fetching de datos.
- Inconvenientes: más complejo de montar y cachear.

**gRPC**
- Binario (protobuf), pensado para comunicación entre microservicios internos.
- Ventajas: rendimiento muy alto, tipado fuerte.
- Inconvenientes: no lo consume un navegador directamente, difícil de depurar.

**SOAP**
- Basado en XML, contratos formales (WSDL), común en sistemas legacy/banca/gobierno.
- Ventajas: estándares fuertes de seguridad y transacciones.
- Inconvenientes: pesado y verboso para APIs nuevas.

Frameworks REST en Python:
- **FastAPI** (usado aquí): moderno, tipado, documentación automática, asíncrono.
- **Flask**: minimalista y flexible, pero hay que añadir manualmente validación/docs.
- **Django REST Framework**: todo incluido (admin, ORM, auth), más pesado.

### Servidores

**Servidor de aplicación** (ejecuta el código Python):
- **Uvicorn** (usado aquí): ASGI, asíncrono, rápido con concurrencia.
- **Gunicorn**: WSGI, síncrono, maduro, buena gestión de múltiples procesos. 
  En producción con FastAPI se suele usar Gunicorn gestionando workers de Uvicorn.

**Servidor web / proxy inverso** (delante del servidor de aplicación):
- **Nginx**: sirve ficheros estáticos, gestiona HTTPS/seguridad, reenvía peticiones 
  dinámicas al servidor de aplicación. Eficiente con miles de conexiones.
- **Apache**: alternativa más antigua, más "todo en uno", generalmente más pesado.

Para este ejercicio local solo se usa Uvicorn — la combinación completa 
(Nginx + Gunicorn + Uvicorn) es propia de un despliegue en producción.

#### ¿Cuándo necesito Nginx/Apache delante de Uvicorn?

Para un ejercicio local como este (solo yo, en mi propia máquina), Uvicorn solo es 
suficiente — no hace falta nada más. Nginx/Apache empiezan a ser necesarios cuando 
aparece alguno de estos escenarios:

1. **Varios usuarios simultáneos** (aunque sea tráfico interno de empresa, no de 
   internet): Uvicorn solo gestiona un número limitado de conexiones eficientemente. 
   Gunicorn + varios workers de Uvicorn reparten esa carga.
2. **HTTPS**: en cuanto viajan contraseñas o datos sensibles por la red, aunque sea 
   interna, se quiere cifrado — más fácil de configurar en Nginx que en Uvicorn directo.
3. **Servir ficheros estáticos** (imágenes, CSS, JS compilado): Nginx lo hace mucho 
   más rápido que dejar que el código Python se encargue.
4. **Seguridad y control de acceso**: filtrar peticiones raras, limitar peticiones 
   por segundo, ocultar detalles internos del backend.
5. **Varios servicios detrás de una sola puerta**: si el CCMS tiene backend, buscador 
   (Elasticsearch) y LLM local en puertos distintos, Nginx puede ser el único punto 
   de entrada que decide a qué servicio va cada ruta.

Regla práctica: Uvicorn/Gunicorn solos valen para desarrollo o una app interna muy 
pequeña. En cuanto hay varios usuarios reales, HTTPS serio, estáticos que servir, 
o varios servicios que unificar, se añade Nginx/Apache delante.
