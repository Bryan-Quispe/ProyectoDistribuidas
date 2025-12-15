"""Esquemas de validación para PedidoService"""
from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from typing import Optional
from datetime import datetime


class EstadoPedidoEnum(str, Enum):
    RECIBIDO = "RECIBIDO"
    CONFIRMADO = "CONFIRMADO"
    EN_PREPARACION = "EN_PREPARACION"
    LISTO_PARA_ENTREGA = "LISTO_PARA_ENTREGA"
    EN_RUTA = "EN_RUTA"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"


class TipoEntregaEnum(str, Enum):
    DOMICILIO = "DOMICILIO"
    PUNTO_RETIRO = "PUNTO_RETIRO"
    LOCKER = "LOCKER"


class CreatePedidoRequest(BaseModel):
    """Esquema para crear un pedido"""
    tipo_entrega: TipoEntregaEnum
    direccion: str = Field(..., min_length=5, max_length=500)
    ciudad: str = Field(..., min_length=2, max_length=100)
    codigo_postal: str = Field(..., min_length=3, max_length=20)
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    descripcion: Optional[str] = Field(None, max_length=1000)
    peso_kg: float = Field(..., ge=0.1)
    dimensiones: Optional[str] = Field(None, max_length=100)
    valor_declarado: float = Field(..., ge=0)
    destinatario_nombre: str = Field(..., min_length=2, max_length=255)
    destinatario_telefono: Optional[str] = Field(None, max_length=20)
    destinatario_email: Optional[EmailStr] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "tipo_entrega": "DOMICILIO",
                "direccion": "Calle Principal 123, Apartamento 4B",
                "ciudad": "Bogotá",
                "codigo_postal": "110111",
                "latitud": 4.7110,
                "longitud": -74.0721,
                "descripcion": "Paquete con documentos",
                "peso_kg": 2.5,
                "dimensiones": "30x20x10 cm",
                "valor_declarado": 100000,
                "destinatario_nombre": "Juan Pérez",
                "destinatario_telefono": "+573001234567",
                "destinatario_email": "juan@example.com"
            }
        }


class UpdatePedidoRequest(BaseModel):
    """Esquema para actualización parcial de pedido"""
    estado: Optional[EstadoPedidoEnum] = None
    repartidor_id: Optional[str] = None
    factura_id: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "estado": "CONFIRMADO",
                "repartidor_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class PedidoResponse(BaseModel):
    """Esquema de respuesta de pedido"""
    id: str
    numero_pedido: str
    cliente_id: str
    estado: EstadoPedidoEnum
    tipo_entrega: TipoEntregaEnum
    direccion: str
    ciudad: str
    codigo_postal: str
    latitud: Optional[float]
    longitud: Optional[float]
    descripcion: Optional[str]
    peso_kg: float
    dimensiones: Optional[str]
    valor_declarado: float
    destinatario_nombre: str
    destinatario_telefono: Optional[str]
    destinatario_email: Optional[str]
    repartidor_id: Optional[str]
    factura_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    cancelled_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CancelPedidoRequest(BaseModel):
    """Esquema para cancelar pedido"""
    motivo: str = Field(..., min_length=5, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "motivo": "Cliente solicita cancelación del pedido"
            }
        }
