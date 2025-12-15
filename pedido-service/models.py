"""Modelos de base de datos para PedidoService"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Float, Integer, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from datetime import datetime
import enum
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database import Base


class EstadoPedidoEnum(str, enum.Enum):
    RECIBIDO = "RECIBIDO"
    CONFIRMADO = "CONFIRMADO"
    EN_PREPARACION = "EN_PREPARACION"
    LISTO_PARA_ENTREGA = "LISTO_PARA_ENTREGA"
    EN_RUTA = "EN_RUTA"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"


class TipoEntregaEnum(str, enum.Enum):
    DOMICILIO = "DOMICILIO"
    PUNTO_RETIRO = "PUNTO_RETIRO"
    LOCKER = "LOCKER"


class Pedido(Base):
    __tablename__ = "pedidos"
    
    id = Column(String(36), primary_key=True, index=True)
    cliente_id = Column(String(36), nullable=False, index=True)
    numero_pedido = Column(String(50), unique=True, nullable=False, index=True)
    estado = Column(SQLEnum(EstadoPedidoEnum), nullable=False, default=EstadoPedidoEnum.RECIBIDO)
    tipo_entrega = Column(SQLEnum(TipoEntregaEnum), nullable=False)
    
    # Información de dirección
    direccion = Column(String(500), nullable=False)
    ciudad = Column(String(100), nullable=False)
    codigo_postal = Column(String(20), nullable=False)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    
    # Información del pedido
    descripcion = Column(Text, nullable=True)
    peso_kg = Column(Float, nullable=False, default=0.0)
    dimensiones = Column(String(100), nullable=True)
    valor_declarado = Column(Float, nullable=False, default=0.0)
    
    # Información de entrega
    destinatario_nombre = Column(String(255), nullable=False)
    destinatario_telefono = Column(String(20), nullable=True)
    destinatario_email = Column(String(255), nullable=True)
    
    # Repartidor asignado
    repartidor_id = Column(String(36), nullable=True, index=True)
    
    # Factura
    factura_id = Column(String(36), nullable=True, index=True)
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Pedido {self.numero_pedido}>"
