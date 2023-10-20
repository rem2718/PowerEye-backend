#web_server\app\config_testing.py
import os
from dotenv import load_dotenv

load_dotenv()

class TestConfig:
    TESTING = True
    MONGODB_SETTINGS = {
        'db': os.getenv('TEST_DB_NAME'),
        'host': os.getenv('TEST_DB_URL')
    }


