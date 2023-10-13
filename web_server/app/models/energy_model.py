# energy_model.py
from app.extensions import db
from .user_model import User  # Import the User model


class Energy(db.DynamicDocument):
    date = db.DateField(required=True)
    user_id = db.ReferenceField('User')
    energy_readings = db.DynamicField()  # DynamicFields pairs (applianceid: energy_reading)

    meta = {
        'collection': 'Energies'  # the real collection name here
    }    

    # Add any additional methods or properties as needed