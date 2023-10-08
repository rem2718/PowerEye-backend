from app import db
import jwt
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

class User(db.Document):
    username = db.StringField(required=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    merros_password = db.StringField(required=True)
    energy_goal = db.FloatField(default=0.0)
    is_deleted = db.BooleanField(default=False)
    profile_pic = db.StringField()
    token = db.StringField()
    appliances = db.ListField(db.DictField())  # List of appliance dictionaries

    # Add any additional methods or properties as needed
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def generate_token(self):
        payload = {
            'user_id': str(self.id),
            'exp': datetime.utcnow() + timedelta(days=30)  # Token expiration time
        }
        return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')