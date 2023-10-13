#web_server\app\config.py
from dotenv import load_dotenv
load_dotenv()
import os

# Flask settings
SECRET_KEY = os.environ.get('SECRET_KEY')

# Flask mongoengine settings
MONGODB_URI = os.environ.get('MONGODB_URI')
MONGODB_SETTINGS = {
    'host': MONGODB_URI
}