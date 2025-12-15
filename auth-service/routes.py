"""API endpoints para AuthService"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auth_service.models import User
from auth_service.schemas import (
    UserRegister, UserLogin, TokenResponse, UserResponse, RefreshTokenRequest
)
from auth_service.service import AuthService
from shared.database import get_db
from shared.jwt_utils import verify_token
from shared.logger import setup_logger, log_request

router = APIRouter()
logger = setup_logger("auth-service")


@router.post("/register", response_model=UserResponse, tags=["Authentication"])
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema.
    
    - **email**: Email único del usuario
    - **username**: Nombre de usuario único
    - **password**: Contraseña (mínimo 6 caracteres)
    - **full_name**: Nombre completo (opcional)
    - **role**: Rol del usuario (CLIENTE, REPARTIDOR, SUPERVISOR, ADMIN)
    """
    try:
        user = AuthService.register_user(db, user_data)
        log_request(logger, "POST", "/register", 201, None)
        return user
    except ValueError as e:
        log_request(logger, "POST", "/register", 400, None)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        log_request(logger, "POST", "/register", 500, None)
        logger.error(f"Error en registro: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error en registro")


@router.post("/login", response_model=TokenResponse, tags=["Authentication"])
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Autentica un usuario y retorna tokens JWT.
    
    - **username**: Nombre de usuario
    - **password**: Contraseña
    
    Retorna:
    - **access_token**: Token JWT para acceso a recursos protegidos
    - **refresh_token**: Token para renovar el access_token
    - **expires_in**: Tiempo de expiración en segundos (1800 = 30 minutos)
    """
    try:
        user, access_token, refresh_token = AuthService.login_user(
            db, credentials.username, credentials.password
        )
        log_request(logger, "POST", "/login", 200, user.id)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800
        )
    except ValueError as e:
        log_request(logger, "POST", "/login", 401, None)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        log_request(logger, "POST", "/login", 500, None)
        logger.error(f"Error en login: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error en autenticación")


@router.post("/token/refresh", response_model=TokenResponse, tags=["Authentication"])
async def refresh_access_token(request_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Genera un nuevo access token usando el refresh token.
    
    - **refresh_token**: Token de renovación obtenido en el login
    
    Retorna un nuevo access_token válido
    """
    try:
        new_access_token = AuthService.refresh_token(db, request_data.refresh_token)
        
        # Decodificar para obtener user_id
        payload = verify_token(request_data.refresh_token)
        user_id = payload.get("sub")
        
        log_request(logger, "POST", "/token/refresh", 200, user_id)
        return TokenResponse(
            access_token=new_access_token,
            expires_in=1800
        )
    except ValueError as e:
        log_request(logger, "POST", "/token/refresh", 401, None)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        log_request(logger, "POST", "/token/refresh", 500, None)
        logger.error(f"Error en refresh token: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error en renovación de token")


@router.post("/token/revoke", tags=["Authentication"])
async def revoke_token(request: Request, db: Session = Depends(get_db)):
    """
    Revoca un token agregándolo a la lista negra.
    Requiere autenticación con JWT en el header Authorization.
    """
    try:
        # Extraer token del header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise ValueError("No se proporcionó token")
        
        token = auth_header.split(" ")[1]
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        AuthService.revoke_token(db, token, user_id)
        log_request(logger, "POST", "/token/revoke", 200, user_id)
        
        return {"message": "Token revocado exitosamente"}
    except ValueError as e:
        log_request(logger, "POST", "/token/revoke", 401, None)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        log_request(logger, "POST", "/token/revoke", 500, None)
        logger.error(f"Error en revoke token: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error en revocación de token")


@router.get("/me", response_model=UserResponse, tags=["Users"])
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Obtiene la información del usuario autenticado.
    Requiere autenticación con JWT en el header Authorization.
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise ValueError("No se proporcionó token")
        
        token = auth_header.split(" ")[1]
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        user = AuthService.get_user(db, user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        log_request(logger, "GET", "/me", 200, user_id)
        return user
    except ValueError as e:
        log_request(logger, "GET", "/me", 401, None)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        log_request(logger, "GET", "/me", 500, None)
        logger.error(f"Error obteniendo usuario actual: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error obteniendo usuario")
