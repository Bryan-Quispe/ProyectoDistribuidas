"""Servicios de negocio para BillingService"""
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from billing_service.models import Factura, EstadoFacturaEnum
from billing_service.schemas import CreateFacturaRequest, UpdateFacturaRequest


# Tasas de impuesto en Colombia (IVA = 19%)
IVA_RATE = 0.19


class BillingService:
    
    @staticmethod
    def calcular_total_factura(factura_data: CreateFacturaRequest) -> tuple[float, float, float]:
        """Calcula subtotal, impuesto y total final"""
        subtotal = (factura_data.tarifa_base + 
                   factura_data.tarifa_distancia + 
                   factura_data.tarifa_peso - 
                   factura_data.descuento)
        
        impuesto = subtotal * IVA_RATE if factura_data.impuesto == 0 else factura_data.impuesto
        total_final = subtotal + impuesto
        
        return subtotal, impuesto, total_final
    
    @staticmethod
    def crear_factura(db: Session, factura_data: CreateFacturaRequest) -> Factura:
        """Crea una nueva factura en estado BORRADOR con transacción ACID"""
        # Calcular totales
        subtotal, impuesto, total_final = BillingService.calcular_total_factura(factura_data)
        
        # Crear factura
        factura = Factura(
            id=str(uuid.uuid4()),
            numero_factura=f"FAC-{int(datetime.utcnow().timestamp())}-{uuid.uuid4().hex[:8].upper()}",
            pedido_id=factura_data.pedido_id,
            cliente_id=factura_data.cliente_id,
            tarifa_base=factura_data.tarifa_base,
            tarifa_distancia=factura_data.tarifa_distancia,
            tarifa_peso=factura_data.tarifa_peso,
            descuento=factura_data.descuento,
            total=subtotal,
            impuesto=impuesto,
            total_final=total_final,
            descripcion=factura_data.descripcion,
            concepto=factura_data.concepto,
            estado=EstadoFacturaEnum.BORRADOR,
            fecha_vencimiento=datetime.utcnow() + timedelta(days=30)
        )
        
        db.add(factura)
        db.commit()
        db.refresh(factura)
        
        return factura
    
    @staticmethod
    def obtener_factura(db: Session, factura_id: str) -> Factura:
        """Obtiene una factura por ID"""
        return db.query(Factura).filter(Factura.id == factura_id).first()
    
    @staticmethod
    def obtener_factura_por_numero(db: Session, numero_factura: str) -> Factura:
        """Obtiene una factura por número"""
        return db.query(Factura).filter(Factura.numero_factura == numero_factura).first()
    
    @staticmethod
    def obtener_facturas_cliente(db: Session, cliente_id: str, skip: int = 0, limit: int = 10):
        """Obtiene todas las facturas de un cliente"""
        return db.query(Factura).filter(Factura.cliente_id == cliente_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def obtener_facturas_pedido(db: Session, pedido_id: str):
        """Obtiene las facturas de un pedido"""
        return db.query(Factura).filter(Factura.pedido_id == pedido_id).all()
    
    @staticmethod
    def actualizar_factura(db: Session, factura_id: str, factura_data: UpdateFacturaRequest) -> Factura:
        """Actualiza una factura parcialmente"""
        factura = db.query(Factura).filter(Factura.id == factura_id).first()
        
        if not factura:
            raise ValueError("Factura no encontrada")
        
        if factura.estado != EstadoFacturaEnum.BORRADOR:
            raise ValueError("Solo se pueden editar facturas en estado BORRADOR")
        
        if factura_data.estado is not None:
            factura.estado = factura_data.estado
        
        if factura_data.descuento is not None:
            factura.descuento = factura_data.descuento
            # Recalcular total
            subtotal = (factura.tarifa_base + factura.tarifa_distancia + 
                       factura.tarifa_peso - factura_data.descuento)
            factura.total = subtotal
            factura.total_final = subtotal + factura.impuesto
        
        db.commit()
        db.refresh(factura)
        
        return factura
    
    @staticmethod
    def cambiar_estado_factura(db: Session, factura_id: str, nuevo_estado: EstadoFacturaEnum) -> Factura:
        """Cambia el estado de una factura con validaciones"""
        factura = db.query(Factura).filter(Factura.id == factura_id).first()
        
        if not factura:
            raise ValueError("Factura no encontrada")
        
        # Validaciones de transición de estado
        if factura.estado == EstadoFacturaEnum.PAGADA:
            raise ValueError("No se puede cambiar el estado de una factura ya pagada")
        
        if nuevo_estado == EstadoFacturaEnum.PAGADA:
            factura.fecha_pago = datetime.utcnow()
        
        factura.estado = nuevo_estado
        db.commit()
        db.refresh(factura)
        
        return factura
