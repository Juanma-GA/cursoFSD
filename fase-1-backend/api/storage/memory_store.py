from dataclasses import dataclass


# Capa de almacenamiento: la única que sabe CÓMO se guardan los datos.
# Hoy es un diccionario en memoria; en la Fase 2 esta será la única capa
# que cambie al pasar a una base de datos real (Postgres, XML nativa...).
# Las capas de arriba (servicios, rutas) no deberían enterarse del cambio.
@dataclass
class Topic:
    id: int
    titulo: str
    contenido: str


_topics: dict[int, Topic] = {}
_next_id = 1


def crear(titulo: str, contenido: str) -> Topic:
    global _next_id
    topic = Topic(id=_next_id, titulo=titulo, contenido=contenido)
    _topics[topic.id] = topic
    _next_id += 1
    return topic


def listar() -> list[Topic]:
    return list(_topics.values())


def obtener(topic_id: int) -> Topic | None:
    return _topics.get(topic_id)
