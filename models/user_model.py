from pymongo import MongoClient
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from models.role_default_permissions_model import RoleDefaultPermissionsModel


class UserModel:
    def __init__(self, db):
        self.collection = db["users"]
        self.db = db  # Para relaciones con otros modelos
        self.role_permissions_model = RoleDefaultPermissionsModel(db)
        # Crear índices únicos para email y username
        self.collection.create_index("email", unique=True)
        self.collection.create_index("username", unique=True)

    def create_user(
        self, username, email, password, role="user", assigned_centers=None
    ):
        """
        Crea un nuevo usuario con permisos y centros asignados según el rol.
        Los permisos predeterminados se asignan según el rol.
        """
        if role not in ["super_admin", "admin_centro", "user"]:
            raise ValueError(
                "Rol no válido. Debe ser 'super_admin', 'admin_centro' o 'user'."
            )

        # Obtener los permisos predeterminados para el rol
        default_permissions = self.role_permissions_model.get_default_permissions(role)

        user = {
            "username": username,
            "email": email,
            "password": password,  # Guardar la contraseña directamente para la prueba
            "role": role,
            "permissions": default_permissions,  # Asignar permisos predeterminados según el rol
            "assigned_centers": assigned_centers
            or [],  # Centros de apuestas que administra
            "assigned_taquilla": None,  # Taquilla asignada (si es un usuario)
        }
        try:
            result = self.collection.insert_one(user)
            return result.inserted_id
        except DuplicateKeyError:
            raise ValueError("El email o el nombre de usuario ya están en uso.")

    def find_user_by_email(self, email):
        return self.collection.find_one({"email": email})

    def find_user_by_username(self, username):
        return self.collection.find_one({"username": username})

    def find_user_by_id(self, user_id):
        return self.collection.find_one({"_id": ObjectId(user_id)})

    def find_user_by_identifier(self, identifier):
        """
        Busca un usuario por email o username.
        """
        return self.collection.find_one(
            {"$or": [{"email": identifier}, {"username": identifier}]}
        )

    def verify_password(self, user, password):
        """
        Verifica la contraseña ingresada con la almacenada.
        """
        return user["password"] == password

    def update_user(self, user_id, updates):
        """
        Actualiza los datos de un usuario.
        """
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)}, {"$set": updates}
            )
            return result.modified_count > 0
        except DuplicateKeyError:
            raise ValueError("El email o el nombre de usuario ya están en uso.")

    def delete_user(self, user_id):
        """
        Elimina un usuario de la base de datos.
        """
        result = self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    def add_permission_to_user(self, user_id, permission_id):
        """
        Añade un permiso a un usuario.
        """
        return self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"permissions": ObjectId(permission_id)}},
        )

    def remove_permission_from_user(self, user_id, permission_id):
        """
        Elimina un permiso de un usuario.
        """
        return self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"permissions": ObjectId(permission_id)}},
        )

    def assign_center(self, user_id, center_id):
        """
        Asigna un centro de apuestas a un usuario.
        """
        return self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"assigned_centers": ObjectId(center_id)}},
        )

    def unassign_center(self, user_id, center_id):
        """
        Desasigna un centro de apuestas de un usuario.
        """
        return self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"assigned_centers": ObjectId(center_id)}},
        )

    def assign_taquilla(self, user_id, taquilla_id):
        """
        Asigna una taquilla a un usuario.
        """
        return self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"assigned_taquilla": ObjectId(taquilla_id)}},
        )

    def unassign_taquilla(self, user_id):
        """
        Desasigna la taquilla de un usuario.
        """
        return self.collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"assigned_taquilla": None}}
        )

    def get_assigned_centers(self, user_id):
        """
        Obtiene los centros asignados a un usuario.
        """
        user = self.find_user_by_id(user_id)
        return user.get("assigned_centers", []) if user else []

    def get_assigned_taquilla(self, user_id):
        """
        Obtiene la taquilla asignada a un usuario.
        """
        user = self.find_user_by_id(user_id)
        return user.get("assigned_taquilla") if user else None

    def is_center_admin(self, user_id, center_id):
        """
        Verifica si un usuario es administrador de un centro específico.
        """
        user = self.find_user_by_id(user_id)
        return user and (
            user.get("role") == "super_admin"
            or (
                user.get("role") == "admin_centro"
                and ObjectId(center_id) in user.get("assigned_centers", [])
            )
        )

    def change_user_role(self, user_id, new_role):
        """
        Cambia el rol de un usuario y actualiza sus permisos predeterminados.
        """
        if new_role not in ["super_admin", "admin_centro", "user"]:
            raise ValueError(
                "Rol no válido. Debe ser 'super_admin', 'admin_centro' o 'user'."
            )

        result = self.collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"role": new_role}}
        )
        if result.modified_count > 0:
            # Asignar nuevos permisos predeterminados basados en el nuevo rol
            self.assign_default_permissions(user_id, new_role)
        return result.modified_count > 0

    def assign_default_permissions(self, user_id, role):
        """
        Asigna permisos predeterminados a un usuario basado en su rol.
        """
        default_permissions = self.role_permissions_model.get_default_permissions(role)
        self.collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"permissions": default_permissions}}
        )

    def serialize(self, user):
        """
        Serializa un usuario para respuesta JSON.
        """
        return {
            "id": str(user["_id"]),
            "username": user.get("username"),
            "email": user.get("email"),
            "role": user.get("role", "user"),
            "permissions": user.get("permissions", []),
            "assigned_centers": [
                str(center_id) for center_id in user.get("assigned_centers", [])
            ],
            "assigned_taquilla": (
                str(user.get("assigned_taquilla"))
                if user.get("assigned_taquilla")
                else None
            ),
        }


def has_permission(self, user_id, permission_id):
    """
    Verifica si un usuario tiene un permiso específico.
    """
    user = self.find_user_by_id(user_id)
    return user and ObjectId(permission_id) in user.get("permissions", [])
