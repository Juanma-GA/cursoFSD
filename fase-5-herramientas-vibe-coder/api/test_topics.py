import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models  # noqa: F401 -- el import registra las 9 tablas en Base.metadata
import storage.memory_store as memory_store
from database import Base
from main import app

# Base de datos de test: SQLite en memoria, no la PostgreSQL real de
# desarrollo (ccms en Docker). Ver la sección "Estrategia de base de datos
# para los tests" del README de esta fase para el razonamiento completo.
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture()
def client(monkeypatch):
    # StaticPool: una base de datos SQLite en memoria vive solo mientras
    # dura una conexión. Sin StaticPool, cada nueva conexión abriría una
    # base de datos en memoria distinta y vacía. StaticPool reutiliza
    # siempre la misma conexión para que toda la request (y el test) vean
    # los mismos datos.
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

    # Crea las 9 tablas del esquema en la base de datos de test, vacía,
    # antes de cada test.
    Base.metadata.create_all(bind=test_engine)

    # storage/memory_store.py hace "from database import SessionLocal" al
    # importarse, así que ya tiene su propia referencia a la fábrica de
    # sesiones real. Sobreescribir database.SessionLocal no bastaría --
    # hay que sobreescribir la referencia que memory_store.py ya guardó.
    monkeypatch.setattr(memory_store, "SessionLocal", TestingSessionLocal)

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=test_engine)


def test_crear_topic_devuelve_201_con_id_asignado(client):
    respuesta = client.post(
        "/topics",
        json={"titulo": "Instalar el driver", "contenido": "Pasos para instalar el driver."},
    )

    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["id"] is not None
    assert datos["titulo"] == "Instalar el driver"
    assert datos["contenido"] == "Pasos para instalar el driver."


def test_listar_topics_incluye_el_topic_recien_creado(client):
    creado = client.post(
        "/topics",
        json={"titulo": "Configurar la impresora", "contenido": "Pasos para configurarla."},
    ).json()

    respuesta = client.get("/topics")

    assert respuesta.status_code == 200
    ids_en_la_lista = [topic["id"] for topic in respuesta.json()]
    assert creado["id"] in ids_en_la_lista


def test_mejorar_topic_existente_devuelve_sugerencia(client):
    creado = client.post(
        "/topics",
        json={"titulo": "Instalar el driver", "contenido": "  instalar   el driver  "},
    ).json()

    respuesta = client.post(f"/topics/{creado['id']}/mejorar")

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["contenido_original"] == "  instalar   el driver  "
    assert datos["contenido_mejorado"] == "Instalar el driver."


def test_mejorar_topic_inexistente_devuelve_404(client):
    respuesta = client.post("/topics/999999/mejorar")

    assert respuesta.status_code == 404
