"""
Tests unitaires — Logger Central.
Vérifie que le logger 'meeting_ai' est correctement configuré et fonctionnel.
"""
import logging
import pytest
from app.core.logger import logger


class TestLogger:
    """Tests du logger central de l'application."""

    def test_logger_exists(self):
        """Le module logger doit exporter un objet logger."""
        assert logger is not None

    def test_logger_name_is_correct(self):
        """Le logger doit avoir le nom 'meeting_ai'."""
        assert logger.name == "meeting_ai"

    def test_logger_has_valid_level(self):
        """Le logger doit avoir un niveau de log valide."""
        valid_levels = {
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        }
        # Un niveau NOTSET (0) est valide si le handler parent gère le niveau
        assert logger.level in valid_levels or logger.level == logging.NOTSET

    def test_logger_is_python_logger_instance(self):
        """Le logger doit être une instance de logging.Logger."""
        assert isinstance(logger, logging.Logger)

    def test_logger_can_log_info(self):
        """Le logger ne doit pas lever d'exception lors d'un log INFO."""
        try:
            logger.info("[Test] Message de test INFO")
        except Exception as exc:
            pytest.fail(f"logger.info() a levé une exception : {exc}")

    def test_logger_can_log_error(self):
        """Le logger ne doit pas lever d'exception lors d'un log ERROR."""
        try:
            logger.error("[Test] Message de test ERROR")
        except Exception as exc:
            pytest.fail(f"logger.error() a levé une exception : {exc}")
