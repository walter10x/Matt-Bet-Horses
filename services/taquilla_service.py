from models.taquilla_model import TaquillaModel
from models.betting_center_model import BettingCenterModel
from models.user_model import UserModel  # Asegúrate de importar el modelo de usuarios
from models.permission_model import PermissionModel  # Importar el modelo de permisos
import logging
from bson import ObjectId


class TaquillaService:
    def __init__(self, db):
        # Instanciar los modelos
        self.user_model = UserModel(db)  # Modelo de usuarios
        self.taquilla_model = TaquillaModel(db)  # Modelo de taquillas
        self.betting_center_model = BettingCenterModel(
            db, self.user_model, self.taquilla_model
        )  # Modelo de centros de apuestas
        self.permission_model = PermissionModel(db)  # Modelo de permisos

    def create_taquilla(self, number, betting_center_id):
        """
        Crea una nueva taquilla y la añade al centro de apuestas correspondiente.
        """
        try:
            # Validar que el ID del centro de apuestas sea válido
            if not ObjectId.is_valid(betting_center_id):
                raise ValueError(
                    f"ID del centro de apuestas inválido: {betting_center_id}"
                )

            # Crear la taquilla
            taquilla_id = self.taquilla_model.create_taquilla(number, betting_center_id)

            # Añadir la taquilla al centro de apuestas
            added = self.betting_center_model.add_taquilla(
                betting_center_id, taquilla_id
            )
            if not added:
                raise ValueError("No se pudo añadir la taquilla al centro de apuestas.")

            return taquilla_id
        except ValueError as e:
            logging.error(f"Error al crear taquilla: {str(e)}")
            raise ValueError(str(e))

    def get_taquilla_by_id(self, taquilla_id):
        """
        Obtiene una taquilla por su ID, incluyendo el usuario asignado.
        """
        if not ObjectId.is_valid(taquilla_id):
            raise ValueError(f"ID de taquilla inválido: {taquilla_id}")

        taquilla = self.taquilla_model.find_taquilla_by_id(taquilla_id)
        if taquilla:
            assigned_user = self.user_model.find_user_by_id(
                str(taquilla.get("assigned_user_id"))
            )  # Obtener usuario asignado
            return {
                "id": str(taquilla["_id"]),
                "number": taquilla["number"],
                "assigned_user": {
                    "id": str(assigned_user["_id"]) if assigned_user else None,
                    "username": (
                        assigned_user["username"] if assigned_user else "Sin Asignar"
                    ),
                },
            }
        return None

    def update_taquilla(self, taquilla_id, updates):
        """
        Actualiza la información de una taquilla.
        """
        return self.taquilla_model.update_taquilla(taquilla_id, updates)

    def delete_taquilla(self, taquilla_id):
        """
        Elimina una taquilla y la elimina del centro de apuestas correspondiente.
        """
        if not ObjectId.is_valid(taquilla_id):
            raise ValueError(f"ID de taquilla inválido: {taquilla_id}")

        taquilla = self.get_taquilla_by_id(taquilla_id)
        if taquilla:
            self.betting_center_model.remove_taquilla(
                taquilla["betting_center_id"], taquilla_id
            )
        return self.taquilla_model.delete_taquilla(taquilla_id)

    def get_all_taquillas_by_center(self, center_id):
        """
        Obtiene todas las taquillas asociadas a un centro de apuestas, incluyendo los usuarios asignados.
        """
        if not ObjectId.is_valid(center_id):
            raise ValueError(f"ID del centro de apuestas inválido: {center_id}")

        taquillas = self.taquilla_model.find_taquillas_by_center(center_id)
        serialized_taquillas = []
        for taquilla in taquillas:
            assigned_user = self.user_model.find_user_by_id(
                str(taquilla.get("assigned_user_id"))
            )
            serialized_taquillas.append(
                {
                    "id": str(taquilla["_id"]),
                    "number": taquilla["number"],
                    "assigned_user": {
                        "id": str(assigned_user["_id"]) if assigned_user else None,
                        "username": (
                            assigned_user["username"]
                            if assigned_user
                            else "Sin Asignar"
                        ),
                    },
                }
            )
        return serialized_taquillas

    def assign_user(self, taquilla_id, user_id):
        print(f"Servicio - Taquilla ID: {taquilla_id}, tipo: {type(taquilla_id)}")
        print(f"Servicio - User ID: {user_id}, tipo: {type(user_id)}")
        try:
            # Imprimir los valores recibidos
            taquilla_object_id = ObjectId(taquilla_id)
            user_object_id = ObjectId(user_id)

            print(f"Taquilla ObjectId: {taquilla_object_id}")
            print(f"User ObjectId: {user_object_id}")

            # Validar que los IDs sean válidos ObjectId
            if not taquilla_id or not user_id:
                raise ValueError(
                    "Se requieren tanto el ID de la taquilla como el ID del usuario"
                )

            if not ObjectId.is_valid(taquilla_id):
                raise ValueError(f"ID de taquilla inválido: {taquilla_id}")
            if not ObjectId.is_valid(user_id):
                raise ValueError(f"ID de usuario inválido: {user_id}")

            # Convertir a ObjectId
            taquilla_object_id = ObjectId(taquilla_id)
            user_object_id = ObjectId(user_id)

            # Imprimir los ObjectId convertidos
            print(f"taquilla_object_id: {taquilla_object_id}")
            print(f"user_object_id: {user_object_id}")

            # Verificar si la taquilla existe
            taquilla = self.taquilla_model.find_taquilla_by_id(taquilla_object_id)
            if not taquilla:
                raise ValueError("Taquilla no encontrada")

            # Verificar si el usuario existe
            user = self.user_model.find_user_by_id(user_object_id)
            if not user:
                raise ValueError("Usuario no encontrado")

            # Imprimir en consola los IDs
            print(
                f"ID del usuario: {user_object_id}, ID de la taquilla: {taquilla_object_id}"
            )

            # Registro de información
            logging.info(
                f"Asignando usuario ID: {user_object_id} (Username: {user['username']}) a taquilla ID: {taquilla_object_id} (Número: {taquilla['number']})"
            )

            # Asignar el usuario a la taquilla
            result = self.taquilla_model.assign_user(taquilla_object_id, user_object_id)
            if not result:
                raise ValueError("No se pudo asignar el usuario a la taquilla")

            return True

        except Exception as e:
            logging.error(f"Error al asignar el usuario a la taquilla: {e}")
            raise ValueError(f"Error al asignar el usuario a la taquilla: {str(e)}")

    def unassign_user(self, taquilla_id):
        """
        Desasigna un usuario de una taquilla.
        """
        return self.taquilla_model.unassign_user(taquilla_id)

    def is_center_admin(self, user_id, betting_center_id):
        """
        Verifica si el usuario tiene permisos para administrar el centro de apuestas.
        """
        return self.betting_center_model.is_center_admin(user_id, betting_center_id)
