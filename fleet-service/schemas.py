"""Esquemas de validación para FleetService"""
from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from typing import Optional
from datetime import datetime


class EstadoRepartidorEnum(str, Enum):
    DISPONIBLE = "DISPONIBLE"
    EN_RUTA = "EN_RUTA"
    MANTENIMIENTO = "MANTENIMIENTO"
    INACTIVO = "INACTIVO"


class TipoVehiculoEnum(str, Enum):
    MOTO = "MOTO"
    CARRO = "CARRO"
    CAMION = "CAMION"
    BICICLETA = "BICICLETA"


class CreateRepartidorRequest(BaseModel):
    """Esquema para crear repartidor"""
    nombre: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    telefono: str = Field(..., min_length=7, max_length=20)
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Carlos García",
                "email": "carlos@example.com",
                "telefono": "+573001234567"
            }
        }


class UpdateRepartidorRequest(BaseModel):
    """Esquema para actualizar repartidor"""
    estado: Optional[EstadoRepartidorEnum] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    calificacion_promedio: Optional[float] = Field(None, ge=0, le=5)


class RepartidorResponse(BaseModel):
    """Respuesta de repartidor"""
    id: str
    nombre: str
    email: str
    telefono: str
    estado: EstadoRepartidorEnum
    latitud: Optional[float]
    longitud: Optional[float]
    calificacion_promedio: float
    entregas_completadas: str
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class CreateVehiculoRequest(BaseModel):
    """Esquema para crear vehículo"""
    repartidor_id: str
    placa: str = Field(..., min_length=1, max_length=20)
    tipo: TipoVehiculoEnum
    modelo: str = Field(..., min_length=1, max_length=100)
    marca: str = Field(..., min_length=1, max_length=100)
    anio: str = Field(..., min_length=4, max_length=4)
    capacidad_kg: float = Field(..., gt=0)
    volumen_m3: Optional[float] = Field(None, gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "repartidor_id": "550e8400-e29b-41d4-a716-446655440000",
                "placa": "ABC-123",
                "tipo": "CARRO",
                "modelo": "Honda Civic",
                "marca": "Honda",
                "anio": "2022",
                "capacidad_kg": 500,
                "volumen_m3": 2.5
            }
        }


class VehiculoResponse(BaseModel):
    """Respuesta de vehículo"""
    id: str
    repartidor_id: str
    placa: str
    tipo: TipoVehiculoEnum
    modelo: str
    marca: str
    anio: str
    capacidad_kg: float
    volumen_m3: Optional[float]
    estado: EstadoRepartidorEnum
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True
