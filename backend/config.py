# Copyright (c) 2026 Mauro Nolan Fernández. Todos los derechos reservados.
import os
from dotenv import load_dotenv

load_dotenv(override=False)


def _origins(raw: str) -> list[str]:
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


class Config:
    DEBUG = False
    TESTING = False
    LOG_LEVEL = "WARNING"
    LOG_FORMAT = "json"

    BREVO_API_KEY = os.getenv("BREVO_API_KEY")
    MAIL_FROM = os.getenv("MAIL_FROM")
    MAIL_TO = os.getenv("MAIL_TO")
    ALLOWED_ORIGINS = _origins(os.getenv("ALLOWED_ORIGINS", ""))
    TRUST_PROXY = os.getenv("TRUST_PROXY", "false").lower() == "true"

    REQUIRED = ("BREVO_API_KEY", "MAIL_FROM", "MAIL_TO", "ALLOWED_ORIGINS")

    @classmethod
    def validate(cls):
        """Falla al arrancar si falta configuración crítica."""
        missing = [key for key in cls.REQUIRED if not getattr(cls, key)]
        if missing:
            raise RuntimeError(
                f"Faltan variables de entorno obligatorias: {', '.join(missing)}"
            )


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "text"


class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    TESTING = True
    LOG_LEVEL = "DEBUG"
    LOG_FORMAT = "text"

    BREVO_API_KEY = "fake-api-key"
    MAIL_FROM = "test@example.com"
    MAIL_TO = "test@example.com"
    ALLOWED_ORIGINS = ["http://localhost:5500"]


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}