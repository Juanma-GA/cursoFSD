from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from database import Base

# Las 9 tablas del esquema diseñado en construccion_esquema_bd.md, mapeadas
# tal cual aparecen en el diagrama Mermaid de ese documento (mismas columnas,
# mismas PK/FK). Este archivo no añade ninguna tabla ni columna nueva: es la
# traducción directa del diseño a clases SQLAlchemy.


class ObjetoContenido(Base):
    # Identidad de un topic o un ditamap. Nunca guarda el contenido en sí
    # -- eso vive en Revisiones (ver nota de esa tabla).
    __tablename__ = "objetos_contenido"

    id = Column(Integer, primary_key=True)
    tipo = Column(String(20), nullable=False)  # "topic" o "ditamap"
    titulo_actual = Column(String(255), nullable=False)


class Autor(Base):
    __tablename__ = "autores"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)


class Revision(Base):
    __tablename__ = "revisiones"

    id = Column(Integer, primary_key=True)
    objeto_id = Column(Integer, ForeignKey("objetos_contenido.id"), nullable=False)
    autor_id = Column(Integer, ForeignKey("autores.id"), nullable=False)
    # Null si el objeto es un ditamap: la estructura de un mapa vive en
    # mapa_topic_refs, no como texto plano en esta columna.
    contenido = Column(Text, nullable=True)
    fecha = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class Version(Base):
    __tablename__ = "versiones"

    id = Column(Integer, primary_key=True)
    objeto_id = Column(Integer, ForeignKey("objetos_contenido.id"), nullable=False)
    revision_id = Column(Integer, ForeignKey("revisiones.id"), nullable=False)
    etiqueta = Column(String(255), nullable=False)  # checkpoint deliberado, tipo tag
    fecha = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class Estado(Base):
    __tablename__ = "estados"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False, unique=True)
    orden = Column(Integer, nullable=False)


class ObjetoEstado(Base):
    __tablename__ = "objeto_estado"

    id = Column(Integer, primary_key=True)
    objeto_id = Column(Integer, ForeignKey("objetos_contenido.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("versiones.id"), nullable=False)
    estado_id = Column(Integer, ForeignKey("estados.id"), nullable=False)


class Baseline(Base):
    __tablename__ = "baselines"

    id = Column(Integer, primary_key=True)
    ditamap_id = Column(Integer, ForeignKey("objetos_contenido.id"), nullable=False)
    mapa_revision_id = Column(Integer, ForeignKey("revisiones.id"), nullable=False)
    nombre = Column(String(255), nullable=False)
    fecha_sellado = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class BaselineVersion(Base):
    __tablename__ = "baseline_version"

    id = Column(Integer, primary_key=True)
    baseline_id = Column(Integer, ForeignKey("baselines.id"), nullable=False)
    objeto_id = Column(Integer, ForeignKey("objetos_contenido.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("versiones.id"), nullable=False)


class MapaTopicRef(Base):
    __tablename__ = "mapa_topic_refs"

    id = Column(Integer, primary_key=True)
    mapa_revision_id = Column(Integer, ForeignKey("revisiones.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("objetos_contenido.id"), nullable=False)
    topic_version_id = Column(Integer, ForeignKey("versiones.id"), nullable=False)
    orden = Column(Integer, nullable=False)
    keyref = Column(String(255), nullable=True)  # opcional, referencia indirecta tipo DITA key
