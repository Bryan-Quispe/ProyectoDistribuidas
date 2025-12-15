"""Aplicación FastAPI para FleetService"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fleet_service.routes import router
from fleet_service.models import Base
from shared.database import engine
from shared.logger import setup_logger

logger = setup_logger("fleet-service")
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FleetService",
    description="Servicio de gestión de repartidores y vehículos",
    version="1.0.0",
    docs_url="/swagger-ui.html",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/fleet", tags=["fleet"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "fleet-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
