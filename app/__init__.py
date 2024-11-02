from flask import Flask
from .routes import app_routes  # Importa el blueprint de routes.py

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Registra el blueprint en la aplicación
    app.register_blueprint(app_routes)

    return app

