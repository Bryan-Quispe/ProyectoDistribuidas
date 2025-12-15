"""Aplicación FastAPI para BillingService"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from billing_service.routes import router
from billing_service.models import Base
from shared.database import engine
from shared.logger import setup_logger

logger = setup_logger("billing-service")
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BillingService",
    description="Servicio de facturación y cálculo de tarifas",
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

app.include_router(router, prefix="/api/billing", tags=["billing"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "billing-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
