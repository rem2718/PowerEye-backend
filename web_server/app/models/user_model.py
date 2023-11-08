import os
from app.extensions import db
from .appliance_model import Appliance  # Import the Appliance model
import jwt
from datetime import datetime, timedelta
from mongoengine import EmbeddedDocumentField
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()
from app.utils.enums import PlugType
from dotenv import load_dotenv
load_dotenv()
from app.config import Config
from bson import ObjectId





class User(db.Document):
    # _id = db.ObjectIdField(primary_key=True)
    email = db.EmailField(required=True)
    password = db.StringField(required=True)
    username = db.StringField(default="")
    is_deleted = db.BooleanField(default=False)
    appliances = db.ListField(EmbeddedDocumentField(Appliance),required=False,default=None)
    cloud_type= db.EnumField(PlugType, default=PlugType.MEROSS)
    cloud_password = db.StringField(required=True)
    current_month_energy = db.FloatField(default=0.0)
    energy_goal = db.FloatField(default=-1.0)
    registration_token = db.StringField(default="")
    #profile_pic
    
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
