# app/config/__init__.py:
import os
from flask import Flask

app = Flask(__name__)

# Load the appropriate configuration based on the environment variable
config_name = os.getenv('FLASK_CONFIG', 'development')

if config_name == 'development':
    from config.development import DevelopmentConfig
    app.config.from_object(DevelopmentConfig)
elif config_name == 'production':
    from config.production import ProductionConfig
    app.config.from_object(ProductionConfig)
elif config_name == 'testing':
    from config.testing import TestingConfig
    app.config.from_object(TestingConfig)
else:
    raise ValueError("Invalid FLASK_CONFIG environment variable")

# Initialize the MongoEngine
from flask_mongoengine import MongoEngine
db = MongoEngine(app)
