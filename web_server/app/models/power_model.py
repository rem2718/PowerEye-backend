# power_model.py
from app.extensions import db 
from .user_model import User  # Import the User model

class Power(db.DynamicDocument):
    timestamp = db.DateTimeField(required=True)
    user = db.ReferenceField('User')
    # Appliance ID will be used as a field name directly

    meta = {
        'collection': 'Powers'  # the real collection name here
    }    

    def save(self, *args, **kwargs):
        # Prevent saving by raising an exception
        raise ReadOnlyDocumentError("This document is read-only and cannot be modified.")
