from database import Base, engine
import models  # noqa: F401  -- el import registra las 9 tablas en Base.metadata

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente en la base de datos 'ccms'.")
