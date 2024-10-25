# routes/betting_center_routes.py

from flask import Blueprint, request, jsonify
from services.betting_center_service import BettingCenterService
from pymongo import MongoClient
from config import Config
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

# Asegúrate de importar los modelos necesarios
from models.user_model import UserModel
from models.taquilla_model import TaquillaModel
from models.betting_center_model import BettingCenterModel

betting_center_routes = Blueprint("betting_center_routes", __name__)

# Conexión a la base de datos
client = MongoClient(Config.MONGO_URI)
db = client["bet_db"]

# Crear instancias de los modelos
user_model = UserModel(db)
taquilla_model = TaquillaModel(db)
betting_center_model = BettingCenterModel(db, user_model, taquilla_model)

# Pasar el modelo de usuario y taquilla al servicio
betting_center_service = BettingCenterService(db)


def handle_error(message, status_code):
    logging.error(f"Error: {message}")
    return jsonify({"error": message}), status_code


@betting_center_routes.route("/betting-centers", methods=["POST"])
@jwt_required()
def create_betting_center():
    try:
        current_user = get_jwt_identity()
        if current_user["role"] != "super_admin":
            return handle_error(
                "Acceso denegado: se requiere rol de super administrador", 403
            )

        data = request.get_json()
        name = data.get("name")
        address = data.get("address")
        admin_id = data.get("admin_id")

        if not name or not address or not admin_id:
            return handle_error(
                "El nombre, la dirección y el ID del administrador son requeridos", 400
            )

        # Verificar que el admin_id corresponde a un usuario con rol 'admin_centro'
        admin_user = user_model.find_user_by_id(admin_id)
        if not admin_user or admin_user.get("role") != "admin_centro":
            return handle_error(
                "El ID de administrador proporcionado no es válido", 400
            )

        center_id = betting_center_service.create_betting_center(
            name, address, admin_id
        )
        return (
            jsonify(
                {
                    "message": "Centro de apuestas creado exitosamente",
                    "id": str(center_id),
                }
            ),
            201,
        )

    except Exception as e:
        return handle_error(f"Error al crear el centro de apuestas: {str(e)}", 500)


@betting_center_routes.route("/betting-centers", methods=["GET"])
@jwt_required()
def get_all_betting_centers():
    try:
        current_user = get_jwt_identity()
        if current_user["role"] == "super_admin":
            centers = betting_center_service.get_all_centers()
        elif current_user["role"] == "admin_centro":
            centers = betting_center_service.get_centers_by_admin(current_user["id"])
        else:
            return handle_error("Acceso denegado", 403)

        center_list = [
            betting_center_service.serialize_betting_center(center)
            for center in centers
        ]
        return jsonify(center_list), 200

    except Exception as e:
        return handle_error(f"Error al obtener los centros de apuestas: {str(e)}", 500)


# routes/betting_center_routes.py
@betting_center_routes.route("/betting-centers/<string:center_id>", methods=["GET"])
@jwt_required()
def get_betting_center(center_id):
    try:
        current_user = get_jwt_identity()
        center = betting_center_service.get_betting_center_with_details(center_id)

        if not center:
            return handle_error("Centro de apuestas no encontrado", 404)

        if (
            current_user["role"] != "super_admin"
            and str(center["admin_id"]) != current_user["id"]
        ):
            return handle_error("Acceso denegado", 403)

        return jsonify(center), 200

    except Exception as e:
        return handle_error(f"Error al obtener el centro de apuestas: {str(e)}", 500)


@betting_center_routes.route("/betting-centers/<string:center_id>", methods=["PUT"])
@jwt_required()
def update_betting_center(center_id):
    try:
        current_user = get_jwt_identity()
        center = betting_center_service.get_betting_center_by_id(center_id)

        if not center:
            return handle_error("Centro de apuestas no encontrado", 404)

        if (
            current_user["role"] != "super_admin"
            and str(center["admin_id"]) != current_user["id"]
        ):
            return handle_error("Acceso denegado", 403)

        data = request.get_json()
        updates = {}
        if "name" in data:
            updates["name"] = data["name"]
        if "address" in data:
            updates["address"] = data["address"]

        success = betting_center_service.update_betting_center(center_id, updates)
        if not success:
            return handle_error("No se pudo actualizar el centro de apuestas", 400)

        return jsonify({"message": "Centro de apuestas actualizado exitosamente"}), 200

    except Exception as e:
        return handle_error(f"Error al actualizar el centro de apuestas: {str(e)}", 500)

    # ASIGNAR UN SUUARIO A UN ADMIN


@betting_center_routes.route(
    "/betting-centers/<string:center_id>/assign-users", methods=["POST"]
)
@jwt_required()
def assign_users_to_admin(center_id):
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        user_id = data.get("user_id")

        if not user_id:
            return handle_error("Se requiere un user_id para asignar", 400)

        success = betting_center_service.assign_user_to_admin(
            center_id, user_id, current_user["id"], current_user["role"]
        )

        if success:
            return (
                jsonify(
                    {"message": "Usuario asignado exitosamente al centro de apuestas"}
                ),
                200,
            )
        else:
            return handle_error(
                "No se pudo asignar el usuario al centro de apuestas", 400
            )

    except Exception as e:
        return handle_error(
            f"Error al asignar usuarios al administrador del centro de apuestas: {str(e)}",
            500,
        )


@betting_center_routes.route(
    "/betting-centers/<string:center_id>/manage-permissions", methods=["POST"]
)
@jwt_required()
def manage_user_permissions(center_id):
    try:
        current_user = get_jwt_identity()
        if current_user["role"] not in ["admin_centro", "super_admin"]:
            return handle_error(
                "Acceso denegado: solo los administradores de centros pueden gestionar permisos",
                403,
            )

        data = request.get_json()
        user_id = data.get("user_id")
        permissions = data.get("permissions")  # Espera una lista de permisos

        if not user_id or permissions is None:
            return handle_error(
                "Se requiere el ID del usuario y la lista de permisos", 400
            )

        # Si es admin_centro, verificar que el centro de apuestas pertenece a él
        if current_user["role"] == "admin_centro":
            if betting_center_service.get_center_admin(center_id) != current_user["id"]:
                return handle_error(
                    "Acceso denegado: no eres el administrador de este centro de apuestas",
                    403,
                )

        # Lógica para gestionar permisos del usuario
        success = betting_center_service.manage_user_permissions(user_id, permissions)
        if not success:
            return handle_error("No se pudo gestionar los permisos del usuario", 400)

        return jsonify({"message": "Permisos gestionados exitosamente"}), 200

    except Exception as e:
        return handle_error(f"Error al gestionar permisos del usuario: {str(e)}", 500)


@betting_center_routes.route("/betting-centers/<string:center_id>", methods=["DELETE"])
@jwt_required()
def delete_betting_center(center_id):
    try:
        current_user = get_jwt_identity()
        if current_user["role"] != "super_admin":
            return handle_error(
                "Acceso denegado: se requiere rol de super administrador", 403
            )

        success = betting_center_service.delete_betting_center(center_id)
        if not success:
            return handle_error("Centro de apuestas no encontrado", 404)

        return jsonify({"message": "Centro de apuestas eliminado exitosamente"}), 200

    except Exception as e:
        return handle_error(f"Error al eliminar el centro de apuestas: {str(e)}", 500)


@betting_center_routes.route(
    "/betting-centers/<string:center_id>/change-admin", methods=["POST"]
)
@jwt_required()
def change_center_admin(center_id):
    try:
        current_user = get_jwt_identity()
        if current_user["role"] != "super_admin":
            return handle_error(
                "Acceso denegado: se requiere rol de super administrador", 403
            )

        data = request.get_json()
        new_admin_id = data.get("new_admin_id")
        if not new_admin_id:
            return handle_error("Se requiere el ID del nuevo administrador", 400)

        # Verificar que el nuevo_admin_id corresponde a un usuario con rol 'admin_centro'
        new_admin = user_model.find_user_by_id(new_admin_id)
        if not new_admin or new_admin.get("role") != "admin_centro":
            return handle_error("El ID del nuevo administrador no es válido", 400)

        success = betting_center_service.change_admin(center_id, new_admin_id)
        if not success:
            return handle_error(
                "No se pudo cambiar el administrador del centro de apuestas", 400
            )

        # Actualizar la asignación de centros para el nuevo y antiguo administrador
        old_admin_id = betting_center_service.get_center_admin(center_id)
        if old_admin_id:
            betting_center_service.user_model.unassign_center(old_admin_id, center_id)
        betting_center_service.user_model.assign_center(new_admin_id, center_id)

        return (
            jsonify(
                {
                    "message": "Administrador del centro de apuestas cambiado exitosamente"
                }
            ),
            200,
        )

    except Exception as e:
        return handle_error(
            f"Error al cambiar el administrador del centro de apuestas: {str(e)}", 500
        )
