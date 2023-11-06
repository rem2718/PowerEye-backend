# energy_model.py
from app.extensions import db
from .user_model import User  # Import the User model


class Energy(db.DynamicDocument):
    date = db.DateField(required=True)
    user = db.ReferenceField('User')
    # Appliance ID will be used as a field name directly
    meta = {
        'collection': 'Energys'
    }    

    def save(self, *args, **kwargs):
        # Prevent saving by raising an exception
        raise ReadOnlyDocumentError("This document is read-only and cannot be modified.")