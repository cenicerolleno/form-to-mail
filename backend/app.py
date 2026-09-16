import os
from flask import Flask
from flask_cors import CORS
from routes import contact_bp
from config import config_by_name
from logging_config import setup_logging


def create_app(config_name=None):
    env = config_name or os.getenv("FLASK_ENV", "development")
    config = config_by_name[env]
    config.validate()

    app = Flask(__name__)
    app.config.from_object(config)

    setup_logging(app)
    app.logger.info("Aplicación iniciada en modo %s", env)

    CORS(
        app,
        resources={r"/contact": {"origins": config.ALLOWED_ORIGINS}},
        methods=["POST"],
        allow_headers=["Content-Type"],
    )

    app.register_blueprint(contact_bp)

    return app