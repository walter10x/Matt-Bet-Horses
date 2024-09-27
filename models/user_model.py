from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

class UserModel:
    def __init__(self, db):
        self.collection = db['users']

    def create_user(self, username, email, password, dni=None, phone=None):
        hashed_password = generate_password_hash(password)
        user = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'dni': dni,
            'phone': phone
        }
        result = self.collection.insert_one(user)
        return result.inserted_id

    def find_user_by_email(self, email):
        return self.collection.find_one({'email': email})

    def find_user_by_id(self, user_id):
        return self.collection.find_one({'_id': ObjectId(user_id)})

    def verify_password(self, user, password):
        return check_password_hash(user['password'], password)

    def update_user(self, user_id, updates):
        result = self.collection.update_one({'_id': ObjectId(user_id)}, {'$set': updates})
        return result.modified_count > 0

    def delete_user(self, user_id):
        result = self.collection.delete_one({'_id': ObjectId(user_id)})
        return result.deleted_count > 0

    def serialize(self, user):
        return {
            'id': str(user['_id']),
            'username': user.get('username'),
            'email': user.get('email'),
            'dni': user.get('dni'),
            'phone': user.get('phone')
        }