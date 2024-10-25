from bson.objectid import ObjectId
from models.betting_center_model import BettingCenterModel
from models.taquilla_model import (
    TaquillaModel,
)  # Asegúrate de importar el modelo de taquillas
from models.user_model import UserModel  # Asegúrate de importar el modelo de usuarios


class BettingCenterService:
    def __init__(self, db):
        self.user_model = UserModel(db)  # Para las relaciones con usuarios
        self.taquilla_model = TaquillaModel(db)  # Para las relaciones con taquillas
        self.betting_center_model = BettingCenterModel(
            db, self.user_model, self.taquilla_model
        )

    def create_betting_center(self, name, address, admin_id):
        """
        Crea un nuevo centro de apuestas.
        """
        return self.betting_center_model.create_betting_center(name, address, admin_id)

    def get_all_centers(self):
        """
        Obtiene todos los centros de apuestas.
        """
        return self.betting_center_model.get_all_centers()

    def get_centers_by_admin(self, admin_id):
        """
        Obtiene todos los centros administrados por un usuario específico.
        """
        return self.betting_center_model.get_centers_by_admin(admin_id)

    def get_betting_center_by_id(self, center_id):
        """
        Obtiene un centro de apuestas por su ID.
        """
        return self.betting_center_model.find_betting_center_by_id(center_id)

    def get_betting_center_with_details(self, center_id):
        """
        Obtiene un centro de apuestas con detalles adicionales como taquillas y usuarios asignados.
        """
        center = self.betting_center_model.find_betting_center_by_id(center_id)
        if not center:
            return None

        # Obtener taquillas asociadas
        taquillas = self.taquilla_model.find_taquillas_by_center(center_id)
        serialized_taquillas = []

        for taquilla in taquillas:
            # Obtener el usuario asignado a la taquilla
            assigned_user = None
            if taquilla.get("assigned_user_id"):
                assigned_user = self.user_model.find_user_by_id(
                    str(taquilla["assigned_user_id"])
                )

            # Serializar la taquilla con el nombre y el ID del usuario si existe
            serialized_taquillas.append(
                {
                    "id": str(taquilla["_id"]),
                    "number": taquilla.get(
                        "number", "N/A"
                    ),  # Mostrar el número de la taquilla
                    "assigned_user": {
                        "id": str(assigned_user["_id"]) if assigned_user else None,
                        "name": (
                            assigned_user.get("username", "Sin Asignar")
                            if assigned_user
                            else "Sin Asignar"
                        ),
                    },
                }
            )

        # Serializar el centro de apuestas con los detalles de las taquillas
        serialized_center = {
            "id": str(center["_id"]),
            "name": center.get("name", "N/A"),
            "address": center.get("address", "N/A"),
            "admin_id": str(center.get("admin_id", "")),
            "taquillas": serialized_taquillas,
        }

        return serialized_center

    def update_betting_center(self, center_id, updates):
        """
        Actualiza los datos de un centro de apuestas.
        """
        return self.betting_center_model.update_betting_center(center_id, updates)

    def delete_betting_center(self, center_id):
        """
        Elimina un centro de apuestas.
        """
        return self.betting_center_model.delete_betting_center(center_id)

    def change_admin(self, center_id, new_admin_id):
        """
        Cambia el administrador de un centro de apuestas.
        """
        return self.betting_center_model.change_admin(center_id, new_admin_id)

    def serialize_betting_center(self, center):
        """
        Serializa un centro de apuestas para la salida JSON.
        """
        return self.betting_center_model.serialize(center)

    def add_taquilla(self, center_id, taquilla_id):
        """
        Añade una taquilla al centro de apuestas.
        """
        return self.betting_center_model.add_taquilla(center_id, taquilla_id)

    def remove_taquilla(self, center_id, taquilla_id):
        """
        Elimina una taquilla del centro de apuestas.
        """
        return self.betting_center_model.remove_taquilla(center_id, taquilla_id)

    def is_user_assigned_to_another_center(self, user_id):
        """
        Verifica si el usuario ya está asignado a otro centro de apuestas.
        """
        user = self.user_model.find_user_by_id(user_id)
        if not user:
            return False

        return user.get("admin_id") is not None

    def assign_user_to_admin(
        self, center_id, user_id, current_user_id, current_user_role
    ):
        # Obtener el centro de apuestas y el usuario
        center = self.betting_center_model.find_betting_center_by_id(center_id)
        user = self.user_model.find_user_by_id(user_id)

        if not center:
            raise Exception("Centro de apuestas no encontrado.")
        if not user:
            raise Exception("Usuario no encontrado.")

        # Verificar que el usuario no esté asignado a otro centro de apuestas
        if user.get("assigned_centers") and center_id not in user["assigned_centers"]:
            raise Exception("El usuario ya está asignado a otro centro de apuestas.")

        # Verificar permisos del usuario actual
        if current_user_role == "super_admin":
            # El superadmin tiene permiso automáticamente
            pass
        elif current_user_role == "admin_centro":
            # Verificar si el usuario actual es el administrador del centro
            if str(center.get("admin_id")) != current_user_id:
                raise Exception(
                    "No tienes permiso para asignar usuarios a este centro de apuestas."
                )
        else:
            raise Exception(
                "No tienes los permisos necesarios para realizar esta acción."
            )

        # Asignar el usuario al centro de apuestas
        success = self.user_model.assign_center(user_id, center_id)
        if not success:
            raise Exception("No se pudo asignar el usuario al centro de apuestas.")

        return True

    def manage_user_permissions(self, admin_id, user_id, permissions):
        """
        Permite a un administrador gestionar permisos de un usuario.
        """
        user = self.user_model.find_user_by_id(user_id)
        if not user:
            return None

        # Lógica para asignar o revocar permisos
        for permission in permissions:
            if permission["action"] == "assign":
                self.user_model.assign_permission(user_id, permission["permission_id"])
            elif permission["action"] == "revoke":
                self.user_model.revoke_permission(user_id, permission["permission_id"])

        return True

    def get_center_admin(self, center_id):
        """
        Obtiene el ID del administrador asignado a un centro de apuestas.
        """
        center = self.betting_center_model.find_betting_center_by_id(center_id)
        if not center:
            return None

        return str(center.get("admin_id", ""))  # Retorna el ID del administrador
