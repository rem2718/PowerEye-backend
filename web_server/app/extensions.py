# app/extensions.py
"""
Flask extensions are third-party libraries that add extra functionality to Flask.

This module initializes and provides instances of Flask extensions.

- `db`: MongoEngine for MongoDB integration.
- `bcrypt`: Bcrypt for password hashing.
- `jwt`: JWTManager for JSON Web Token support.

"""

from flask_mongoengine import MongoEngine
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# Initialize Flask extensions
db = MongoEngine()
bcrypt = Bcrypt()
jwt = JWTManager()
