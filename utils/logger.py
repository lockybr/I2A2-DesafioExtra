"""
Configuração de logging para o EDA Agent.
"""

import logging
from config.settings import settings

def setup_logging():
    """
    Configura o sistema de logging da aplicação.
    
    Returns:
        logging.Logger: Logger configurado
    """
    logging.basicConfig(
        level=getattr(logging, settings.LOGGING_CONFIG["level"]),
        format=settings.LOGGING_CONFIG["format"]
    )
    
    logger = logging.getLogger("eda_agent")
    
    # Configurar níveis específicos para bibliotecas externas
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    logger.info("Logging system configured")
    return logger
