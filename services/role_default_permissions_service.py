from models.role_default_permissions_model import RoleDefaultPermissionsModel


class RoleDefaultPermissionsService:
    def __init__(self, db):
        self.role_default_permissions_model = RoleDefaultPermissionsModel(db)

    def get_default_permissions(self, role):
        """
        Obtiene los permisos predeterminados para un rol específico.
        """
        return self.role_default_permissions_model.get_default_permissions(role)

    def set_default_permissions(self, role, permissions):
        """
        Establece los permisos predeterminados para un rol específico.
        """
        return self.role_default_permissions_model.set_default_permissions(
            role, permissions
        )

    def get_all_role_permissions(self):
        """
        Obtiene todos los permisos predeterminados para todos los roles.
        """
        return self.role_default_permissions_model.get_all_role_permissions()

    def initialize_default_permissions(self):
        """
        Inicializa los permisos predeterminados para los roles en el sistema.
        """
        return self.role_default_permissions_model.initialize_default_permissions()
