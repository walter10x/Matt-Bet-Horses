from flask import Flask
from pymongo import MongoClient
from config import Config
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
import os
from routes.auth_routes import auth_routes
from routes.user_routes import user_routes
from routes.betting_center_routes import betting_center_routes
from routes.taquilla_routes import taquilla_routes
from routes.role_default_permissions_routes import role_default_permissions_routes
from routes.configuration_routes import configuration_routes
from routes.permission_routes import permission_routes
from flask_cors import CORS
import logging
from models.role_default_permissions_model import RoleDefaultPermissionsModel
from models.permission_model import (
    PermissionModel,
)  # Asegúrate de importar tu modelo de permisos


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
client = MongoClient(app.config["MONGO_URI"])
db = client.get_database()

# Inicializar el modelo de permisos
role_permissions_model = RoleDefaultPermissionsModel(db)

# Verificar y inicializar permisos predeterminados
try:
    existing_permissions = role_permissions_model.get_all_role_permissions()
    if not existing_permissions:
        logging.info("Inicializando permisos predeterminados...")
        role_permissions_model.initialize_default_permissions()
    else:
        logging.info(
            "Los permisos predeterminados ya existen, no es necesario inicializar."
        )
except Exception as e:
    logging.error(f"Error al inicializar permisos: {e}")

    # Inicializar permisos generales
permission_model = PermissionModel(db)

# Verificar y cargar los permisos generales
try:
    existing_permissions = permission_model.get_all_permissions()
    if not existing_permissions:
        logging.info("Inicializando permisos generales...")
        permission_model.initialize_permissions()  # Esta función debe cargar los permisos generales
    else:
        logging.info("Los permisos generales ya existen, no es necesario inicializar.")
except Exception as e:
    logging.error(f"Error al inicializar los permisos generales: {e}")

# Registrar las rutas de la aplicación
app.register_blueprint(auth_routes)
app.register_blueprint(user_routes)
app.register_blueprint(betting_center_routes)
app.register_blueprint(taquilla_routes)
app.register_blueprint(role_default_permissions_routes)
app.register_blueprint(configuration_routes)
app.register_blueprint(permission_routes)


# Ruta de ejemplo para verificar que la aplicación está corriendo
@app.route("/")
def home():
    return "¡La aplicación está funcionando correctamente!"


if __name__ == "__main__":
    app.run(debug=True)
