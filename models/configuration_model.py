from pymongo import MongoClient
from bson import ObjectId

class ConfigurationModel:
    def __init__(self, db):
        self.collection = db['configurations']

    def create_configuration(self, center_id, config_data):
        """Crea una nueva configuración para un centro de apuestas."""
        config = {
            'center_id': ObjectId(center_id),
            'min_sale_limit': config_data.get('min_sale_limit'),
            'max_sale_limit': config_data.get('max_sale_limit'),
            'min_horse_limit': config_data.get('min_horse_limit'),
            'max_horse_limit': config_data.get('max_horse_limit'),
            'max_tickets_to_delete': config_data.get('max_tickets_to_delete'),
            'no_limit': config_data.get('no_limit', False),
            'min_horses_per_race': config_data.get('min_horses_per_race'),
            'fixed_dividend': config_data.get('fixed_dividend'),
            'max_dividend': config_data.get('max_dividend'),
            'min_dividend': config_data.get('min_dividend')
        }
        result = self.collection.insert_one(config)
        return result.inserted_id

    def get_configuration(self, center_id):
        """Obtiene la configuración de un centro de apuestas específico."""
        return self.collection.find_one({'center_id': ObjectId(center_id)})

    def update_configuration(self, center_id, updates):
        """Actualiza la configuración de un centro de apuestas específico."""
        return self.collection.update_one(
            {'center_id': ObjectId(center_id)},
            {'$set': updates}
        )

    def delete_configuration(self, center_id):
        """Elimina la configuración de un centro de apuestas específico."""
        return self.collection.delete_one({'center_id': ObjectId(center_id)})
