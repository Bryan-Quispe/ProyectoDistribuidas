"""API endpoints para FleetService"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fleet_service.models import Repartidor, Vehiculo, EstadoRepartidorEnum
from fleet_service.schemas import (
    CreateRepartidorRequest, UpdateRepartidorRequest, RepartidorResponse,
    CreateVehiculoRequest, VehiculoResponse
)
from fleet_service.service import FleetService
from shared.database import get_db
from shared.jwt_utils import verify_jwt_in_request
from shared.logger import setup_logger, log_request

router = APIRouter()
logger = setup_logger("fleet-service")


@router.post("/repartidores", response_model=RepartidorResponse, tags=["Repartidores"])
async def crear_repartidor(
    repartidor_data: CreateRepartidorRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Crea un nuevo repartidor. Requiere rol ADMIN o SUPERVISOR."""
    try:
        token_data = await verify_jwt_in_request(request)
        user_role = token_data.get("role", "").upper()
        
        if user_role not in ["SUPERVISOR", "ADMIN"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo supervisores pueden crear repartidores")
        
        repartidor = FleetService.crear_repartidor(db, repartidor_data)
        log_request(logger, "POST", "/repartidores", 201, token_data.get("sub"))
        return repartidor
    except ValueError as e:
        log_request(logger, "POST", "/repartidores", 400, None)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log_request(logger, "POST", "/repartidores", 500, None)
        logger.error(f"Error creando repartidor: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creando repartidor")


@router.get("/repartidores/{repartidor_id}", response_model=RepartidorResponse, tags=["Repartidores"])
async def obtener_repartidor(
    repartidor_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Obtiene un repartidor específico."""
    try:
        token_data = await verify_jwt_in_request(request)
        repartidor = FleetService.obtener_repartidor(db, repartidor_id)
        
        if not repartidor:
            raise ValueError("Repartidor no encontrado")
        
        log_request(logger, "GET", f"/repartidores/{repartidor_id}", 200, token_data.get("sub"))
        return repartidor
    except ValueError as e:
        log_request(logger, "GET", f"/repartidores/{repartidor_id}", 404, None)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log_request(logger, "GET", f"/repartidores/{repartidor_id}", 500, None)
        logger.error(f"Error obteniendo repartidor: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error obteniendo repartidor")


@router.get("/repartidores", response_model=list[RepartidorResponse], tags=["Repartidores"])
async def listar_repartidores(
    skip: int = 0,
    limit: int = 10,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Lista todos los repartidores activos."""
    try:
        token_data = await verify_jwt_in_request(request)
        repartidores = FleetService.obtener_todos_repartidores(db, skip, limit)
        log_request(logger, "GET", "/repartidores", 200, token_data.get("sub"))
        return repartidores
    except HTTPException:
        raise
    except Exception as e:
        log_request(logger, "GET", "/repartidores", 500, None)
        logger.error(f"Error listando repartidores: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error listando repartidores")


@router.patch("/repartidores/{repartidor_id}", response_model=RepartidorResponse, tags=["Repartidores"])
async def actualizar_repartidor(
    repartidor_id: str,
    repartidor_data: UpdateRepartidorRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Actualiza un repartidor (PATCH)."""
    try:
        token_data = await verify_jwt_in_request(request)
        repartidor = FleetService.actualizar_repartidor(db, repartidor_id, repartidor_data)
        log_request(logger, "PATCH", f"/repartidores/{repartidor_id}", 200, token_data.get("sub"))
        return repartidor
    except ValueError as e:
        log_request(logger, "PATCH", f"/repartidores/{repartidor_id}", 404, None)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log_request(logger, "PATCH", f"/repartidores/{repartidor_id}", 500, None)
        logger.error(f"Error actualizando repartidor: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error actualizando repartidor")


@router.post("/vehiculos", response_model=VehiculoResponse, tags=["Vehiculos"])
async def crear_vehiculo(
    vehiculo_data: CreateVehiculoRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Crea un nuevo vehículo para un repartidor."""
    try:
        token_data = await verify_jwt_in_request(request)
        user_role = token_data.get("role", "").upper()
        
        if user_role not in ["SUPERVISOR", "ADMIN"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo supervisores pueden crear vehículos")
        
        vehiculo = FleetService.crear_vehiculo(db, vehiculo_data)
        log_request(logger, "POST", "/vehiculos", 201, token_data.get("sub"))
        return vehiculo
    except ValueError as e:
        log_request(logger, "POST", "/vehiculos", 400, None)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log_request(logger, "POST", "/vehiculos", 500, None)
        logger.error(f"Error creando vehículo: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creando vehículo")


@router.get("/vehiculos/{vehiculo_id}", response_model=VehiculoResponse, tags=["Vehiculos"])
async def obtener_vehiculo(
    vehiculo_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Obtiene un vehículo específico."""
    try:
        token_data = await verify_jwt_in_request(request)
        vehiculo = FleetService.obtener_vehiculo(db, vehiculo_id)
        
        if not vehiculo:
            raise ValueError("Vehículo no encontrado")
        
        log_request(logger, "GET", f"/vehiculos/{vehiculo_id}", 200, token_data.get("sub"))
        return vehiculo
    except ValueError as e:
        log_request(logger, "GET", f"/vehiculos/{vehiculo_id}", 404, None)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log_request(logger, "GET", f"/vehiculos/{vehiculo_id}", 500, None)
        logger.error(f"Error obteniendo vehículo: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error obteniendo vehículo")
