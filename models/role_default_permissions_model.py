from pymongo import MongoClient


class RoleDefaultPermissionsModel:
    def __init__(self, db):
        self.collection = db["role_default_permissions"]

    def get_default_permissions(self, role):
        """Obtiene los permisos predeterminados para un rol específico."""
        role_permissions = self.collection.find_one({"role": role})
        return role_permissions["permissions"] if role_permissions else []

    def set_default_permissions(self, role, permissions):
        """Establece los permisos predeterminados para un rol específico."""
        self.collection.update_one(
            {"role": role}, {"$set": {"permissions": permissions}}, upsert=True
        )

    def get_all_role_permissions(self):
        """Obtiene todos los permisos de roles."""
        return list(self.collection.find())

    def initialize_default_permissions(self):
        """Inicializa los permisos predeterminados para los roles."""
        default_permissions = {
            "super_admin": ["all"],
            "admin_centro": [
                "view_centers",
                "manage_taquillas",
                "delete_tickets",
                "view_tickets",
                "reprint_tickets",
                "view_summaries",
                "manage_configuration",
            ],
            "user": [
                "configure_printer",
                "sell_tickets",
                "delete_tickets",
                "reprint_tickets",
                "view_summaries",
            ],
        }
        for role, permissions in default_permissions.items():
            self.set_default_permissions(role, permissions)
