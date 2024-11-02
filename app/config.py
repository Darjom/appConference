from flask import Flask
from .routes import app as app_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Registrar rutas
    app.register_blueprint(app_routes)

    return app
