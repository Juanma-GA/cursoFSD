import { useEffect, useState } from "react";
import { obtenerTopics } from "./api";
import TopicForm from "./components/TopicForm";
import TopicList from "./components/TopicList";
import "./App.css";

// App: dueño del ÚNICO estado que varios componentes necesitan compartir.
//
// - ESTADO PROPIO (useState): `topics`, `cargando`, `error`. `topics` vive
//   aquí y no en TopicList porque TANTO TopicList (para pintarlo) COMO
//   TopicForm (para añadirle el topic recién creado) necesitan verlo o
//   modificarlo — es lo que en React se llama "levantar el estado" al
//   ancestro común más cercano.
// - DATOS DEL BACKEND: `topics` empieza como `[]` y se rellena de verdad
//   en el `useEffect` de abajo, con la respuesta real de GET /topics. A
//   partir de ahí ya es estado de React (se puede actualizar sin volver a
//   preguntarle al backend, como hace `handleTopicCreado`).
// - SOLO PRESENTACIÓN: el layout (<header>, <main>, dos columnas) — no
//   decide nada, solo organiza dónde va cada componente hijo.
function App() {
  const [topics, setTopics] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    obtenerTopics()
      .then(setTopics)
      .catch(() => setError("No se pudieron cargar los topics. ¿Está la API corriendo en el puerto 8000?"))
      .finally(() => setCargando(false));
  }, []);

  function handleTopicCreado(nuevoTopic) {
    // Actualiza el estado local con la respuesta del POST en vez de volver
    // a pedir la lista entera con otro GET — un topic ya lo devuelve
    // completo la propia API al crearlo.
    setTopics((topicsActuales) => [...topicsActuales, nuevoTopic]);
  }

  return (
    <>
      <header>
        <h1>CCMS — Dashboard de topics (Fase 3)</h1>
      </header>
      <main className="layout">
        <section>
          <TopicForm onTopicCreado={handleTopicCreado} />
        </section>
        <section>
          <h2>Topics</h2>
          <TopicList topics={topics} cargando={cargando} error={error} />
        </section>
      </main>
    </>
  );
}

export default App;
