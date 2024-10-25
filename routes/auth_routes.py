from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from pymongo import MongoClient
from config import Config
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

auth_routes = Blueprint('auth_routes', __name__)

try:
    client = MongoClient(Config.MONGO_URI)
    db = client['bet_db']
    auth_service = AuthService(db)
except Exception as e:
    logging.error(f"Error al conectar con MongoDB: {str(e)}")
    raise

def handle_error(message, status_code):
    logging.error(f"Error: {message}")
    return jsonify({'error': message}), status_code

@auth_routes.route('/register', methods=['POST'])
@jwt_required(optional=True)
def register():
    try:
        data = request.get_json()
        if not data:
            return handle_error('No se recibieron datos', 400)
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        # Validar campos
        if not username or not email or not password:
            return handle_error('Faltan campos requeridos', 400)

        # Registrar el usuario utilizando AuthService
        user_id = auth_service.register_user(username, email, password, role)
        return jsonify({'message': 'Usuario registrado exitosamente', 'user_id': str(user_id)}), 201
    except ValueError as e:
        return handle_error(str(e), 400)
    except Exception as e:
        logging.error(f"Error inesperado: {str(e)}")
        return handle_error('Ocurrió un error interno del servidor', 500)

@auth_routes.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return handle_error('No se recibieron datos', 400)
        
        identifier = data.get('identifier')
        password = data.get('password')

        if not identifier or not password:
            return handle_error('Faltan campos requeridos', 400)

        # Intentar iniciar sesión utilizando AuthService
        access_token, user = auth_service.login_user(identifier, password)
        return jsonify({
            'message': 'Inicio de sesión exitoso',
            'access_token': access_token,
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'role': user['role']
            }
        }), 200
    except ValueError as e:
        return handle_error(str(e), 401)
    except Exception as e:
        logging.error(f"Error inesperado en login: {str(e)}")
        return handle_error('Ocurrió un error interno del servidor', 500)
