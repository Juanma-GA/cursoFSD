from pydantic import BaseModel


# Estos modelos Pydantic son el "contrato" de la API: lo que el cliente
# envía y lo que recibe por HTTP. Se mantienen separados del modelo de
# dominio (storage.memory_store.Topic) a propósito: la forma en la que
# viajan los datos por la red no tiene por qué coincidir siempre con la
# forma en la que se guardan internamente (por ejemplo, aquí no se expone
# ningún campo interno que en el futuro no queramos mostrar al cliente).
class TopicCreate(BaseModel):
    titulo: str
    contenido: str


class TopicOut(BaseModel):
    id: int
    titulo: str
    contenido: str


class TopicMejoradoOut(BaseModel):
    id: int
    contenido_original: str
    contenido_mejorado: str
