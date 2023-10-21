#web_server\app\config_testing.py
import os
from dotenv import load_dotenv

load_dotenv()

class TestConfig:
    TESTING = True
    MONGODB_URI = os.environ.get('TEST_DB_URL')
    MONGODB_SETTINGS = {
        'host': MONGODB_URI
    }


