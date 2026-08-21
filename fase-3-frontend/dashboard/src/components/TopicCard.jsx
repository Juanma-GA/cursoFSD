import { useState } from "react";
import { mejorarTopic } from "../api";

// TopicCard: tarjeta de un único topic.
//
// - DATOS DEL BACKEND (llegan como prop `topic`, no se generan aquí):
//   topic.id, topic.titulo, topic.contenido — vinieron de GET /topics en
//   el componente padre (TopicList/App) y solo se leen en este componente.
//
// - ESTADO PROPIO (useState, vive y muere en esta tarjeta):
//   `sugerencia` y `mejorando` no existen en el backend ni en ningún otro
//   componente — son el resultado transitorio de pulsar "Mejorar" en ESTA
//   tarjeta concreta. Por eso viven aquí y no en App: ninguna otra parte
//   de la interfaz necesita saber si esta tarjeta está mostrando o no una
//   sugerencia.
//
// - SOLO PRESENTACIÓN (JSX que pinta, sin decidir nada):
//   el <article>, los <h3>/<p>, el botón — solo muestran lo que ya está en
//   props/estado, no calculan ni transforman datos.
function TopicCard({ topic }) {
  const [sugerencia, setSugerencia] = useState(null);
  const [mejorando, setMejorando] = useState(false);
  const [error, setError] = useState(null);

  async function handleMejorar() {
    setMejorando(true);
    setError(null);
    try {
      const resultado = await mejorarTopic(topic.id);
      setSugerencia(resultado.contenido_mejorado);
    } catch {
      setError("No se pudo generar la sugerencia. ¿Está la API corriendo?");
    } finally {
      setMejorando(false);
    }
  }

  return (
    <article className="topic-card">
      <h3>{topic.titulo}</h3>
      <p>{topic.contenido}</p>

      <button onClick={handleMejorar} disabled={mejorando}>
        {mejorando ? "Generando sugerencia..." : "Mejorar con IA (mock)"}
      </button>

      {sugerencia && (
        <div className="topic-card__sugerencia">
          <strong>Sugerencia (no guardada automáticamente):</strong>
          <p>{sugerencia}</p>
        </div>
      )}

      {error && <p className="topic-card__error">{error}</p>}
    </article>
  );
}

export default TopicCard;
