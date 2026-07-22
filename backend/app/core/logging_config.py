from typing import Dict, Any

def get_logging_config(log_level: str) -> Dict[str, Any]:
    """
    Retourne la configuration de logging structurée sous forme de dictionnaire.
    Cette configuration peut être passée à logging.config.dictConfig.
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(levelname)s - %(name)s - [%(filename)s:%(lineno)d] - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": '{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "file": "%(filename)s", "line": %(lineno)d, "message": "%(message)s"}'
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console"],
                "level": log_level,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
            "meeting_ai": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            }
        }
    }
