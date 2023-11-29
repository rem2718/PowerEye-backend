# notified_device_model.py
"""
Module defining the NotifiedDevicedel.

This module defines the NotifiedDevice model as a Flask-MongoEngine embedded document.

"""
from app.extensions import db

class NotifiedDevice(db.EmbeddedDocument):
    device_id = db.StringField()
    fcm_token = db.StringField()

    meta = {
        'collection': 'NotifiedDevices'  # the real collection name here
    }
