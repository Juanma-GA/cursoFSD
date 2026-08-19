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
