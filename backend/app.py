from flask import Flask
from flask_cors import CORS
from routes import contact_bp
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins=Config.ALLOWED_ORIGINS)
    app.register_blueprint(contact_bp)
    return app