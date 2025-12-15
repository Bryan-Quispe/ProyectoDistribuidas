"""Servicios de negocio para AuthService"""
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import bcrypt
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auth_service.models import User, TokenBlacklist, RoleEnum
from auth_service.schemas import UserRegister, TokenResponse, RefreshTokenRequest
from shared.jwt_utils import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES


def hash_password(password: str) -> str:
    """Hashea una contraseña"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verifica una contraseña contra su hash"""
    return bcrypt.checkpw(password.encode(), password_hash.encode())


class AuthService:
    
    @staticmethod
    def register_user(db: Session, user_data: UserRegister) -> User:
        """Registra un nuevo usuario"""
        # Verificar que el usuario no exista
        existing_user = db.query(User).filter(
            or_(User.email == user_data.email, User.username == user_data.username)
        ).first()
        
        if existing_user:
            raise ValueError("El usuario o email ya existe")
        
        # Crear nuevo usuario
        user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            username=user_data.username,
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def login_user(db: Session, username: str, password: str) -> tuple[User, str, str]:
        """Autentica un usuario y genera tokens"""
        # Buscar usuario
        user = db.query(User).filter(User.username == username).first()
        
        if not user or not user.is_active or not verify_password(password, user.password_hash):
            raise ValueError("Credenciales inválidas")
        
        # Actualizar último login
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        # Generar tokens
        access_token = create_access_token(
            data={"sub": user.id, "username": user.username, "role": user.role.value}
        )
        
        refresh_token = create_access_token(
            data={"sub": user.id, "type": "refresh"},
            expires_delta=timedelta(days=7)
        )
        
        return user, access_token, refresh_token
    
    @staticmethod
    def refresh_token(db: Session, refresh_token_str: str) -> str:
        """Genera un nuevo access token usando refresh token"""
        payload = verify_token(refresh_token_str)
        
        if payload.get("type") != "refresh":
            raise ValueError("Token inválido")
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise ValueError("Usuario no encontrado o inactivo")
        
        # Generar nuevo access token
        new_access_token = create_access_token(
            data={"sub": user.id, "username": user.username, "role": user.role.value}
        )
        
        return new_access_token
    
    @staticmethod
    def revoke_token(db: Session, token: str, user_id: str):
        """Revoca un token añadiéndolo a la blacklist"""
        payload = verify_token(token)
        expires_at = datetime.fromtimestamp(payload.get("exp"))
        
        blacklist_entry = TokenBlacklist(
            id=str(uuid.uuid4()),
            token=token,
            expires_at=expires_at
        )
        
        db.add(blacklist_entry)
        db.commit()
    
    @staticmethod
    def get_user(db: Session, user_id: str) -> User:
        """Obtiene un usuario por ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def is_token_revoked(db: Session, token: str) -> bool:
        """Verifica si un token está en la blacklist"""
        return db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first() is not None


