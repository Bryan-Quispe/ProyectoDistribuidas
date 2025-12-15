"""Servicios de negocio para FleetService"""
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fleet_service.models import Repartidor, Vehiculo, EstadoRepartidorEnum
from fleet_service.schemas import CreateRepartidorRequest, UpdateRepartidorRequest, CreateVehiculoRequest


class FleetService:
    
    @staticmethod
    def crear_repartidor(db: Session, repartidor_data: CreateRepartidorRequest) -> Repartidor:
        """Crea un nuevo repartidor"""
        # Verificar que el email no exista
        existing = db.query(Repartidor).filter(Repartidor.email == repartidor_data.email).first()
        if existing:
            raise ValueError("El email ya está registrado")
        
        repartidor = Repartidor(
            id=str(uuid.uuid4()),
            nombre=repartidor_data.nombre,
            email=repartidor_data.email,
            telefono=repartidor_data.telefono,
            estado=EstadoRepartidorEnum.DISPONIBLE
        )
        
        db.add(repartidor)
        db.commit()
        db.refresh(repartidor)
        
        return repartidor
    
    @staticmethod
    def obtener_repartidor(db: Session, repartidor_id: str) -> Repartidor:
        """Obtiene un repartidor por ID"""
        return db.query(Repartidor).filter(Repartidor.id == repartidor_id).first()
    
    @staticmethod
    def obtener_todos_repartidores(db: Session, skip: int = 0, limit: int = 10):
        """Obtiene todos los repartidores"""
        return db.query(Repartidor).filter(Repartidor.is_active == True).offset(skip).limit(limit).all()
    
    @staticmethod
    def actualizar_repartidor(db: Session, repartidor_id: str, repartidor_data: UpdateRepartidorRequest) -> Repartidor:
        """Actualiza un repartidor con transacción ACID"""
        repartidor = db.query(Repartidor).filter(Repartidor.id == repartidor_id).first()
        
        if not repartidor:
            raise ValueError("Repartidor no encontrado")
        
        if repartidor_data.estado is not None:
            repartidor.estado = repartidor_data.estado
        if repartidor_data.latitud is not None:
            repartidor.latitud = repartidor_data.latitud
            repartidor.ultima_ubicacion = datetime.utcnow()
        if repartidor_data.longitud is not None:
            repartidor.longitud = repartidor_data.longitud
            repartidor.ultima_ubicacion = datetime.utcnow()
        if repartidor_data.calificacion_promedio is not None:
            repartidor.calificacion_promedio = repartidor_data.calificacion_promedio
        
        db.commit()
        db.refresh(repartidor)
        
        return repartidor
    
    @staticmethod
    def dar_baja_repartidor(db: Session, repartidor_id: str) -> Repartidor:
        """Da de baja un repartidor"""
        repartidor = db.query(Repartidor).filter(Repartidor.id == repartidor_id).first()
        
        if not repartidor:
            raise ValueError("Repartidor no encontrado")
        
        repartidor.is_active = False
        repartidor.estado = EstadoRepartidorEnum.INACTIVO
        
        db.commit()
        db.refresh(repartidor)
        
        return repartidor
    
    @staticmethod
    def crear_vehiculo(db: Session, vehiculo_data: CreateVehiculoRequest) -> Vehiculo:
        """Crea un nuevo vehículo"""
        # Verificar que el repartidor existe
        repartidor = db.query(Repartidor).filter(Repartidor.id == vehiculo_data.repartidor_id).first()
        if not repartidor:
            raise ValueError("Repartidor no encontrado")
        
        # Verificar que la placa no exista
        existing = db.query(Vehiculo).filter(Vehiculo.placa == vehiculo_data.placa).first()
        if existing:
            raise ValueError("La placa ya está registrada")
        
        vehiculo = Vehiculo(
            id=str(uuid.uuid4()),
            repartidor_id=vehiculo_data.repartidor_id,
            placa=vehiculo_data.placa,
            tipo=vehiculo_data.tipo,
            modelo=vehiculo_data.modelo,
            marca=vehiculo_data.marca,
            anio=vehiculo_data.anio,
            capacidad_kg=vehiculo_data.capacidad_kg,
            volumen_m3=vehiculo_data.volumen_m3
        )
        
        db.add(vehiculo)
        db.commit()
        db.refresh(vehiculo)
        
        return vehiculo
    
    @staticmethod
    def obtener_vehiculo(db: Session, vehiculo_id: str) -> Vehiculo:
        """Obtiene un vehículo por ID"""
        return db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    
    @staticmethod
    def obtener_vehiculos_repartidor(db: Session, repartidor_id: str):
        """Obtiene todos los vehículos de un repartidor"""
        return db.query(Vehiculo).filter(
            Vehiculo.repartidor_id == repartidor_id,
            Vehiculo.is_active == True
        ).all()
    
    @staticmethod
    def actualizar_estado_vehiculo(db: Session, vehiculo_id: str, estado: EstadoRepartidorEnum) -> Vehiculo:
        """Actualiza el estado de un vehículo"""
        vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
        
        if not vehiculo:
            raise ValueError("Vehículo no encontrado")
        
        vehiculo.estado = estado
        db.commit()
        db.refresh(vehiculo)
        
        return vehiculo
