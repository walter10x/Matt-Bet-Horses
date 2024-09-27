from flask import Blueprint, request, jsonify
from models.user_model import UserModel
from pymongo import MongoClient
from config import Config
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import logging

auth_routes = Blueprint('auth_routes', __name__)

client = MongoClient(Config.MONGO_URI)
db = client['bet_db']
user_model = UserModel(db)

def handle_error(message, status_code):
    logging.error(f"Error: {message}")
    return jsonify({'error': message}), status_code

@auth_routes.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return handle_error('No se recibieron datos', 400)
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return handle_error('Faltan campos requeridos', 400)
        
        if user_model.find_user_by_email(email):
            return handle_error('Email ya registrado', 400)

        user_id = user_model.create_user(username, email, password)
        logging.info(f"Usuario registrado: {email}")
        return jsonify({'message': 'Usuario registrado exitosamente', 'user_id': str(user_id)}), 201

    except Exception as e:
        return handle_error(f'Ocurrió un error: {str(e)}', 500)

@auth_routes.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return handle_error('No se recibieron datos', 400)
        
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return handle_error('Faltan campos requeridos', 400)

        user = user_model.find_user_by_email(email)
        if not user or not user_model.verify_password(user, password):
            return handle_error('Credenciales inválidas', 401)

        access_token = create_access_token(identity=str(user['_id']))
        logging.info(f"Inicio de sesión exitoso: {email}")
        return jsonify({
            'message': 'Inicio de sesión exitoso',
            'access_token': access_token,
            'user': user_model.serialize(user)
        }), 200

    except Exception as e:
        return handle_error(f'Ocurrió un error: {str(e)}', 500)

@auth_routes.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    try:
        current_user_id = get_jwt_identity()
        logging.info(f"Accediendo a ruta protegida. Usuario ID: {current_user_id}")
        user = user_model.find_user_by_id(current_user_id)
        if not user:
            return handle_error("Usuario no encontrado", 404)
        return jsonify(logged_in_as=user_model.serialize(user)), 200
    except Exception as e:
        return handle_error(f"Error al acceder a la ruta protegida: {str(e)}", 500)