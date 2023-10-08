class TestingConfig:
    TESTING = True
    SECRET_KEY = 'your_secret_key_here'
    MONGODB_SETTINGS = {
        'db': 'your_testing_database_name',
        'host': 'your_mongo_db_uri'
    }
