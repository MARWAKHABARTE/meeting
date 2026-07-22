import logging
from logging.config import dictConfig
from .settings import settings
from .logging_config import get_logging_config

def setup_logging() -> None:
    """
    Initialise le système de logging à l'aide de dictConfig.
    Cette fonction est appelée au démarrage de l'application (main.py).
    """
    config = get_logging_config(settings.LOG_LEVEL)
    dictConfig(config)

# Logger global réutilisable dans l'ensemble de l'application
logger = logging.getLogger("meeting_ai")
