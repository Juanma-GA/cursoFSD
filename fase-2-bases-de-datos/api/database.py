from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Credenciales del contenedor Docker levantado según el README de esta fase:
# docker run --name ccms-postgres -e POSTGRES_PASSWORD=curso123
#   -e POSTGRES_DB=ccms -p 5432:5432 -d postgres
DATABASE_URL = "postgresql+psycopg2://postgres:curso123@localhost:5432/ccms"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base de la que heredan todos los modelos en models.py; SQLAlchemy usa
# Base.metadata para saber qué tablas existen y poder crearlas.
Base = declarative_base()
