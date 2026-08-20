import re

from storage import memory_store
from storage.memory_store import Topic


# Capa de lógica de negocio: aquí vive el "qué hacer", no el "cómo viaja por HTTP"
# ni el "cómo se guarda". Por eso esta capa no importa nada de FastAPI ni sabe
# qué es un código de estado 404 — eso es responsabilidad del router.
class TopicNoEncontrado(Exception):
    pass


def crear_topic(titulo: str, contenido: str) -> Topic:
    return memory_store.crear(titulo=titulo, contenido=contenido)


def listar_topics() -> list[Topic]:
    return memory_store.listar()


def mejorar_topic(topic_id: int) -> tuple[Topic, str]:
    """
    Simula la llamada a un LLM (como hace Oxygen en el flujo real) para
    sugerir una versión más legible del contenido de un topic.

    Importante: NO sobrescribe el topic guardado. Igual que un editor humano
    revisaría la sugerencia del LLM antes de aceptarla, aquí devolvemos la
    sugerencia aparte y es una decisión futura (fuera de este ejercicio)
    si se persiste o no. Guardar automáticamente lo que sugiere un modelo
    sin revisión sería una mala práctica editorial.
    """
    topic = memory_store.obtener(topic_id)
    if topic is None:
        raise TopicNoEncontrado(f"No existe ningún topic con id={topic_id}")

    contenido_mejorado = _mock_mejora_legibilidad(topic.contenido)
    return topic, contenido_mejorado


def _mock_mejora_legibilidad(texto: str) -> str:
    """
    Mock de "mejora de legibilidad" sin llamar a ningún LLM real: aplica
    limpieza de texto determinista (espacios repetidos, mayúscula inicial,
    punto final) para simular una respuesta de modelo de forma reproducible
    y sin coste ni dependencias externas.

    Cuando en una fase posterior se conecte un LLM real, esta función es
    el único punto que habría que sustituir por la llamada HTTP al modelo
    — las rutas y el resto del servicio no cambiarían.
    """
    texto = re.sub(r"\s+", " ", texto).strip()
    if not texto:
        return texto

    texto = texto[0].upper() + texto[1:]
    if texto[-1] not in ".!?":
        texto += "."

    return texto
