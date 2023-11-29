# power_model.py
"""
Module defining the Power model.

This module defines the Power model as a Flask-MongoEngine dynamic document
"""
from app.extensions import db
from .user_model import User


class Power(db.DynamicDocument):
    timestamp = db.DateTimeField(required=True)
    user = db.ReferenceField('User')
    # Appliance ID will be used as a field name directly

    meta = {
        'collection': 'Powers',  # the real collection name here
        'indexes': [
            {'fields': ['user', 'timestamp']},
        ],
    }