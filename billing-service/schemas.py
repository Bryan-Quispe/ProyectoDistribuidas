"""Esquemas de validación para BillingService"""
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from datetime import datetime


class EstadoFacturaEnum(str, Enum):
    BORRADOR = "BORRADOR"
    ENVIADA = "ENVIADA"
    PAGADA = "PAGADA"
    VENCIDA = "VENCIDA"
    CANCELADA = "CANCELADA"


class CreateFacturaRequest(BaseModel):
    """Esquema para crear factura"""
    pedido_id: str
    cliente_id: str
    tarifa_base: float = Field(..., gt=0)
    tarifa_distancia: float = Field(default=0, ge=0)
    tarifa_peso: float = Field(default=0, ge=0)
    descuento: float = Field(default=0, ge=0)
    impuesto: float = Field(default=0, ge=0)
    descripcion: Optional[str] = Field(None, max_length=1000)
    concepto: str = Field(default="Servicio de Envío", max_length=255)
    
    class Config:
        json_schema_extra = {
            "example": {
                "pedido_id": "550e8400-e29b-41d4-a716-446655440000",
                "cliente_id": "550e8400-e29b-41d4-a716-446655440001",
                "tarifa_base": 10000,
                "tarifa_distancia": 5000,
                "tarifa_peso": 2000,
                "descuento": 1000,
                "impuesto": 1728,
                "descripcion": "Envío urbano"
            }
        }


class UpdateFacturaRequest(BaseModel):
    """Esquema para actualizar factura"""
    estado: Optional[EstadoFacturaEnum] = None
    descuento: Optional[float] = Field(None, ge=0)


class FacturaResponse(BaseModel):
    """Respuesta de factura"""
    id: str
    numero_factura: str
    pedido_id: str
    cliente_id: str
    tarifa_base: float
    tarifa_distancia: float
    tarifa_peso: float
    descuento: float
    total: float
    impuesto: float
    total_final: float
    descripcion: Optional[str]
    concepto: str
    estado: EstadoFacturaEnum
    fecha_emision: datetime
    fecha_vencimiento: Optional[datetime]
    fecha_pago: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True
