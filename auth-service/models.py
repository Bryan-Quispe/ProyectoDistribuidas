"""Modelos de base de datos para AuthService"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.sql import func
from datetime import datetime
import enum
import sys
import os

# Añadir carpeta compartida al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database import Base


class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    CLIENTE = "CLIENTE"
    REPARTIDOR = "REPARTIDOR"
    SUPERVISOR = "SUPERVISOR"


class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(SQLEnum(RoleEnum), nullable=False, default=RoleEnum.CLIENTE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<User {self.username}>"


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    
    id = Column(String(36), primary_key=True, index=True)
    token = Column(String(500), nullable=False, index=True, unique=True)
    revoked_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    def __repr__(self):
        return f"<TokenBlacklist revoked_at={self.revoked_at}>"
