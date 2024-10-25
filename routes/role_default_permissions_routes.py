# routes/role_default_permissions_routes.py

from flask import Blueprint, request, jsonify
from services.role_default_permissions_service import RoleDefaultPermissionsService
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
from config import Config
import logging

role_default_permissions_routes = Blueprint("role_default_permissions_routes", __name__)

client = MongoClient(Config.MONGO_URI)
db = client["bet_db"]
role_permissions_service = RoleDefaultPermissionsService(db)


def handle_error(message, status_code):
    logging.error(f"Error: {message}")
    return jsonify({"error": message}), status_code


@role_default_permissions_routes.route("/role-permissions", methods=["GET"])
@jwt_required()
def get_all_role_permissions():
    try:
        current_user = get_jwt_identity()
        if current_user["role"] != "super_admin":
            return handle_error(
                "Acceso denegado: se requiere rol de super administrador", 403
            )

        permissions = role_permissions_service.get_all_role_permissions()
        return jsonify(permissions), 200
    except Exception as e:
        return handle_error(f"Error al obtener los permisos de roles: {str(e)}", 500)


@role_default_permissions_routes.route(
    "/role-permissions/<string:role>", methods=["GET"]
)
@jwt_required()
def get_role_permissions(role):
    try:
        current_user = get_jwt_identity()
        if current_user["role"] != "super_admin":
            return handle_error(
                "Acceso denegado: se requiere rol de super administrador", 403
            )

        permissions = role_permissions_service.get_default_permissions(role)
        return jsonify({"role": role, "permissions": permissions}), 200
    except Exception as e:
        return handle_error(f"Error al obtener los permisos del rol: {str(e)}", 500)


@role_default_permissions_routes.route(
    "/role-permissions/<string:role>", methods=["PUT"]
)
@jwt_required()
def update_role_permissions(role):
    try:
        current_user = get_jwt_identity()
        if current_user["role"] != "super_admin":
            return handle_error(
                "Acceso denegado: se requiere rol de super administrador", 403
            )

        data = request.get_json()
        permissions = data.get("permissions")
        if not permissions:
            return handle_error("Se requieren los permisos", 400)

        role_permissions_service.set_default_permissions(role, permissions)
        return jsonify({"message": "Permisos actualizados exitosamente"}), 200
    except Exception as e:
        return handle_error(f"Error al actualizar los permisos del rol: {str(e)}", 500)


@role_default_permissions_routes.route("/role-permissions/initialize", methods=["POST"])
@jwt_required()
def initialize_permissions():
    """Inicializa los permisos predeterminados para los roles."""
    try:
        current_user = get_jwt_identity()
        if current_user["role"] != "super_admin":
            return handle_error(
                "Acceso denegado: se requiere rol de super administrador", 403
            )

        role_permissions_service.initialize_default_permissions()
        return (
            jsonify({"message": "Permisos predeterminados inicializados exitosamente"}),
            200,
        )
    except Exception as e:
        return handle_error(f"Error al inicializar los permisos: {str(e)}", 500)
