// Capa de acceso a la API: el único archivo que sabe la URL del backend y
// usa fetch() directamente. Mismo motivo que separar storage/ en el backend
// (Fase 1): si mañana cambia la URL, el puerto, o cómo se autentica la
// petición, solo hay que tocar este archivo — los componentes no llaman a
// fetch() nunca directamente, llaman a estas funciones.
const API_URL = "http://localhost:8000";

export async function obtenerTopics() {
  const respuesta = await fetch(`${API_URL}/topics`);
  if (!respuesta.ok) {
    throw new Error("No se pudieron cargar los topics");
  }
  return respuesta.json();
}

export async function crearTopic(titulo, contenido) {
  const respuesta = await fetch(`${API_URL}/topics`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ titulo, contenido }),
  });
  if (!respuesta.ok) {
    throw new Error("No se pudo crear el topic");
  }
  return respuesta.json();
}

export async function mejorarTopic(id) {
  const respuesta = await fetch(`${API_URL}/topics/${id}/mejorar`, {
    method: "POST",
  });
  if (!respuesta.ok) {
    throw new Error("No se pudo generar la sugerencia de mejora");
  }
  return respuesta.json();
}
