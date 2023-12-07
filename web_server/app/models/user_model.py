# user_model.py
"""
Module defining the User model.

This module defines the User model as a Flask-MongoEngine document.
"""
from datetime import datetime, timedelta
import jwt
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from mongoengine import EmbeddedDocumentField
from app.extensions import db
from app.config import Config
from app.utils.enums import PlugType
from .appliance_model import Appliance
from .notified_device_model import NotifiedDevice

bcrypt = Bcrypt()

load_dotenv()

class User(db.Document):
    email = db.EmailField(required=True)
    password = db.StringField(required=True)
    username = db.StringField(default="")
    is_deleted = db.BooleanField(default=False)
    appliances = db.ListField(EmbeddedDocumentField(Appliance),required=False,default=[])
    cloud_type= db.EnumField(PlugType, default=PlugType.MEROSS)
    cloud_password = db.StringField(required=True)
    current_month_energy = db.FloatField(default=0.0)
    energy_goal = db.FloatField(default=-1.0)
    notified_devices = db.ListField(EmbeddedDocumentField(NotifiedDevice),required=False,default=[])
    # profile_pic is saved in the server

    meta = {
        'collection': 'Users'  # the real collection name here
    }

    # Add any additional methods or properties as needed
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def generate_token(self):
        payload = {
            'sub': str(self.id),
            'exp': datetime.utcnow() + timedelta(days=30)  # Token expiration time
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
