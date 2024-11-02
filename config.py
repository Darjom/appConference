import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mi_secreto'  # Cambia a una clave segura en producción
