from dataclasses import dataclass
from datetime import datetime

from database import SessionLocal
from models import Autor, ObjetoContenido, Revision

# Capa de almacenamiento: la única que sabe CÓMO se guardan los datos.
# Desde la Fase 2 habla con PostgreSQL en vez de un diccionario en memoria,
# pero mantiene exactamente la misma interfaz (crear, listar, obtener) que
# ya usaban routers/ y services/ en la Fase 1 -- por eso esos archivos no
# han necesitado ningún cambio al migrar de almacenamiento. El nombre del
# archivo se mantiene (memory_store.py) precisamente para no tocar los
# imports de services/topics_service.py.


@dataclass
class Topic:
    id: int
    titulo: str
    contenido: str


# La Fase 1 no tiene login ni gestión de autores todavía, pero el esquema
# exige un autor_id en cada revisión (ver construccion_esquema_bd.md). Se usa
# un autor de prueba fijo hasta que la fase de autenticación lo sustituya.
_AUTOR_POR_DEFECTO_NOMBRE = "Autor de prueba"
_AUTOR_POR_DEFECTO_EMAIL = "autor.prueba@ccms.local"


def _obtener_autor_por_defecto(db) -> Autor:
    autor = db.query(Autor).filter_by(email=_AUTOR_POR_DEFECTO_EMAIL).first()
    if autor is None:
        autor = Autor(nombre=_AUTOR_POR_DEFECTO_NOMBRE, email=_AUTOR_POR_DEFECTO_EMAIL)
        db.add(autor)
        db.flush()
    return autor


def _a_topic(db, objeto: ObjetoContenido) -> Topic:
    # El contenido nunca vive en objetos_contenido: se lee siempre de la
    # revisión más reciente de ese objeto (última fila insertada).
    ultima_revision = (
        db.query(Revision)
        .filter_by(objeto_id=objeto.id)
        .order_by(Revision.id.desc())
        .first()
    )
    contenido = ultima_revision.contenido if ultima_revision else ""
    return Topic(id=objeto.id, titulo=objeto.titulo_actual, contenido=contenido)


def crear(titulo: str, contenido: str) -> Topic:
    with SessionLocal() as db:
        objeto = ObjetoContenido(tipo="topic", titulo_actual=titulo)
        db.add(objeto)
        db.flush()  # asigna objeto.id sin cerrar la transacción todavía

        autor = _obtener_autor_por_defecto(db)
        revision = Revision(
            objeto_id=objeto.id,
            autor_id=autor.id,
            contenido=contenido,
            fecha=datetime.utcnow(),
        )
        db.add(revision)
        db.commit()

        return Topic(id=objeto.id, titulo=objeto.titulo_actual, contenido=contenido)


def listar() -> list[Topic]:
    with SessionLocal() as db:
        objetos = (
            db.query(ObjetoContenido)
            .filter_by(tipo="topic")
            .order_by(ObjetoContenido.id)
            .all()
        )
        return [_a_topic(db, objeto) for objeto in objetos]


def obtener(topic_id: int) -> Topic | None:
    with SessionLocal() as db:
        objeto = db.query(ObjetoContenido).filter_by(id=topic_id, tipo="topic").first()
        if objeto is None:
            return None
        return _a_topic(db, objeto)
