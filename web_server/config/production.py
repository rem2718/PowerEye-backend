class ProductionConfig:
    DEBUG = False
    SECRET_KEY = 'your_secret_key_here'
    MONGODB_SETTINGS = {
        'db': 'your_production_database_name',
        'host': 'your_mongo_db_uri'
    }
