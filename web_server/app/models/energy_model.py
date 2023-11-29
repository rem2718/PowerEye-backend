# energy_model.py
"""
Module defining the Energy model.

This module defines the Energy model as a Flask-MongoEngine dynamic document.
"""
from app.extensions import db
from .user_model import User




class Energy(db.DynamicDocument):
    date = db.DateField(required=True)
    user = db.ReferenceField('User')
    # Appliance ID will be used as a field name directly
    meta = {
        'collection': 'Energys',
        'indexes': [
            {'fields': ['user', 'date']},
        ],
    }
