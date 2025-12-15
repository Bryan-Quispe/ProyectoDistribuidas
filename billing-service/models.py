"""Modelos de base de datos para BillingService"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Float, Text
from sqlalchemy.sql import func
from datetime import datetime
import enum
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database import Base


class EstadoFacturaEnum(str, enum.Enum):
    BORRADOR = "BORRADOR"
    ENVIADA = "ENVIADA"
    PAGADA = "PAGADA"
    VENCIDA = "VENCIDA"
    CANCELADA = "CANCELADA"


class Factura(Base):
    __tablename__ = "facturas"
    
    id = Column(String(36), primary_key=True, index=True)
    numero_factura = Column(String(50), unique=True, nullable=False, index=True)
    pedido_id = Column(String(36), nullable=False, index=True)
    cliente_id = Column(String(36), nullable=False, index=True)
    
    # Información de tarifa
    tarifa_base = Column(Float, nullable=False)
    tarifa_distancia = Column(Float, nullable=False, default=0)
    tarifa_peso = Column(Float, nullable=False, default=0)
    descuento = Column(Float, nullable=False, default=0)
    total = Column(Float, nullable=False)
    impuesto = Column(Float, nullable=False, default=0)
    total_final = Column(Float, nullable=False)
    
    # Detalles
    descripcion = Column(Text, nullable=True)
    concepto = Column(String(255), nullable=False, default="Servicio de Envío")
    
    # Estado
    estado = Column(SQLEnum(EstadoFacturaEnum), nullable=False, default=EstadoFacturaEnum.BORRADOR)
    
    # Fechas
    fecha_emision = Column(DateTime(timezone=True), server_default=func.now())
    fecha_vencimiento = Column(DateTime(timezone=True), nullable=True)
    fecha_pago = Column(DateTime(timezone=True), nullable=True)
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Factura {self.numero_factura}>"
