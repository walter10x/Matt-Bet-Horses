import os
from dotenv import load_dotenv
from datetime import timedelta  # Importa timedelta

# Cargar las variables de entorno desde .env
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    MONGO_URI = os.getenv('MONGODB_URI')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # Cambia esto a tu variable de entorno si la tienes

    # Configuración de la duración de los tokens
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # Duración del token de acceso
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # Duración del token de refresco
