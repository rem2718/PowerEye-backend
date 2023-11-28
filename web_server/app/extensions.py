# app/extensions.py
# Flask extensions are third-party libraries that add extra functionality to Flask.

from flask_mongoengine import MongoEngine
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_jwt_extended import JWTManager




# Initialize Flask extensions
db = MongoEngine()
bcrypt = Bcrypt()
# csrf = CSRFProtect()
jwt = JWTManager()