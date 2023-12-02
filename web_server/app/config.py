"""
Application configuration settings.

This module defines the configuration settings for the Flask application. 
It includes settings for debugging, the secret key, and the MongoDB connection URI.

Attributes:
    - DEBUG (bool): Enable or disable debug mode.
    - SECRET_KEY (str): Secret key for securing the application.
    - MONGODB_URI (str): MongoDB connection URI.
    - MONGODB_SETTINGS (dict): MongoDB settings with the host URI.

"""
#web_server\app\config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """ 
    Configuration class for the Flask application.
    """
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MONGODB_URI = os.environ.get('DEV_DB_URL')
    MONGODB_SETTINGS = {
        'host': MONGODB_URI
    }
