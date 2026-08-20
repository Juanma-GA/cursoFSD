# Checkpoint Fase 0 — Flujo completo: guardar un topic en el CCMS

Resolución del checkpoint de la Fase 0: qué pasa, paso a paso, desde que un autor 
pulsa "guardar topic" hasta que el contenido queda persistido.

## El flujo

1. **Clic en el frontend.** El autor rellena un formulario (título + contenido del 
   topic) en el panel de administración del CCMS y pulsa "Guardar". Este clic dispara 
   una función JavaScript que recoge esos datos y los empaqueta en un objeto.

2. **Petición HTTP del frontend al backend.** El JavaScript usa `fetch()` para enviar 
   una petición **POST** (porque se está creando/actualizando algo, no solo leyendo) 
   a una URL del backend, por ejemplo `POST /topics`. El cuerpo va en formato **JSON**, 
   con la estructura de datos del topic (título, contenido, autor, fecha...).

3. **El backend recibe la petición.** FastAPI recibe el POST en la ruta correspondiente 
   y **valida** el JSON: comprueba que los campos obligatorios están presentes y con 
   el tipo correcto. Aquí también entra la **autorización**: ¿tiene este usuario 
   permiso de autor para guardar en este proyecto?

4. **El backend habla con la base de datos.** Ya validado, el backend usa un 
   driver/ORM (protocolo distinto de HTTP, más de bajo nivel) para ejecutar el 
   guardado real — un `INSERT` en PostgreSQL, o una operación equivalente en una 
   base XML nativa si el contenido es DITA/XML. **Aquí es donde el contenido queda 
   realmente persistido** — si el servidor se reiniciara ahora, el topic seguiría 
   existiendo.

5. **La base de datos confirma.** Responde al backend confirmando la operación (o 
   devuelve un error si algo falló, ej. una violación de restricción).

6. **El backend responde al frontend.** Construye una respuesta HTTP con un código 
   de estado (`200`/`201 Created` si fue bien; `400`/`422` si el JSON era inválido; 
   `401`/`403` si no había permiso; `500` si algo falló en el servidor) y normalmente 
   un JSON con los datos del topic ya guardado (incluyendo el ID asignado por la BD).

7. **El frontend reacciona.** El JavaScript recibe la respuesta, comprueba el código 
   de estado, y actualiza la interfaz: mensaje de éxito o error concreto según el caso.

## Piezas clave que aparecen en este flujo
- HTTP (verbo POST, código de estado, JSON como formato de datos)
- Validación y autorización en el backend
- Persistencia real en base de datos (protocolo distinto al HTTP frontend↔backend)
- Respuesta y actualización de la interfaz

## Extensión del flujo: subir un archivo .xml en vez de JSON puro

Cuando en vez de un topic en texto plano se sube un archivo (ej. un .xml DITA), 
el flujo cambia en algunos puntos:

### 1. Cómo viaja el archivo por HTTP
Un JSON no puede llevar binario de forma directa y eficiente. Se usa 
**multipart/form-data** en su lugar: un formato de cuerpo HTTP pensado para llevar 
texto y archivos combinados, cada uno como una parte independiente.

En el frontend, se usa `FormData` en vez de construir un JSON a mano:

```javascript
const formData = new FormData();
formData.append("archivo", inputFile.files[0]); // el .xml seleccionado
formData.append("titulo", "Mi topic");

fetch("http://localhost:8000/topics/upload", {
  method: "POST",
  body: formData // el navegador pone el Content-Type correcto automáticamente
});
```

### 2. Cómo lo recibe el backend
FastAPI recibe el archivo mediante un parámetro especial (`UploadFile`), que da 
acceso al contenido en bruto (bytes) y a metadatos (nombre, tipo MIME) — no es un 
campo JSON más.

### 3. Dónde y cómo se persiste (decisión de arquitectura)
Tres opciones posibles:

1. **Archivo en disco/almacenamiento + ruta en BD**: el backend escribe el .xml en 
   una carpeta o almacenamiento tipo S3, y la base de datos relacional solo guarda 
   la ruta (ej. `ruta_archivo = /storage/topics/123.xml`). Patrón más común — las 
   BD relacionales no están optimizadas para archivos grandes.
2. **BLOB en la propia base de datos**: el binario se guarda directamente en una 
   columna. Más simple y transaccional, pero menos eficiente a gran escala.
3. **Parsear y guardar estructurado (BD XML nativa)**: el backend no solo archiva 
   el .xml, sino que lo interpreta, lo valida contra un esquema DITA, y lo indexa 
   para poder consultarlo por su estructura interna. Es la opción con sentido real 
   para un CCMS — se retoma en profundidad en la Fase 2.

### Resumen del flujo con archivo
1. Frontend: FormData en vez de JSON, mismo verbo POST
2. Backend recibe el archivo como bytes/stream, lo valida (¿XML válido? ¿cumple 
   esquema DITA?)
3. Backend decide dónde persistirlo (disco+ruta, BLOB, o parseado en BD XML nativa)
4. Respuesta HTTP igual que en el flujo JSON: éxito/error + datos del topic guardado
