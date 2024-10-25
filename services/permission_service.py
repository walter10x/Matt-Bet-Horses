from bson.objectid import ObjectId
from models.permission_model import PermissionModel
from models.user_model import UserModel


class PermissionService:
    def __init__(self, db):
        self.permission_model = PermissionModel(db)
        self.user_model = UserModel(db)

    def assign_permission_to_user(self, current_user, user_id, permission_id):
        """
        Asigna un permiso a un usuario.
        """
        user = self.user_model.find_user_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        # Verificar si el current_user tiene los permisos para asignar
        if current_user["role"] == "super_admin":
            # Super Admin puede asignar cualquier permiso
            return self.user_model.add_permission_to_user(user_id, permission_id)

        elif current_user["role"] == "admin_centro":
            # Admin Centro solo puede asignar permisos a usuarios en su centro
            # Verificar que el usuario esté asignado a uno de los centros que gestiona el admin_centro
            assigned_centers = self.user_model.get_assigned_centers(current_user["id"])
            if not any(
                center == user.get("assigned_centers") for center in assigned_centers
            ):
                raise ValueError(
                    "Acceso denegado: no puedes asignar permisos a este usuario, no está en tus centros asignados"
                )
            return self.user_model.add_permission_to_user(user_id, permission_id)

        else:
            raise ValueError("Acceso denegado: no tienes permisos para asignar")

    def remove_permission_from_user(self, current_user, user_id, permission_id):
        """
        Revoca un permiso de un usuario.
        """
        user = self.user_model.find_user_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        # Verificar si el current_user tiene los permisos para revocar
        if current_user["role"] == "super_admin":
            # Super Admin puede revocar cualquier permiso
            return self.user_model.remove_permission_from_user(user_id, permission_id)

        elif current_user["role"] == "admin_centro":
            # Admin Centro solo puede revocar permisos de usuarios en su centro
            assigned_centers = self.user_model.get_assigned_centers(current_user["id"])
            if not any(
                center == user.get("assigned_centers") for center in assigned_centers
            ):
                raise ValueError(
                    "Acceso denegado: no puedes revocar permisos de este usuario, no está en tus centros asignados"
                )
            return self.user_model.remove_permission_from_user(user_id, permission_id)

        else:
            raise ValueError("Acceso denegado: no tienes permisos para revocar")

    def get_user_permissions(self, user_id):
        """
        Obtiene los permisos asignados a un usuario.
        """
        user = self.user_model.find_user_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        permissions = self.permission_model.get_permissions_by_ids(
            user.get("permissions", [])
        )
        return [
            self.permission_model.serialize(permission) for permission in permissions
        ]
