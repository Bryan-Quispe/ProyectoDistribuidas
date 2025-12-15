"""Logging centralizado para microservicios"""
import logging
import json
from datetime import datetime
from typing import Optional
import sys

class JSONFormatter(logging.Formatter):
    """Formateador de logs en JSON"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
            "path": record.pathname,
            "line": record.lineno,
        }
        
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logger(name: str, level=logging.INFO):
    """Configura un logger con formato JSON"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    formatter = JSONFormatter()
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger


def log_request(logger: logging.Logger, method: str, uri: str, 
                status_code: int, user_id: Optional[str] = None):
    """Registra información de una solicitud HTTP"""
    extra = {}
    if user_id:
        extra['user_id'] = user_id
    
    logger.info(f"HTTP {method} {uri} - Status: {status_code}", extra=extra)
