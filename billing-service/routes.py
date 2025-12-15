"""API endpoints para BillingService"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from billing_service.models import Factura, EstadoFacturaEnum
from billing_service.schemas import (
    CreateFacturaRequest, UpdateFacturaRequest, FacturaResponse
)
from billing_service.service import BillingService
from shared.database import get_db
from shared.jwt_utils import verify_jwt_in_request
from shared.logger import setup_logger, log_request

router = APIRouter()
logger = setup_logger("billing-service")


@router.post("/", response_model=FacturaResponse, tags=["Facturas"])
async def crear_factura(
    factura_data: CreateFacturaRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva factura en estado BORRADOR.
    Requiere autenticación JWT en el header Authorization.
    
    Cálculo automático de impuesto (IVA 19%) si no se especifica.
    """
    try:
        token_data = await verify_jwt_in_request(request)
        user_id = token_data.get("sub")
        
        factura = BillingService.crear_factura(db, factura_data)
        log_request(logger, "POST", "/api/billing", 201, user_id)
        return factura
    except ValueError as e:
        log_request(logger, "POST", "/api/billing", 400, None)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log_request(logger, "POST", "/api/billing", 500, None)
        logger.error(f"Error creando factura: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creando factura")


@router.get("/{factura_id}", response_model=FacturaResponse, tags=["Facturas"])
async def obtener_factura(
    factura_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Obtiene los detalles de una factura específica."""
    try:
        token_data = await verify_jwt_in_request(request)
        user_id = token_data.get("sub")
        
        factura = BillingService.obtener_factura(db, factura_id)
        
        if not factura:
            raise ValueError("Factura no encontrada")
        
        log_request(logger, "GET", f"/api/billing/{factura_id}", 200, user_id)
        return factura
    except ValueError as e:
        log_request(logger, "GET", f"/api/billing/{factura_id}", 404, None)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log_request(logger, "GET", f"/api/billing/{factura_id}", 500, None)
        logger.error(f"Error obteniendo factura: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error obteniendo factura")


@router.get("/", response_model=list[FacturaResponse], tags=["Facturas"])
async def listar_facturas_cliente(
    skip: int = 0,
    limit: int = 10,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Lista todas las facturas del cliente autenticado."""
    try:
        token_data = await verify_jwt_in_request(request)
        cliente_id = token_data.get("sub")
        
        facturas = BillingService.obtener_facturas_cliente(db, cliente_id, skip, limit)
        log_request(logger, "GET", "/api/billing", 200, cliente_id)
        return facturas
    except HTTPException:
        raise
    except Exception as e:
        log_request(logger, "GET", "/api/billing", 500, None)
        logger.error(f"Error listando facturas: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error listando facturas")


@router.patch("/{factura_id}", response_model=FacturaResponse, tags=["Facturas"])
async def actualizar_factura(
    factura_id: str,
    factura_data: UpdateFacturaRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Actualiza una factura parcialmente (PATCH).
    Solo se pueden editar facturas en estado BORRADOR.
    """
    try:
        token_data = await verify_jwt_in_request(request)
        user_id = token_data.get("sub")
        
        factura = BillingService.actualizar_factura(db, factura_id, factura_data)
        log_request(logger, "PATCH", f"/api/billing/{factura_id}", 200, user_id)
        return factura
    except ValueError as e:
        log_request(logger, "PATCH", f"/api/billing/{factura_id}", 400, None)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log_request(logger, "PATCH", f"/api/billing/{factura_id}", 500, None)
        logger.error(f"Error actualizando factura: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error actualizando factura")


@router.post("/{factura_id}/enviar", tags=["Facturas"])
async def enviar_factura(
    factura_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Envía una factura (cambia estado a ENVIADA)."""
    try:
        token_data = await verify_jwt_in_request(request)
        user_id = token_data.get("sub")
        
        factura = BillingService.cambiar_estado_factura(
            db, factura_id, EstadoFacturaEnum.ENVIADA
        )
        
        log_request(logger, "POST", f"/api/billing/{factura_id}/enviar", 200, user_id)
        return {"message": "Factura enviada exitosamente", "factura_id": factura_id}
    except ValueError as e:
        log_request(logger, "POST", f"/api/billing/{factura_id}/enviar", 400, None)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log_request(logger, "POST", f"/api/billing/{factura_id}/enviar", 500, None)
        logger.error(f"Error enviando factura: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error enviando factura")
