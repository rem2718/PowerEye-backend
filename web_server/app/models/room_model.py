# room_model.py
from app.extensions import db
from .appliance_model import Appliance  # Import the Appliance model
from .user_model import User  # Import the User model
from mongoengine import EmbeddedDocumentField, ReferenceField



class Room(db.Document):
    name = db.StringField(required=True)
    appliances = db.ListField(db.ObjectIdField())
    user_id = db.ReferenceField('User')  # Reference to the User document

    meta = {
        'collection': 'Rooms'
    }
