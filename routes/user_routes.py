from flask import Blueprint, request, jsonify
from services.user_service import UserService
from pymongo import MongoClient
from config import Config
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import logging

user_routes = Blueprint("user_routes", __name__)

# Conexión a la base de datos
client = MongoClient(Config.MONGO_URI)
db = client["bet_db"]
user_service = UserService(db)


def handle_error(message, status_code):
    logging.error(f"Error: {message}")
    return jsonify({"error": message}), status_code


@user_routes.route("/user/<string:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    try:
        current_user = get_jwt_identity()
        if current_user["role"] == "super_admin" or current_user["id"] == user_id:
            user = user_service.get_user_by_id(user_id)
            if not user:
                return handle_error("Usuario no encontrado", 404)
            return jsonify(user_service.serialize(user)), 200
        elif current_user["role"] == "admin_centro":
            # Admin Centro puede ver usuarios de sus centros asignados
            if user_service.is_center_admin(current_user["id"], user_id):
                user = user_service.get_user_by_id(user_id)
                if not user:
                    return handle_error("Usuario no encontrado", 404)
                return jsonify(user_service.serialize(user)), 200
        return handle_error("Acceso denegado", 403)
    except Exception as e:
        return handle_error(f"Error al obtener el usuario: {str(e)}", 500)


@user_routes.route("/users", methods=["GET"])
@jwt_required()
def get_all_users():
    try:
        current_user = get_jwt_identity()
        if current_user["role"] == "super_admin":
            users = user_service.get_all_users(current_user)
            user_list = [user_service.serialize(user) for user in users]
            return jsonify(user_list), 200
        elif current_user["role"] == "admin_centro":
            users = user_service.get_all_users(current_user)
            user_list = [user_service.serialize(user) for user in users]
            return jsonify(user_list), 200
        else:
            return handle_error(
                "Acceso denegado: no tienes permiso para ver todos los usuarios", 403
            )
    except Exception as e:
        return handle_error(f"Error al obtener todos los usuarios: {str(e)}", 500)


@user_routes.route("/user/<string:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    try:
        current_user = get_jwt_identity()
        if (
            current_user["role"] == "super_admin"
            or (
                current_user["role"] == "admin_centro"
                and user_service.is_center_admin(current_user["id"], user_id)
            )
            or current_user["id"] == user_id
        ):
            data = request.get_json()
            updated_user = user_service.update_user(user_id, data)
            if not updated_user:
                return handle_error("No se pudo actualizar el usuario", 400)
            return jsonify({"message": "Usuario actualizado exitosamente"}), 200
        return handle_error("Acceso denegado", 403)
    except Exception as e:
        return handle_error(f"Error al actualizar el usuario: {str(e)}", 500)


@user_routes.route("/user/<string:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    try:
        current_user = get_jwt_identity()
        if current_user["role"] == "super_admin":
            user = user_service.get_user_by_id(user_id)
            if not user:
                return handle_error("Usuario no encontrado", 404)
            user_service.delete_user(user_id)
            return jsonify({"message": "Usuario eliminado exitosamente"}), 200
        return handle_error(
            "Acceso denegado: Solo el super administrador puede eliminar usuarios.", 403
        )
    except Exception as e:
        return handle_error(f"Error al eliminar usuario: {str(e)}", 500)


@user_routes.route("/user/<string:user_id>/change-password", methods=["PUT"])
@jwt_required()
def change_password(user_id):
    try:
        current_user = get_jwt_identity()
        if (
            current_user["role"] == "super_admin"
            or (
                current_user["role"] == "admin_centro"
                and user_service.is_center_admin(current_user["id"], user_id)
            )
            or current_user["id"] == user_id
        ):
            data = request.get_json()
            current_password = data.get("current_password")
            new_password = data.get("new_password")
            user = user_service.get_user_by_id(user_id)
            if not user:
                return handle_error("Usuario no encontrado", 404)
            if not new_password:
                return handle_error("La nueva contraseña es necesaria", 400)
            if (
                current_user["role"] in ["super_admin", "admin_centro"]
                and current_user["id"] != user_id
            ):
                hashed_new_password = generate_password_hash(new_password)
                user_service.update_user(user_id, {"password": hashed_new_password})
                return (
                    jsonify(
                        {
                            "message": "Contraseña cambiada exitosamente por el administrador"
                        }
                    ),
                    200,
                )
            if not current_password:
                return handle_error("La contraseña actual es necesaria", 400)
            if not check_password_hash(user["password"], current_password):
                return handle_error("La contraseña actual es incorrecta", 401)
            hashed_new_password = generate_password_hash(new_password)
            user_service.update_user(user_id, {"password": hashed_new_password})
            return jsonify({"message": "Contraseña cambiada exitosamente"}), 200
        else:
            return handle_error(
                "No tienes permiso para cambiar la contraseña de este usuario", 403
            )
    except Exception as e:
        return handle_error(f"Ocurrió un error al cambiar la contraseña: {str(e)}", 500)
