from fastapi import APIRouter, HTTPException

from schemas import TopicCreate, TopicOut, TopicMejoradoOut
from services import topics_service
from services.topics_service import TopicNoEncontrado

# Capa de rutas: solo traduce HTTP <-> llamadas a la capa de servicios.
# No decide reglas de negocio aquí; si algo parece "lógica" (validar,
# calcular, decidir), esa señal indica que debería vivir en services/.
router = APIRouter(prefix="/topics", tags=["topics"])


@router.post("", response_model=TopicOut, status_code=201)
def crear_topic(datos: TopicCreate) -> TopicOut:
    topic = topics_service.crear_topic(titulo=datos.titulo, contenido=datos.contenido)
    return TopicOut(id=topic.id, titulo=topic.titulo, contenido=topic.contenido)


@router.get("", response_model=list[TopicOut])
def listar_topics() -> list[TopicOut]:
    topics = topics_service.listar_topics()
    return [TopicOut(id=t.id, titulo=t.titulo, contenido=t.contenido) for t in topics]


@router.post("/{topic_id}/mejorar", response_model=TopicMejoradoOut)
def mejorar_topic(topic_id: int) -> TopicMejoradoOut:
    try:
        topic, contenido_mejorado = topics_service.mejorar_topic(topic_id)
    except TopicNoEncontrado as error:
        # Aquí es donde una excepción de dominio se traduce a un código
        # HTTP concreto (404). El servicio no sabe qué es un 404; el
        # router sí, porque es su responsabilidad hablar el idioma HTTP.
        raise HTTPException(status_code=404, detail=str(error)) from error

    return TopicMejoradoOut(
        id=topic.id,
        contenido_original=topic.contenido,
        contenido_mejorado=contenido_mejorado,
    )
