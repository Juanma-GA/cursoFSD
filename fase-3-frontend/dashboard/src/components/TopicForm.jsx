import { useState } from "react";
import { crearTopic } from "../api";

// TopicForm: formulario para crear un topic (POST /topics).
//
// - ESTADO PROPIO (useState): `titulo` y `contenido` son un ejemplo clásico
//   de "estado de formulario" — lo que el usuario va escribiendo antes de
//   enviarlo, no existe todavía en el backend. `enviando` y `error` también
//   son estado local: reflejan qué está pasando con ESTE envío concreto.
// - DATOS DEL BACKEND: aquí no se reciben por props — este componente es
//   quien los ENVÍA (crea el dato nuevo), por eso usa `crearTopic` en vez
//   de recibir datos ya cargados.
// - SOLO PRESENTACIÓN: los <input>/<textarea>/<button> — pintan el valor
//   actual del estado y notifican cambios, sin decidir nada por su cuenta.
//
// Al terminar con éxito, avisa al padre (`onTopicCreado`) para que App
// actualice la lista — TopicForm no sabe ni le importa cómo se muestra la
// lista de topics, solo que "se creó uno nuevo".
function TopicForm({ onTopicCreado }) {
  const [titulo, setTitulo] = useState("");
  const [contenido, setContenido] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(evento) {
    evento.preventDefault();
    setEnviando(true);
    setError(null);
    try {
      const nuevoTopic = await crearTopic(titulo, contenido);
      onTopicCreado(nuevoTopic);
      setTitulo("");
      setContenido("");
    } catch {
      setError("No se pudo crear el topic. ¿Está la API corriendo?");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form className="topic-form" onSubmit={handleSubmit}>
      <h2>Nuevo topic</h2>

      <label>
        Título
        <input
          type="text"
          value={titulo}
          onChange={(evento) => setTitulo(evento.target.value)}
          required
        />
      </label>

      <label>
        Contenido
        <textarea
          value={contenido}
          onChange={(evento) => setContenido(evento.target.value)}
          required
        />
      </label>

      <button type="submit" disabled={enviando}>
        {enviando ? "Guardando..." : "Crear topic"}
      </button>

      {error && <p className="topic-form__error">{error}</p>}
    </form>
  );
}

export default TopicForm;
