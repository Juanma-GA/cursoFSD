from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import topics

app = FastAPI(title="CCMS API - Fase 3")

# Único cambio real frente a la copia de fase-2: CORS. En fase-1/fase-2 la
# API solo se probó con curl/Swagger (mismo origen que el propio backend).
# El dashboard de esta fase corre en el navegador desde otro puerto
# (Vite, 5173), así que sin esto el navegador bloquearía el fetch() por
# política de mismo origen — el mismo concepto ya visto en la Fase 0.
#
# allow_origins apunta solo a localhost:5173 (el dashboard en desarrollo),
# no a "*" (cualquier origen) — en un despliegue real, este valor sería el
# dominio real donde viva el dashboard en producción (ej.
# "https://ccms.miempresa.com"), nunca localhost ni "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# main.py solo ensambla la aplicación: registra routers. No define lógica
# ni rutas aquí directamente, para que este archivo siga siendo pequeño
# aunque el número de recursos (topics, usuarios, proyectos...) crezca.
app.include_router(topics.router)
