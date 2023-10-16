# power_model.py
from app.extensions import db
from .user_model import User  # Import the User model

class Power(db.DynamicDocument):
    timestamp = db.DateTimeField(required=True)
    user = db.ReferenceField('User')
    appliances_powers = db.DynamicField()  # DynamicFields pairs (applianceid: power_reading)

    meta = {
        'collection': 'Powers'  # the real collection name here
    }    

    def save(self, *args, **kwargs):
        # Prevent saving by raising an exception
        raise ReadOnlyDocumentError("This document is read-only and cannot be modified.")
        
    def update(self, *args, **kwargs):
        # Prevent updating by raising an exception
        raise ReadOnlyDocumentError("This document is read-only and cannot be updated.")
    
    def modify(self, *args, **kwargs):
        # Prevent modification by raising an exception
        raise ReadOnlyDocumentError("This document is read-only and cannot be modified.")
    
    def delete(self, *args, **kwargs):
        # Prevent deletion by raising an exception
        raise ReadOnlyDocumentError("This document is read-only and cannot be deleted.")