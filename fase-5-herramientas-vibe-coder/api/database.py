import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Credenciales del contenedor Docker levantado según el README de esta fase:
# docker run --name ccms-postgres -e POSTGRES_PASSWORD=curso123
#   -e POSTGRES_DB=ccms -p 5432:5432 -d postgres
# Las credenciales viven en .env (nunca en Git) — ver .env.example para la
# lista de variables necesarias.
load_dotenv()

# Los valores por defecto (segundo argumento de os.getenv) solo evitan que
# construir DATABASE_URL falle cuando no hay .env -- es el caso de CI
# (GitHub Actions), donde .env nunca existe a propósito (está en
# .gitignore). No son credenciales reales ni necesitan serlo: los tests
# nunca llegan a conectarse con ellas -- sustituyen SessionLocal por SQLite
# en memoria vía monkeypatch (ver test_topics.py) antes de que se use
# ninguna conexión de verdad.
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "ccms")

DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base de la que heredan todos los modelos en models.py; SQLAlchemy usa
# Base.metadata para saber qué tablas existen y poder crearlas.
Base = declarative_base()
