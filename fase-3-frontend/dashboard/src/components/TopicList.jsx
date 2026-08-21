import TopicCard from "./TopicCard";

// TopicList: NO tiene estado propio (no hay ningún useState aquí).
//
// - DATOS DEL BACKEND: `topics` llega entero como prop desde App, que es
//   quien realmente hizo el fetch a GET /topics. TopicList no vuelve a
//   pedir nada ni transforma la lista — solo la recorre.
// - SOLO PRESENTACIÓN: este componente es 100% JSX de pintado. Su única
//   lógica es un `.map()` para convertir cada topic en un <TopicCard>, lo
//   cual sigue siendo presentación (decidir "un topic = una tarjeta"), no
//   una regla de negocio.
//
// Por qué está separado de App aunque no tenga estado: aísla "cómo se
// dibuja la lista completa" de "de dónde salen los topics y cómo se crean
// nuevos", que es responsabilidad de App.
function TopicList({ topics, cargando, error }) {
  if (cargando) {
    return <p>Cargando topics...</p>;
  }

  if (error) {
    return <p className="error">{error}</p>;
  }

  if (topics.length === 0) {
    return <p>Todavía no hay ningún topic. Crea el primero con el formulario.</p>;
  }

  return (
    <div className="topic-list">
      {topics.map((topic) => (
        <TopicCard key={topic.id} topic={topic} />
      ))}
    </div>
  );
}

export default TopicList;
