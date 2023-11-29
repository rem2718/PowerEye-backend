# appliance_model.py
"""
Module defining the Appliance model.

This module defines the Appliance model as a Flask-MongoEngine embedded document.
"""
from app.extensions import db
from app.utils.enums import ApplianceType, EType


class Appliance(db.EmbeddedDocument):
    _id = db.ObjectIdField(default=None)
    name = db.StringField(default="")
    type = db.EnumField(ApplianceType)
    cloud_id = db.StringField()
    energy = db.FloatField(default=0.0)
    is_deleted = db.BooleanField(default=False)
    connection_status = db.BooleanField(default=True)
    status = db.BooleanField(default=True)
    baseline_threshold = db.FloatField(default=-1)
    e_type = db.EnumField(EType, default=EType.NONE)

    meta = {
        'collection': 'Appliances',  # the real collection name here
        'indexes': [
        {
            'fields': ['_id'],
        }
        ]
    }
