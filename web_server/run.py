#run.py:
from app import create_app
from app.views.dummy_views import app as dummy

from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

if __name__ == '__main__':
    app = create_app()
    app.register_blueprint(dummy)
    app.run()


