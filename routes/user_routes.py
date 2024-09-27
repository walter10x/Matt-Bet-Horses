from flask import Blueprint, request, jsonify
from models.user_model import UserModel
from pymongo import MongoClient
from config import Config
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

import logging

user_routes = Blueprint('user_routes', __name__)

# Conexión a la base de datos
client = MongoClient(Config.MONGO_URI)
db = client['bet_db']
user_model = UserModel(db)

def handle_error(message, status_code):
    logging.error(f"Error: {message}")
    return jsonify({'error': message}), status_code

# Ruta para obtener la información del usuario
@user_routes.route('/user/<string:user_id>', methods=['GET'])
@jwt_required()  # Solo usuarios autenticados
def get_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return handle_error('Acceso denegado: No puedes ver la información de otro usuario.', 403)
        
        user = user_model.find_user_by_id(user_id)
        if not user:
            return handle_error('Usuario no encontrado', 404)
        
        return jsonify({'username': user['username'], 'email': user['email']}), 200

    except Exception as e:
        return handle_error(f"Error al obtener el usuario: {str(e)}", 500)

# Ruta para actualizar la información del usuario
@user_routes.route('/user/<string:user_id>', methods=['PUT'])
@jwt_required()  # Solo usuarios autenticados
def update_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return handle_error('Acceso denegado: No puedes actualizar la información de otro usuario.', 403)

        data = request.get_json()
        username = data.get('username')
        email = data.get('email')

        user = user_model.find_user_by_id(user_id)
        if not user:
            return handle_error('Usuario no encontrado', 404)

        updates = {}
        if username:
            updates['username'] = username
        if email:
            updates['email'] = email

        updated_user = user_model.update_user(user_id, updates)
        if not updated_user:
            return handle_error('No se pudo actualizar el usuario', 400)

        return jsonify({'message': 'Usuario actualizado exitosamente'}), 200

    except Exception as e:
        return handle_error(f"Error al actualizar el usuario: {str(e)}", 500)

# Ruta para eliminar un usuario
@user_routes.route('/user/<string:user_id>', methods=['DELETE'])
@jwt_required()  # Solo usuarios autenticados
def delete_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return handle_error('Acceso denegado: No puedes eliminar la cuenta de otro usuario.', 403)

        user = user_model.find_user_by_id(user_id)
        if not user:
            return handle_error('Usuario no encontrado', 404)

        user_model.delete_user(user_id)
        return jsonify({'message': 'Usuario eliminado exitosamente'}), 200

    except Exception as e:
        return handle_error(f"Error al eliminar el usuario: {str(e)}", 500)
    
    #ENDPOINT PARA EL CAMBIO DE CONTRASEÑA

@user_routes.route('/user/<string:user_id>/change-password', methods=['PUT'])
@jwt_required()
def change_password(user_id):
    try:
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({'error': 'No tienes permiso para cambiar la contraseña de este usuario'}), 403

        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        user = user_model.find_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        if not current_password or not new_password:
            return jsonify({'error': 'Ambas contraseñas son necesarias'}), 400
        
        if not check_password_hash(user['password'], current_password):
            return jsonify({'error': 'La contraseña actual es incorrecta'}), 401

        # Generar el hash para la nueva contraseña
        hashed_new_password = generate_password_hash(new_password)
        user_model.update_user(user_id, {'password': hashed_new_password})

        return jsonify({'message': 'Contraseña cambiada exitosamente'}), 200

    except Exception as e:
        return jsonify({'error': f'Ocurrió un error: {str(e)}'}), 500

