from fastapi import FastAPI

from routers import topics

app = FastAPI(title="CCMS API - Fase 1")

# main.py solo ensambla la aplicación: registra routers. No define lógica
# ni rutas aquí directamente, para que este archivo siga siendo pequeño
# aunque el número de recursos (topics, usuarios, proyectos...) crezca.
app.include_router(topics.router)
