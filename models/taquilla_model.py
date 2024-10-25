from pymongo import MongoClient
from bson import ObjectId
import pymongo
import logging

class TaquillaModel:
    def __init__(self, db):
        self.collection = db['taquillas']
        # Crear índice único para el número de taquilla y el centro de apuestas
        self.collection.create_index([('number', 1), ('betting_center_id', 1)], unique=True)

    def create_taquilla(self, number, betting_center_id):
        """
        Crea una nueva taquilla asociada a un centro de apuestas.
        """
        if not ObjectId.is_valid(betting_center_id):
            raise ValueError(f"ID del centro de apuestas inválido: {betting_center_id}")

        taquilla = {
            'number': number,
            'betting_center_id': ObjectId(betting_center_id),
            'assigned_user_id': None,  # ID del usuario asignado a esta taquilla
            'status': 'active'  # Estado inicial de la taquilla
        }
        try:
            result = self.collection.insert_one(taquilla)
            return result.inserted_id
        except pymongo.errors.DuplicateKeyError:
            raise ValueError("Ya existe una taquilla con este número en el centro de apuestas especificado.")

    def find_taquilla_by_id(self, taquilla_id):
        """
        Busca una taquilla por su ID.
        """
        if not ObjectId.is_valid(taquilla_id):
            raise ValueError(f"ID de taquilla inválido: {taquilla_id}")
        return self.collection.find_one({'_id': ObjectId(taquilla_id)})

    def find_taquillas_by_center(self, betting_center_id):
        """
        Busca todas las taquillas asociadas a un centro de apuestas.
        """
        if not ObjectId.is_valid(betting_center_id):
            raise ValueError(f"ID del centro de apuestas inválido: {betting_center_id}")
        return list(self.collection.find({'betting_center_id': ObjectId(betting_center_id)}))

    def update_taquilla(self, taquilla_id, updates):
        """
        Actualiza la información de una taquilla.
        """
        try:
            result = self.collection.update_one({'_id': ObjectId(taquilla_id)}, {'$set': updates})
            return result.modified_count > 0
        except pymongo.errors.DuplicateKeyError:
            raise ValueError("Ya existe una taquilla con este número en el centro de apuestas especificado.")

    def delete_taquilla(self, taquilla_id):
        """
        Elimina una taquilla.
        """
        if not ObjectId.is_valid(taquilla_id):
            raise ValueError(f"ID de taquilla inválido: {taquilla_id}")
        result = self.collection.delete_one({'_id': ObjectId(taquilla_id)})
        return result.deleted_count > 0

    def assign_user(self, taquilla_id, user_id):
        """
        Asigna un usuario a una taquilla.
        """
        try:
            if not ObjectId.is_valid(taquilla_id):
                raise ValueError(f"ID de taquilla inválido: {taquilla_id}")
            if not ObjectId.is_valid(user_id):
                raise ValueError(f"ID de usuario inválido: {user_id}")

            taquilla_object_id = ObjectId(taquilla_id)
            user_object_id = ObjectId(user_id)

            taquilla = self.find_taquilla_by_id(taquilla_object_id)
            if not taquilla:
                raise ValueError(f"Taquilla no encontrada con ID: {taquilla_id}")
            
            result = self.collection.update_one(
                {'_id': taquilla_object_id},
                {'$set': {'assigned_user_id': user_object_id}}
            )
            
            if result.modified_count == 0:
                raise ValueError(f"No se pudo actualizar la taquilla con ID: {taquilla_id}")
            
            return True
        except Exception as e:
            logging.error(f"Error al asignar usuario a taquilla: {str(e)}")
            raise ValueError(f"Error al asignar usuario a taquilla: {str(e)}")

    def unassign_user(self, taquilla_id):
        """
        Desasigna un usuario de una taquilla.
        """
        if not ObjectId.is_valid(taquilla_id):
            raise ValueError(f"ID de taquilla inválido: {taquilla_id}")

        result = self.collection.update_one(
            {'_id': ObjectId(taquilla_id)},
            {'$set': {'assigned_user_id': None}}
        )
        return result.modified_count > 0

    def serialize(self, taquilla):
        """
        Serializa una taquilla para respuesta JSON.
        """
        return {
            'id': str(taquilla['_id']),
            'number': taquilla['number'],
            'betting_center_id': str(taquilla['betting_center_id']),
            'assigned_user_id': str(taquilla['assigned_user_id']) if taquilla.get('assigned_user_id') else None,
            'status': taquilla.get('status', 'active')
        }

    def find_taquillas_by_user(self, user_id):
        """
        Busca todas las taquillas asignadas a un usuario específico.
        """
        if not ObjectId.is_valid(user_id):
            raise ValueError(f"ID de usuario inválido: {user_id}")
        return list(self.collection.find({'assigned_user_id': ObjectId(user_id)}))

    def change_taquilla_status(self, taquilla_id, new_status):
        """
        Cambia el estado de una taquilla.
        """
        if new_status not in ['active', 'inactive', 'maintenance']:
            raise ValueError("Estado no válido. Debe ser 'active', 'inactive' o 'maintenance'.")
        
        if not ObjectId.is_valid(taquilla_id):
            raise ValueError(f"ID de taquilla inválido: {taquilla_id}")

        result = self.collection.update_one(
            {'_id': ObjectId(taquilla_id)},
            {'$set': {'status': new_status}}
        )
        return result.modified_count > 0

    def get_active_taquillas_by_center(self, betting_center_id):
        """
        Obtiene todas las taquillas activas asociadas a un centro de apuestas.
        """
        if not ObjectId.is_valid(betting_center_id):
            raise ValueError(f"ID del centro de apuestas inválido: {betting_center_id}")

        return list(self.collection.find({
            'betting_center_id': ObjectId(betting_center_id),
            'status': 'active'
        }))