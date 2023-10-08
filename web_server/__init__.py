from flask import Flask
from extensions import db

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.controllers import auth_controller, user_controller, goal_controller, energy_controller, appliance_controller, room_controller

    return app
