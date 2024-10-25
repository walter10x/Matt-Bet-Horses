from flask import Blueprint, request, jsonify
from services.taquilla_service import TaquillaService
from pymongo import MongoClient
from config import Config
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from bson import ObjectId

taquilla_routes = Blueprint("taquilla_routes", __name__)

# Conexión a la base de datos
client = MongoClient(Config.MONGO_URI)
db = client["bet_db"]
taquilla_service = TaquillaService(db)


def handle_error(message, status_code):
    logging.error(f"Error: {message}")
    return jsonify({"error": message}), status_code


@taquilla_routes.route("/taquillas", methods=["POST"])
@jwt_required()
def create_taquilla():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        number = data.get("number")
        betting_center_id = data.get("betting_center_id")

        if not number or not betting_center_id:
            return handle_error(
                "El número de taquilla y el ID del centro de apuestas son requeridos",
                400,
            )

        if current_user["role"] == "super_admin" or (
            current_user["role"] == "admin_centro"
            and taquilla_service.is_center_admin(current_user["id"], betting_center_id)
        ):
            taquilla_id = taquilla_service.create_taquilla(number, betting_center_id)
            return (
                jsonify(
                    {"message": "Taquilla creada exitosamente", "id": str(taquilla_id)}
                ),
                201,
            )
        else:
            return handle_error(
                "Acceso denegado: no tienes permiso para crear taquillas en este centro",
                403,
            )

    except Exception as e:
        return handle_error(f"Error al crear la taquilla: {str(e)}", 500)


@taquilla_routes.route("/taquillas/<string:taquilla_id>", methods=["GET"])
@jwt_required()
def get_taquilla(taquilla_id):
    try:
        current_user = get_jwt_identity()
        taquilla = taquilla_service.get_taquilla_by_id(taquilla_id)
        if not taquilla:
            return handle_error("Taquilla no encontrada", 404)

        # Verificar permisos
        if current_user["role"] == "super_admin" or taquilla_service.is_center_admin(
            current_user["id"], str(taquilla["betting_center_id"])
        ):
            return jsonify(taquilla_service.taquilla_model.serialize(taquilla)), 200
        else:
            return handle_error("Acceso denegado", 403)

    except Exception as e:
        return handle_error(f"Error al obtener la taquilla: {str(e)}", 500)


@taquilla_routes.route("/taquillas/<string:taquilla_id>", methods=["PUT"])
@jwt_required()
def update_taquilla(taquilla_id):
    try:
        current_user = get_jwt_identity()
        data = request.get_json()

        taquilla = taquilla_service.get_taquilla_by_id(taquilla_id)
        if not taquilla:
            return handle_error("Taquilla no encontrada", 404)

        # Verificar permisos
        if current_user["role"] == "super_admin" or taquilla_service.is_center_admin(
            current_user["id"], str(taquilla["betting_center_id"])
        ):
            success = taquilla_service.update_taquilla(taquilla_id, data)
            if not success:
                return handle_error("No se pudo actualizar la taquilla", 400)
            return jsonify({"message": "Taquilla actualizada exitosamente"}), 200
        else:
            return handle_error("Acceso denegado", 403)

    except Exception as e:
        return handle_error(f"Error al actualizar la taquilla: {str(e)}", 500)


@taquilla_routes.route("/taquillas/<string:taquilla_id>", methods=["DELETE"])
@jwt_required()
def delete_taquilla(taquilla_id):
    try:
        current_user = get_jwt_identity()
        taquilla = taquilla_service.get_taquilla_by_id(taquilla_id)
        if not taquilla:
            return handle_error("Taquilla no encontrada", 404)

        # Verificar permisos
        if current_user["role"] == "super_admin" or taquilla_service.is_center_admin(
            current_user["id"], str(taquilla["betting_center_id"])
        ):
            success = taquilla_service.delete_taquilla(taquilla_id)
            if not success:
                return handle_error("No se pudo eliminar la taquilla", 400)
            return jsonify({"message": "Taquilla eliminada exitosamente"}), 200
        else:
            return handle_error("Acceso denegado", 403)

    except Exception as e:
        return handle_error(f"Error al eliminar la taquilla: {str(e)}", 500)


@taquilla_routes.route("/betting-centers/<string:center_id>/taquillas", methods=["GET"])
@jwt_required()
def get_taquillas_by_center(center_id):
    try:
        current_user = get_jwt_identity()
        if current_user["role"] == "super_admin" or taquilla_service.is_center_admin(
            current_user["id"], center_id
        ):
            taquillas = taquilla_service.get_all_taquillas_by_center(center_id)
            return (
                jsonify(
                    [
                        taquilla_service.taquilla_model.serialize(taquilla)
                        for taquilla in taquillas
                    ]
                ),
                200,
            )
        else:
            return handle_error("Acceso denegado", 403)

    except Exception as e:
        return handle_error(f"Error al obtener las taquillas del centro: {str(e)}", 500)


@taquilla_routes.route("/taquillas/<string:taquilla_id>/assign-user", methods=["POST"])
@jwt_required()
def assign_user_to_taquilla(taquilla_id):
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        user_id = data.get("user_id")

        print(f"Taquilla ID: {taquilla_id}, tipo: {type(taquilla_id)}")
        print(f"User ID: {user_id}, tipo: {type(user_id)}")

        # Añade estos logs adicionales
        print("Antes de llamar a taquilla_service.assign_user")
        result = taquilla_service.assign_user(taquilla_id, user_id)
        print("Después de llamar a taquilla_service.assign_user")

        if result:
            return (
                jsonify({"message": "Usuario asignado a la taquilla exitosamente"}),
                200,
            )
        else:
            return (
                jsonify({"error": "No se pudo asignar el usuario a la taquilla"}),
                400,
            )

    except ValueError as e:
        print(f"Error en la ruta: {str(e)}")  # Añade este log
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error inesperado en la ruta: {str(e)}")  # Añade este log
        return jsonify({"error": "Error interno del servidor"}), 500

    # EndPoint para desasignar


@taquilla_routes.route(
    "/taquillas/<string:taquilla_id>/unassign-user", methods=["POST"]
)
@jwt_required()
def unassign_user_from_taquilla(taquilla_id):
    try:
        current_user = get_jwt_identity()

        # Llamar al servicio de taquillas para desasignar el usuario
        result = taquilla_service.unassign_user(taquilla_id)

        if result:
            return (
                jsonify({"message": "Usuario desasignado de la taquilla exitosamente"}),
                200,
            )
        else:
            return (
                jsonify({"error": "No se pudo desasignar el usuario de la taquilla"}),
                400,
            )

    except ValueError as e:
        print(f"Error en la ruta: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error inesperado en la ruta: {str(e)}")  # Añade este log
        return jsonify({"error": "Error interno del servidor"}), 500
