#web_server\app\config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MONGODB_URI = os.environ.get('DEV_DB_URL')
    MONGODB_SETTINGS = {
        'host': MONGODB_URI
    }
    
