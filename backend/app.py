from flask import Flask
from flask_cors import CORS
from routes import contact_bp
from config import Config
from logging_config import setup_logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    setup_logging(app)
    app.logger.info("Aplicación iniciada")
    CORS(app, origins=Config.ALLOWED_ORIGINS)
    app.register_blueprint(contact_bp)
    return app