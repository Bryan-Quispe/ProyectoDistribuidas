"""API endpoints para PedidoService"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedido_service.models import Pedido
from pedido_service.schemas import (
    CreatePedidoRequest, UpdatePedidoRequest, PedidoResponse, CancelPedidoRequest
)
from pedido_service.service import PedidoService
from shared.database import get_db
from shared.jwt_utils import verify_jwt_in_request
from shared.logger import setup_logger, log_request

router = APIRouter()
logger = setup_logger("pedido-service")


@router.post("/", response_model=PedidoResponse, tags=["Pedidos"])
async def crear_pedido(
    pedido_data: CreatePedidoRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo pedido.
    Requiere autenticación JWT en el header Authorization.
    
    - **tipo_entrega**: DOMICILIO, PUNTO_RETIRO, o LOCKER
    - **ciudad**: Debe estar en cobertura (Bogotá, Medellín, Cali, Barranquilla, Cartagena)
    - **peso_kg**: Peso del paquete (mínimo 0.1 kg)
    - **valor_declarado**: Valor del envío en pesos colombianos
    """
    try:
        # Verificar JWT
        token_data = await verify_jwt_in_request(request)
        cliente_id = token_data.get("sub")
        
        # Crear pedido
        pedido = PedidoService.crear_pedido(db, cliente_id, pedido_data)
        log_request(logger, "POST", "/api/pedidos", 201, cliente_id)
        return pedido
    except ValueError as e:
        log_request(logger, "POST", "/api/pedidos", 400, None)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log_request(logger, "POST", "/api/pedidos", 500, None)
        logger.error(f"Error creando pedido: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creando pedido")


@router.get("/{pedido_id}", response_model=PedidoResponse, tags=["Pedidos"])
async def obtener_pedido(
    pedido_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles de un pedido específico.
    Requiere autenticación JWT en el header Authorization.
    """
    try:
        # Verificar JWT
        token_data = await verify_jwt_in_request(request)
        user_id = token_data.get("sub")
        
        # Obtener pedido
        pedido = PedidoService.obtener_pedido(db, pedido_id)
        
        if not pedido:
            raise ValueError("Pedido no encontrado")
        
        log_request(logger, "GET", f"/api/pedidos/{pedido_id}", 200, user_id)
        return pedido
    except ValueError as e:
        log_request(logger, "GET", f"/api/pedidos/{pedido_id}", 404, None)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log_request(logger, "GET", f"/api/pedidos/{pedido_id}", 500, None)
        logger.error(f"Error obteniendo pedido: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error obteniendo pedido")


@router.get("/", response_model=list[PedidoResponse], tags=["Pedidos"])
async def listar_pedidos(
    skip: int = 0,
    limit: int = 10,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Lista todos los pedidos del cliente autenticado.
    Requiere autenticación JWT en el header Authorization.
    Parámetros opcionales: skip (desplazamiento), limit (límite de resultados)
    """
    try:
        # Verificar JWT
        token_data = await verify_jwt_in_request(request)
        cliente_id = token_data.get("sub")
        
        # Obtener pedidos del cliente
        pedidos = PedidoService.obtener_pedidos_cliente(db, cliente_id, skip, limit)
        log_request(logger, "GET", "/api/pedidos", 200, cliente_id)
        return pedidos
    except HTTPException:
        raise
    except Exception as e:
        log_request(logger, "GET", "/api/pedidos", 500, None)
        logger.error(f"Error listando pedidos: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error listando pedidos")


@router.patch("/{pedido_id}", response_model=PedidoResponse, tags=["Pedidos"])
async def actualizar_pedido(
    pedido_id: str,
    pedido_data: UpdatePedidoRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Actualiza parcialmente un pedido (PATCH).
    Requiere autenticación JWT en el header Authorization.
    Solo supervisores pueden actualizar estado y repartidor.
    
    - **estado**: Nuevo estado del pedido
    - **repartidor_id**: ID del repartidor asignado
    - **factura_id**: ID de la factura
    """
    try:
        # Verificar JWT
        token_data = await verify_jwt_in_request(request)
        user_id = token_data.get("sub")
        user_role = token_data.get("role", "").upper()
        
        # Validar permiso (solo supervisores)
        if user_role not in ["SUPERVISOR", "ADMIN"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo supervisores pueden actualizar pedidos")
        
        # Actualizar pedido
        pedido = PedidoService.actualizar_pedido(db, pedido_id, pedido_data)
        log_request(logger, "PATCH", f"/api/pedidos/{pedido_id}", 200, user_id)
        return pedido
    except ValueError as e:
        log_request(logger, "PATCH", f"/api/pedidos/{pedido_id}", 404, None)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log_request(logger, "PATCH", f"/api/pedidos/{pedido_id}", 500, None)
        logger.error(f"Error actualizando pedido: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error actualizando pedido")


@router.delete("/{pedido_id}", tags=["Pedidos"])
async def cancelar_pedido(
    pedido_id: str,
    cancel_data: CancelPedidoRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Cancela un pedido (cancelación lógica).
    Requiere autenticación JWT en el header Authorization.
    
    - **motivo**: Motivo de la cancelación
    """
    try:
        # Verificar JWT
        token_data = await verify_jwt_in_request(request)
        cliente_id = token_data.get("sub")
        
        # Cancelar pedido
        pedido = PedidoService.cancelar_pedido(db, pedido_id, cancel_data.motivo)
        log_request(logger, "DELETE", f"/api/pedidos/{pedido_id}", 200, cliente_id)
        return {"message": "Pedido cancelado exitosamente", "pedido_id": pedido_id}
    except ValueError as e:
        log_request(logger, "DELETE", f"/api/pedidos/{pedido_id}", 404, None)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log_request(logger, "DELETE", f"/api/pedidos/{pedido_id}", 500, None)
        logger.error(f"Error cancelando pedido: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error cancelando pedido")
