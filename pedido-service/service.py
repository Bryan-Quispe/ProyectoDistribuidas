"""Servicios de negocio para PedidoService"""
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedido_service.models import Pedido, EstadoPedidoEnum, TipoEntregaEnum
from pedido_service.schemas import CreatePedidoRequest, UpdatePedidoRequest


CIUDADES_COBERTURA = {
    "Bogotá": {"latitud_min": 4.5, "latitud_max": 4.9, "longitud_min": -74.3, "longitud_max": -73.8},
    "Medellín": {"latitud_min": 6.1, "latitud_max": 6.3, "longitud_min": -75.6, "longitud_max": -75.4},
    "Cali": {"latitud_min": 3.3, "latitud_max": 3.5, "longitud_min": -76.6, "longitud_max": -76.4},
    "Barranquilla": {"latitud_min": 10.9, "latitud_max": 11.1, "longitud_min": -74.8, "longitud_max": -74.6},
    "Cartagena": {"latitud_min": 10.3, "latitud_max": 10.5, "longitud_min": -75.5, "longitud_max": -75.3},
}


def validar_cobertura_geografica(ciudad: str, latitud: float = None, longitud: float = None) -> bool:
    """Valida que la ciudad esté en cobertura"""
    if ciudad not in CIUDADES_COBERTURA:
        return False
    
    if latitud is None or longitud is None:
        return True
    
    limites = CIUDADES_COBERTURA[ciudad]
    return (limites["latitud_min"] <= latitud <= limites["latitud_max"] and
            limites["longitud_min"] <= longitud <= limites["longitud_max"])


class PedidoService:
    
    @staticmethod
    def crear_pedido(db: Session, cliente_id: str, pedido_data: CreatePedidoRequest) -> Pedido:
        """Crea un nuevo pedido con validación transaccional"""
        # Validar cobertura geográfica
        if not validar_cobertura_geografica(pedido_data.ciudad, pedido_data.latitud, pedido_data.longitud):
            raise ValueError(f"La ciudad {pedido_data.ciudad} no está en cobertura")
        
        # Validar tipo de entrega
        if pedido_data.tipo_entrega not in [e.value for e in TipoEntregaEnum]:
            raise ValueError("Tipo de entrega inválido")
        
        # Crear pedido
        pedido = Pedido(
            id=str(uuid.uuid4()),
            cliente_id=cliente_id,
            numero_pedido=f"PED-{int(datetime.utcnow().timestamp())}-{uuid.uuid4().hex[:8].upper()}",
            estado=EstadoPedidoEnum.RECIBIDO,
            tipo_entrega=pedido_data.tipo_entrega,
            direccion=pedido_data.direccion,
            ciudad=pedido_data.ciudad,
            codigo_postal=pedido_data.codigo_postal,
            latitud=pedido_data.latitud,
            longitud=pedido_data.longitud,
            descripcion=pedido_data.descripcion,
            peso_kg=pedido_data.peso_kg,
            dimensiones=pedido_data.dimensiones,
            valor_declarado=pedido_data.valor_declarado,
            destinatario_nombre=pedido_data.destinatario_nombre,
            destinatario_telefono=pedido_data.destinatario_telefono,
            destinatario_email=pedido_data.destinatario_email
        )
        
        db.add(pedido)
        db.commit()
        db.refresh(pedido)
        
        return pedido
    
    @staticmethod
    def obtener_pedido(db: Session, pedido_id: str) -> Pedido:
        """Obtiene un pedido por ID"""
        return db.query(Pedido).filter(Pedido.id == pedido_id).first()
    
    @staticmethod
    def obtener_pedido_por_numero(db: Session, numero_pedido: str) -> Pedido:
        """Obtiene un pedido por número de pedido"""
        return db.query(Pedido).filter(Pedido.numero_pedido == numero_pedido).first()
    
    @staticmethod
    def obtener_pedidos_cliente(db: Session, cliente_id: str, skip: int = 0, limit: int = 10):
        """Obtiene todos los pedidos de un cliente"""
        return db.query(Pedido).filter(Pedido.cliente_id == cliente_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def obtener_todos_pedidos(db: Session, skip: int = 0, limit: int = 10):
        """Obtiene todos los pedidos (para supervisores)"""
        return db.query(Pedido).offset(skip).limit(limit).all()
    
    @staticmethod
    def actualizar_pedido(db: Session, pedido_id: str, pedido_data: UpdatePedidoRequest) -> Pedido:
        """Actualiza parcialmente un pedido con transacción ACID"""
        pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
        
        if not pedido:
            raise ValueError("Pedido no encontrado")
        
        # Actualizar solo los campos proporcionados
        if pedido_data.estado is not None:
            pedido.estado = pedido_data.estado
        if pedido_data.repartidor_id is not None:
            pedido.repartidor_id = pedido_data.repartidor_id
        if pedido_data.factura_id is not None:
            pedido.factura_id = pedido_data.factura_id
        if pedido_data.latitud is not None:
            pedido.latitud = pedido_data.latitud
        if pedido_data.longitud is not None:
            pedido.longitud = pedido_data.longitud
        
        db.commit()
        db.refresh(pedido)
        
        return pedido
    
    @staticmethod
    def cancelar_pedido(db: Session, pedido_id: str, motivo: str) -> Pedido:
        """Cancela un pedido de forma lógica"""
        pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
        
        if not pedido:
            raise ValueError("Pedido no encontrado")
        
        if pedido.estado == EstadoPedidoEnum.CANCELADO:
            raise ValueError("El pedido ya está cancelado")
        
        if pedido.estado in [EstadoPedidoEnum.ENTREGADO]:
            raise ValueError("No se puede cancelar un pedido ya entregado")
        
        pedido.estado = EstadoPedidoEnum.CANCELADO
        pedido.cancelled_at = datetime.utcnow()
        
        db.commit()
        db.refresh(pedido)
        
        return pedido
