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