"""Aplicación FastAPI para PedidoService"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedido_service.routes import router
from pedido_service.models import Base
from shared.database import engine
from shared.logger import setup_logger

# Configurar logger
logger = setup_logger("pedido-service")

# Crear tablas
Base.metadata.create_all(bind=engine)

# Crear aplicación
app = FastAPI(
    title="PedidoService",
    description="Servicio de gestión de pedidos",
    version="1.0.0",
    docs_url="/swagger-ui.html",
    openapi_url="/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(router, prefix="/api/pedidos", tags=["pedidos"])


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "pedido-service"}


@app.get("/docs", tags=["Documentation"])
async def docs():
    """Documentación OpenAPI"""
    return {"docs_url": "/swagger-ui.html", "openapi_url": "/openapi.json"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
