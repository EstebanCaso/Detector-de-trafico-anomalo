"""
Configuración de logging para toda la aplicación
"""

import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging(name, log_file=None, level=logging.INFO):
    """
    Configura logging para un módulo
    
    Args:
        name: Nombre del módulo
        log_file: Ruta del archivo de log (opcional)
        level: Nivel de logging
        
    Returns:
        Logger configurado
    """
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Formato de logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        os.makedirs(os.path.dirname(log_file) or '.', exist_ok=True)
        
        # Crear nombre de archivo con timestamp
        log_name = f"{os.path.splitext(log_file)[0]}_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_name,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
