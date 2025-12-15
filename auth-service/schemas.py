"""Esquemas de validación para AuthService"""
from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from typing import Optional
from datetime import datetime


class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    CLIENTE = "CLIENTE"
    REPARTIDOR = "REPARTIDOR"
    SUPERVISOR = "SUPERVISOR"


class UserRegister(BaseModel):
    """Esquema para registro de usuario"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = Field(None, max_length=255)
    role: RoleEnum = RoleEnum.CLIENTE
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@example.com",
                "username": "usuario123",
                "password": "securepassword",
                "full_name": "Juan Pérez",
                "role": "CLIENTE"
            }
        }


class UserLogin(BaseModel):
    """Esquema para login"""
    username: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "usuario123",
                "password": "securepassword"
            }
        }


class TokenResponse(BaseModel):
    """Esquema de respuesta de token"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class UserResponse(BaseModel):
    """Esquema de respuesta de usuario"""
    id: str
    email: str
    username: str
    full_name: Optional[str]
    role: RoleEnum
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "usuario@example.com",
                "username": "usuario123",
                "full_name": "Juan Pérez",
                "role": "CLIENTE",
                "is_active": True,
                "created_at": "2025-12-15T10:30:00"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Esquema para refresh de token"""
    refresh_token: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
