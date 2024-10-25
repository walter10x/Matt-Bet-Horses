from models.user_model import UserModel
import logging

class UserService:
    def __init__(self, db):
        self.user_model = UserModel(db)

    def get_all_users(self, current_user):
        if current_user['role'] == 'super_admin':
            return list(self.user_model.collection.find())
        elif current_user['role'] == 'admin_centro':
            admin_centers = self.user_model.get_centers_by_admin(current_user['id'])
            center_ids = [center['_id'] for center in admin_centers]
            return list(self.user_model.collection.find({'assigned_centers': {'$in': center_ids}}))
        else:
            raise ValueError("Acceso denegado")

    def get_user_by_id(self, user_id):
        """
        Obtiene un usuario por su ID.
        """
        return self.user_model.find_user_by_id(user_id)

    def update_user(self, user_id, updates):
        """
        Actualiza los datos de un usuario.
        """
        return self.user_model.update_user(user_id, updates)

    def delete_user(self, user_id):
        """
        Elimina un usuario de la base de datos.
        """
        return self.user_model.delete_user(user_id)

    def create_user(self, username, email, password, role='user'):
        """
        Registra un nuevo usuario en el sistema.
        Se asegura de que la contraseña esté hasheada antes de guardarla.
        """
        try:
            # Crear el usuario con los datos proporcionados
            user_id = self.user_model.create_user(username, email, password, role=role)
            return user_id
        except ValueError as e:
            logging.error(f"Error al registrar el usuario: {str(e)}")
            raise ValueError(str(e))

    def add_permission_to_user(self, user_id, permission_id):
        """
        Añade un permiso a un usuario.
        """
        return self.user_model.add_permission_to_user(user_id, permission_id)

    def remove_permission_from_user(self, user_id, permission_id):
        """
        Elimina un permiso de un usuario.
        """
        return self.user_model.remove_permission_from_user(user_id, permission_id)

    def assign_center(self, user_id, center_id):
        """
        Asigna un centro de apuestas a un usuario.
        """
        return self.user_model.assign_center(user_id, center_id)

    def unassign_center(self, user_id, center_id):
        """
        Desasigna un centro de apuestas de un usuario.
        """
        return self.user_model.unassign_center(user_id, center_id)

    def assign_taquilla(self, user_id, taquilla_id):
        """
        Asigna una taquilla a un usuario.
        """
        return self.user_model.assign_taquilla(user_id, taquilla_id)

    def unassign_taquilla(self, user_id):
        """
        Desasigna la taquilla de un usuario.
        """
        return self.user_model.unassign_taquilla(user_id)

    def get_assigned_centers(self, user_id):
        """
        Obtiene los centros asignados a un usuario.
        """
        return self.user_model.get_assigned_centers(user_id)

    def get_assigned_taquilla(self, user_id):
        """
        Obtiene la taquilla asignada a un usuario.
        """
        return self.user_model.get_assigned_taquilla(user_id)

    def is_center_admin(self, user_id, center_id):
        """
        Verifica si un usuario es administrador de un centro específico.
        """
        return self.user_model.is_center_admin(user_id, center_id)

    def change_user_role(self, user_id, new_role):
        """
        Cambia el rol de un usuario y actualiza sus permisos predeterminados.
        """
        return self.user_model.change_user_role(user_id, new_role)

    def assign_default_permissions(self, user_id, role):
        """
        Asigna permisos predeterminados a un usuario basado en su rol.
        """
        return self.user_model.assign_default_permissions(user_id, role)

    def serialize(self, user):
        """
        Serializa un usuario para respuesta JSON.
        """
        return self.user_model.serialize(user)
