import os
from flask import Flask
from .extensions import db, bcrypt, csrf


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Load configuration based on environment
    if os.environ.get('FLASK_ENV') == 'testing':
        from .config_testing import TestConfig as Config
    else:
        from .config import Config

    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from .controllers import user_controller, energy_controller, appliance_controller, room_controller

    return app
