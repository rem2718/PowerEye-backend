# web_server\app\config_testing.py
"""
Configuration for testing environment.

This module defines the configuration settings for the testing environment.

- `DEBUG`: Debug mode is turned off.
- `TESTING`: Testing mode is enabled.
- `MONGODB_URI`: MongoDB URI for the testing database.
- `MONGODB_SETTINGS`: MongoDB settings with the testing database URI.
"""
import os
from dotenv import load_dotenv

load_dotenv('.env.testing')

class TestConfig:
    """ 
    Configuration class for testing environment.
    """
    DEBUG = False
    TESTING = False
    MONGODB_URI = os.environ.get('TEST_DB_URL')
    MONGODB_SETTINGS = {
        'host': MONGODB_URI
    }
