from pymongo import MongoClient
from bson import ObjectId
from pymongo.errors import DuplicateKeyError


class PermissionModel:
    def __init__(self, db):
        self.collection = db["permissions"]
        # Crear índice único para el nombre del permiso
        self.collection.create_index("name", unique=True)

    def create_permission(self, name, description):
        """
        Crea un nuevo permiso en la base de datos.
        """
        permission = {"name": name, "description": description}
        try:
            result = self.collection.insert_one(permission)
            return result.inserted_id
        except DuplicateKeyError:
            raise ValueError("Ya existe un permiso con este nombre.")

    def get_permission(self, permission_id):
        """
        Obtiene un permiso por su ID.
        """
        return self.collection.find_one({"_id": ObjectId(permission_id)})

    def get_permission_by_name(self, name):
        """
        Obtiene un permiso por su nombre.
        """
        return self.collection.find_one({"name": name})

    def get_all_permissions(self):
        """
        Obtiene todos los permisos de la base de datos.
        """
        return list(self.collection.find())

    def update_permission(self, permission_id, updates):
        """
        Actualiza un permiso existente.
        """
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(permission_id)}, {"$set": updates}
            )
            return result.modified_count > 0
        except DuplicateKeyError:
            raise ValueError("Ya existe un permiso con este nombre.")

    def delete_permission(self, permission_id):
        """
        Elimina un permiso de la base de datos.
        """
        result = self.collection.delete_one({"_id": ObjectId(permission_id)})
        return result.deleted_count > 0

    def serialize(self, permission):
        """
        Serializa un permiso para respuesta JSON.
        """
        return {
            "id": str(permission["_id"]),
            "name": permission["name"],
            "description": permission["description"],
        }

    def get_permissions_by_ids(self, permission_ids):
        """
        Obtiene una lista de permisos por sus IDs.
        """
        return list(
            self.collection.find(
                {"_id": {"$in": [ObjectId(id) for id in permission_ids]}}
            )
        )

    def initialize_permissions(self):
        """
        Inicializa permisos predeterminados.
        """
        permissions = [
            ("view_centers", "Ver centros de apuestas"),
            ("manage_taquillas", "Gestionar taquillas"),
            ("delete_tickets", "Eliminar tickets"),
            ("view_tickets", "Ver tickets"),
            ("reprint_tickets", "Reimprimir tickets"),
            ("view_summaries", "Ver resúmenes"),
            ("manage_configuration", "Gestionar configuración"),
            ("configure_printer", "Configurar impresora"),
            ("sell_tickets", "Vender tickets"),
        ]
        for name, description in permissions:
            try:
                self.create_permission(name, description)
            except ValueError:
                # Si el permiso ya existe, lo ignoramos
                pass
