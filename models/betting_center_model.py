from pymongo import MongoClient
from bson import ObjectId
import pymongo


class BettingCenterModel:
    def __init__(self, db, user_model, taquilla_model):
        self.collection = db["betting_centers"]
        self.user_model = user_model  # Para acceder a la información de los usuarios
        self.taquilla_model = (
            taquilla_model  # Para acceder a la información de las taquillas
        )

        # Crear índice único para nombre de centros
        self.collection.create_index("name", unique=True)

    def create_betting_center(self, name, address, admin_id):
        """
        Crea un nuevo centro de apuestas con un administrador.
        """
        betting_center = {
            "name": name,
            "address": address,
            "admin_id": ObjectId(admin_id),  # El administrador del centro de apuestas
            "taquillas": [],  # Lista de taquillas asociadas
            "associated_users": [],  # Usuarios asociados con el centro
        }
        try:
            result = self.collection.insert_one(betting_center)
            return result.inserted_id
        except pymongo.errors.DuplicateKeyError:
            raise ValueError("Ya existe un centro de apuestas con este nombre.")

    def find_betting_center_by_id(self, center_id):
        """
        Busca un centro de apuestas por su ID.
        """
        return self.collection.find_one({"_id": ObjectId(center_id)})

    def find_center_by_id(self, center_id):
        """
        Busca un centro de apuestas por su ID.
        """
        return self.collection.find_one({"_id": ObjectId(center_id)})

    def find_betting_center_by_name(self, name):
        """
        Busca un centro de apuestas por su nombre.
        """
        return self.collection.find_one({"name": name})

    def update_betting_center(self, center_id, updates):
        """
        Actualiza la información de un centro de apuestas.
        """
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(center_id)}, {"$set": updates}
            )
            return result.modified_count > 0
        except pymongo.errors.DuplicateKeyError:
            raise ValueError("Ya existe un centro de apuestas con este nombre.")

    def delete_betting_center(self, center_id):
        """
        Elimina un centro de apuestas.
        """
        result = self.collection.delete_one({"_id": ObjectId(center_id)})
        return result.deleted_count > 0

    def add_taquilla(self, center_id, taquilla_id):
        """
        Añade una taquilla al centro de apuestas.
        """
        result = self.collection.update_one(
            {"_id": ObjectId(center_id)},
            {"$addToSet": {"taquillas": ObjectId(taquilla_id)}},
        )
        return result.modified_count > 0

    def remove_taquilla(self, center_id, taquilla_id):
        """
        Elimina una taquilla del centro de apuestas.
        """
        result = self.collection.update_one(
            {"_id": ObjectId(center_id)},
            {"$pull": {"taquillas": ObjectId(taquilla_id)}},
        )
        return result.modified_count > 0

    def associate_user(self, center_id, user_id):
        """
        Asocia un usuario al centro de apuestas.
        """
        result = self.collection.update_one(
            {"_id": ObjectId(center_id)},
            {"$addToSet": {"associated_users": ObjectId(user_id)}},
        )
        return result.modified_count > 0

    def disassociate_user(self, center_id, user_id):
        """
        Desasocia un usuario del centro de apuestas.
        """
        result = self.collection.update_one(
            {"_id": ObjectId(center_id)},
            {"$pull": {"associated_users": ObjectId(user_id)}},
        )
        return result.modified_count > 0

    def serialize(self, betting_center):
        """
        Serializa un centro de apuestas para respuesta JSON, incluyendo taquillas con detalles.
        """
        taquillas = self.taquilla_model.find_taquillas_by_center(
            str(betting_center["_id"])
        )
        taquillas_info = [
            self.taquilla_model.serialize(taquilla) for taquilla in taquillas
        ]

        return {
            "id": str(betting_center["_id"]),
            "name": betting_center.get("name", "N/A"),
            "address": betting_center.get("address", "N/A"),
            "admin_id": str(betting_center.get("admin_id", "")),
            "taquillas": taquillas_info,
            "associated_users": [
                str(user_id) for user_id in betting_center.get("associated_users", [])
            ],
        }

    def get_centers_by_admin(self, admin_id):
        """
        Obtiene todos los centros administrados por un usuario específico.
        """
        return list(self.collection.find({"admin_id": ObjectId(admin_id)}))

    def change_admin(self, center_id, new_admin_id):
        """
        Cambia el administrador de un centro de apuestas.
        """
        result = self.collection.update_one(
            {"_id": ObjectId(center_id)}, {"$set": {"admin_id": ObjectId(new_admin_id)}}
        )
        return result.modified_count > 0

    def get_all_centers(self):
        """
        Obtiene todos los centros de apuestas.
        """
        return list(self.collection.find())

    def get_center_admin(self, center_id):
        """
        Obtiene el administrador de un centro de apuestas.
        """
        center = self.find_betting_center_by_id(center_id)
        return str(center["admin_id"]) if center else None

    def is_center_admin(self, user_id, center_id):
        """
        Verifica si un usuario es administrador de un centro específico.
        """
        center = self.find_betting_center_by_id(center_id)
        return center and (center.get("admin_id") == ObjectId(user_id))
