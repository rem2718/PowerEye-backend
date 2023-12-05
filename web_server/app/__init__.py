# web_server\app\__init__.py
"""
Initialize and configure the Flask application.

This module creates a Flask application, 
loads configuration based on the environment, and initializes various extensions. 
It also registers blueprints for different views.

"""
import os
from flask import Flask
from dotenv import load_dotenv
from .extensions import db, bcrypt, jwt
from .views.appliance_views import appliance_views
from .views.room_views import room_views
from .views.user_views import user_views
from .views.power_views import power_views
from .views.energy_views import energy_views
from .config import Config


# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Load configuration based on environment
    # if os.environ.get('FLASK_ENV') == 'testing':
    #     from .config_testing import TestConfig as Config
    # else:
    #     from .config import Config
    app.secret_key = os.getenv('SECRET_KEY')
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    app.register_blueprint(appliance_views)
    app.register_blueprint(room_views)
    app.register_blueprint(power_views)
    app.register_blueprint(user_views)
    app.register_blueprint(energy_views)

    return app

# if __name__ == '__main__':
#     app = create_app()
#     app.run(host='0.0.0.0')
