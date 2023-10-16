# appliance_model.py
from app.extensions import db


class Appliance(db.EmbeddedDocument):
    _id = db.ObjectIdField(unique=True, default=None)
    name = db.StringField(unique=True)
    type = db.StringField(default=None)
    cloud_id = db.StringField(unique=True)
    energy = db.FloatField(default=0.0)
    is_deleted = db.BooleanField(default=False)
    connection_status = db.BooleanField(default= True)
    status = db.BooleanField(default=True)
    baseline_threshold = db.FloatField(default=-1)
    e_type = db.IntField()
    
    meta = {
        'collection': 'Appliances'  # the real collection name here
    }