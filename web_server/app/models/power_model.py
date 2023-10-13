# power_model.py
from app.extensions import db
from .user_model import User  # Import the User model

class Power(db.DynamicDocument):
    timestamp = db.DateTimeField(required=True)
    user_id = db.ReferenceField('User')
    appliances_powers = db.DynamicField()  # DynamicFields pairs (applianceid: power_reading)

    meta = {
        'collection': 'Powers'  # the real collection name here
    }    

    # Add any additional methods or properties as needed