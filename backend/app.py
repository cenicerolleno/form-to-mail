import os
from flask import Flask
from flask_cors import CORS
from routes import contact_bp
from config import Config, config_by_name
from logging_config import setup_logging

def create_app():
    app = Flask(__name__)
    env = os.getenv("FLASK_ENV", "development")
    config = config_by_name[env]         
    app.config.from_object(config)
    setup_logging(app)
    app.logger.info("Aplicación iniciada")
    CORS(app, origins=config.ALLOWED_ORIGINS)
    app.register_blueprint(contact_bp)
    return app