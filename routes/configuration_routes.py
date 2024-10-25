from flask import Blueprint, request, jsonify
from models.configuration_model import ConfigurationModel
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.betting_center_model import BettingCenterModel
from pymongo import MongoClient
from config import Config
import logging

configuration_routes = Blueprint('configuration_routes', __name__)

client = MongoClient(Config.MONGO_URI)
db = client['bet_db']
config_model = ConfigurationModel(db)

def handle_error(message, status_code):
    logging.error(f"Error: {message}")
    return jsonify({'error': message}), status_code

@configuration_routes.route('/configuration/<string:center_id>', methods=['POST'])
@jwt_required()
def create_configuration(center_id):
    try:
        current_user = get_jwt_identity()
        if current_user['role'] not in ['super_admin', 'admin_centro']:
            return handle_error('No tienes permiso para crear configuraciones', 403)

        data = request.get_json()
        config_id = config_model.create_configuration(center_id, data)
        return jsonify({'message': 'Configuración creada exitosamente', 'id': str(config_id)}), 201
    except Exception as e:
        return handle_error(f"Error al crear la configuración: {str(e)}", 500)

@configuration_routes.route('/configuration/<string:center_id>', methods=['GET'])
@jwt_required()
def get_configuration(center_id):
    try:
        current_user = get_jwt_identity()
        if current_user['role'] not in ['super_admin', 'admin_centro']:
            return handle_error('No tienes permiso para ver configuraciones', 403)

        config = config_model.get_configuration(center_id)
        if not config:
            return handle_error('Configuración no encontrada', 404)
        return jsonify(config), 200
    except Exception as e:
        return handle_error(f"Error al obtener la configuración: {str(e)}", 500)

@configuration_routes.route('/configuration/<string:center_id>', methods=['PUT'])
@jwt_required()
def update_configuration(center_id):
    try:
        current_user = get_jwt_identity()
        if current_user['role'] not in ['super_admin', 'admin_centro']:
            return handle_error('No tienes permiso para actualizar configuraciones', 403)

        data = request.get_json()
        result = config_model.update_configuration(center_id, data)
        if result.modified_count:
            return jsonify({'message': 'Configuración actualizada exitosamente'}), 200
        return handle_error('No se encontró la configuración para actualizar', 404)
    except Exception as e:
        return handle_error(f"Error al actualizar la configuración: {str(e)}", 500)

@configuration_routes.route('/configuration/<string:center_id>', methods=['DELETE'])
@jwt_required()
def delete_configuration(center_id):
    try:
        current_user = get_jwt_identity()
        if current_user['role'] != 'super_admin':
            return handle_error('Solo el super administrador puede eliminar configuraciones', 403)

        result = config_model.delete_configuration(center_id)
        if result.deleted_count:
            return jsonify({'message': 'Configuración eliminada exitosamente'}), 200
        return handle_error('No se encontró la configuración para eliminar', 404)
    except Exception as e:
        return handle_error(f"Error al eliminar la configuración: {str(e)}", 500)