# config\development.py
class DevelopmentConfig:
    DEBUG = True
    SECRET_KEY = 'your_secret_key_here'
    MONGODB_SETTINGS = {
        'db': 'your_development_database_name',
        'host': 'your_mongo_db_uri'
    }
