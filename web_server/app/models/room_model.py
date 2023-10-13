# room_model.py
from app.extensions import db
from .appliance_model import Appliance  # Import the Appliance model
from .user_model import User  # Import the User model
from mongoengine import ReferenceField
from mongoengine import EmbeddedDocumentField



class Room(db.Document):
    name = db.StringField(required=True)
    appliances = db.ListField(EmbeddedDocumentField(Appliance))
    user_id = db.ReferenceField('User')  # Reference to the User document

    meta = {
        'collection': 'Rooms'
    }
