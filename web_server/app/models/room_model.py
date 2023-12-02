# room_model.py
"""
Module defining the Room model.

This module defines the Room model as a Flask-MongoEngine document.
"""
from mongoengine import ReferenceField
from app.extensions import db
from .user_model import User  




class Room(db.Document):
    name = db.StringField(required=True)
    appliances = db.ListField(db.ObjectIdField())
    user_id = db.ReferenceField('User') 

    meta = {
        'collection': 'Rooms'
    }
