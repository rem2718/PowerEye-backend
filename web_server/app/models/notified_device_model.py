# appliance_model.py
from app.extensions import db
from bson import ObjectId


class Notified_Device(db.EmbeddedDocument):
    device_id = db.StringField()
    fcm_token = db.StringField()

    meta = {
        'collection': 'Notified_Devices'  # the real collection name here
    }