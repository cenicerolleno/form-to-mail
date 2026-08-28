import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = False
    BREVO_API_KEY = os.getenv("BREVO_API_KEY")
    MAIL_FROM = os.getenv("MAIL_FROM")
    MAIL_TO = os.getenv("MAIL_TO")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
    LOG_LEVEL = "WARNING"
    LOG_FORMAT = "json"
    
class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "text"
    
class ProductionConfig(Config):
    pass
    
class TestingConfig(Config):
    TESTING = True
    BREVO_API_KEY = "fake-api-key" 
    MAIL_FROM = "test@example.com"
    MAIL_TO = "test@example.com"
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
    ]
    LOG_LEVEL = "DEBUG"

config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}