from models.user_model import UserModel
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
import logging

class AuthService:
    def __init__(self, db):
        self.user_model = UserModel(db)

    def register_user(self, username, email, password, role='user'):
        """
        Registra un nuevo usuario en el sistema.
        Se asegura de que la contraseña esté hasheada antes de guardarla.
        """
        try:
            # Hashear la contraseña antes de almacenarla
            hashed_password = generate_password_hash(password)

            # Crear el usuario con la contraseña hasheada
            user_id = self.user_model.create_user(username, email, hashed_password, role=role)
            return user_id
        except ValueError as e:
            logging.error(f"Error al registrar el usuario: {str(e)}")
            raise ValueError(str(e))

    def login_user(self, identifier, password):
        """
        Maneja el inicio de sesión de un usuario, validando las credenciales.
        Devuelve un token de acceso si las credenciales son correctas.
        """
        user = self.user_model.find_user_by_identifier(identifier)

        # Si el usuario no existe o la contraseña no es correcta, lanzamos un error genérico
        if not user or not check_password_hash(user['password'], password):
            logging.error("Credenciales inválidas")
            raise ValueError("Email o contraseña incorrectos.")

        # Generar el token de acceso JWT
        access_token = create_access_token(identity={
            'id': str(user['_id']),
            'role': user['role'],
            'permissions': user.get('permissions', [])
        })
        return access_token, user
