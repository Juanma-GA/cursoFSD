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

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base de la que heredan todos los modelos en models.py; SQLAlchemy usa
# Base.metadata para saber qué tablas existen y poder crearlas.
Base = declarative_base()
