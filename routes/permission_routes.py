from flask import Blueprint, request, jsonify
from services.permission_service import PermissionService
from pymongo import MongoClient
from config import Config
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

permission_routes = Blueprint("permission_routes", __name__)

# Conexión a la base de datos
client = MongoClient(Config.MONGO_URI)
db = client["bet_db"]
permission_service = PermissionService(db)


def handle_error(message, status_code):
    logging.error(f"Error: {message}")
    return jsonify({"error": message}), status_code


@permission_routes.route("/permissions/assign", methods=["POST"])
@jwt_required()
def assign_permission():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        user_id = data.get("user_id")
        permission_id = data.get("permission_id")

        if not user_id or not permission_id:
            return handle_error(
                "El ID del usuario y el ID del permiso son requeridos", 400
            )

        permission_service.assign_permission_to_user(
            current_user, user_id, permission_id
        )
        return jsonify({"message": "Permiso asignado exitosamente"}), 200

    except Exception as e:
        return handle_error(f"Error al asignar permiso: {str(e)}", 500)


@permission_routes.route("/permissions/revoke", methods=["POST"])
@jwt_required()
def revoke_permission():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        user_id = data.get("user_id")
        permission_id = data.get("permission_id")

        if not user_id or not permission_id:
            return handle_error(
                "El ID del usuario y el ID del permiso son requeridos", 400
            )

        permission_service.remove_permission_from_user(
            current_user, user_id, permission_id
        )
        return jsonify({"message": "Permiso revocado exitosamente"}), 200

    except Exception as e:
        return handle_error(f"Error al revocar permiso: {str(e)}", 500)


@permission_routes.route("/permissions/<string:user_id>", methods=["GET"])
@jwt_required()
def get_user_permissions(user_id):
    try:
        current_user = get_jwt_identity()

        # Permitir que solo el super_admin o el propio usuario vean sus permisos
        if current_user["role"] != "super_admin" and current_user["id"] != user_id:
            return handle_error(
                "Acceso denegado: No tienes permiso para ver estos datos", 403
            )

        permissions = permission_service.get_user_permissions(user_id)
        return jsonify(permissions), 200

    except Exception as e:
        return handle_error(f"Error al obtener permisos del usuario: {str(e)}", 500)


# Ruta para obtener todos los permisos disponibles
@permission_routes.route("/permissions", methods=["GET"])
@jwt_required()
def get_all_permissions():
    try:
        current_user = get_jwt_identity()

        # Solo el super_admin puede ver todos los permisos
        if current_user["role"] != "super_admin":
            return handle_error(
                "Acceso denegado: solo los super administradores pueden ver todos los permisos",
                403,
            )

        permissions = permission_service.permission_model.get_all_permissions()
        return (
            jsonify(
                [
                    permission_service.permission_model.serialize(permission)
                    for permission in permissions
                ]
            ),
            200,
        )

    except Exception as e:
        return handle_error(f"Error al obtener todos los permisos: {str(e)}", 500)
