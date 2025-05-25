from flask import Flask
from app.routes import evaluation_routes
from backend.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(evaluation_routes, url_prefix='/evaluacion')

    return app