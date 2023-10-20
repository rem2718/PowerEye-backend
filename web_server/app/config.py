#web_server\app\config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = True
    MONGODB_SETTINGS = {
        'db': os.getenv('DEV_DB_NAME'),
        'host': os.getenv('DEV_DB_URL')
    }
