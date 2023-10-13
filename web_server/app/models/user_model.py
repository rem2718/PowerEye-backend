
from app.extensions import db
from .appliance_model import Appliance  # Import the Appliance model
import jwt
from datetime import datetime, timedelta
from mongoengine import EmbeddedDocumentField
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()



class User(db.Document):
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    username = db.StringField()
    is_deleted = db.BooleanField(default=False)
    appliances = db.ListField(EmbeddedDocumentField(Appliance))
    cloud_type= db.IntField()
    cloud_password = db.StringField(required=True)
    current_month_energy = db.FloatField(default=0.0)
    energy_goal = db.FloatField(default=0.0)
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
            'user_id': str(self.id),
            'exp': datetime.utcnow() + timedelta(days=30)  # Token expiration time
        }
        return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
