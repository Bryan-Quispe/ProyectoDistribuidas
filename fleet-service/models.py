"""Modelos de base de datos para FleetService"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Float, Boolean
from sqlalchemy.sql import func
from datetime import datetime
import enum
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database import Base


class EstadoRepartidorEnum(str, enum.Enum):
    DISPONIBLE = "DISPONIBLE"
    EN_RUTA = "EN_RUTA"
    MANTENIMIENTO = "MANTENIMIENTO"
    INACTIVO = "INACTIVO"


class TipoVehiculoEnum(str, enum.Enum):
    MOTO = "MOTO"
    CARRO = "CARRO"
    CAMION = "CAMION"
    BICICLETA = "BICICLETA"


class Repartidor(Base):
    __tablename__ = "repartidores"
    
    id = Column(String(36), primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    telefono = Column(String(20), nullable=False)
    estado = Column(SQLEnum(EstadoRepartidorEnum), nullable=False, default=EstadoRepartidorEnum.DISPONIBLE)
    
    # Ubicación actual
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    ultima_ubicacion = Column(DateTime(timezone=True), nullable=True)
    
    # Información
    calificacion_promedio = Column(Float, default=5.0)
    entregas_completadas = Column(String(36), default=0)
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Repartidor {self.nombre}>"


class Vehiculo(Base):
    __tablename__ = "vehiculos"
    
    id = Column(String(36), primary_key=True, index=True)
    repartidor_id = Column(String(36), nullable=False, index=True)
    placa = Column(String(20), unique=True, nullable=False, index=True)
    tipo = Column(SQLEnum(TipoVehiculoEnum), nullable=False)
    modelo = Column(String(100), nullable=False)
    marca = Column(String(100), nullable=False)
    anio = Column(String(4), nullable=False)
    
    # Capacidad
    capacidad_kg = Column(Float, nullable=False)
    volumen_m3 = Column(Float, nullable=True)
    
    # Estado
    estado = Column(SQLEnum(EstadoRepartidorEnum), nullable=False, default=EstadoRepartidorEnum.DISPONIBLE)
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Vehiculo {self.placa}>"
