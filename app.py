from flask import Flask
from pymongo import MongoClient
from config import Config
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
import os
from routes.auth_routes import auth_routes
from routes.user_routes import user_routes
from flask_cors import CORS
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Crear la aplicación Flask
app = Flask(__name__)

# Aplicar configuración desde config.py
app.config.from_object(Config)

# Configurar JWT
jwt = JWTManager(app)

# Configurar CORS
CORS(app)

# Conexión a MongoDB usando la URI de las variables de entorno
client = MongoClient(app.config['MONGO_URI'])
db = client.get_database()

# Registrar las rutas de autenticación
app.register_blueprint(auth_routes)
app.register_blueprint(user_routes)

# Ruta de ejemplo para verificar que la aplicación está corriendo
@app.route('/')
def home():
    return "¡La aplicación está funcionando correctamente!"

if __name__ == '__main__':
    app.run(debug=True)