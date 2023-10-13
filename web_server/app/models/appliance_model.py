# appliance_model.py
from app.extensions import db


class Appliance(db.EmbeddedDocument):
    _id = db.ObjectIdField(primary_key=True, default=None)
    name = db.StringField()
    cloud_id = db.StringField(unique=True)
    energy = db.FloatField(default=0.0)
    is_deleted = db.BooleanField(default=False)
    connection_status = db.BooleanField()
    status = db.BooleanField(default=True)
    baseline_threshold = db.FloatField(default=-1)
    e_type = db.IntField()
    
    meta = {
        'collection': 'Appliances'  # the real collection name here
    }