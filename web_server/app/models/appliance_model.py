# appliance_model.py
from app.extensions import db
from enum import Enum

class EType(Enum):
    NONE = 1
    SHIFTABLE = 2
    PHANTOM = 3


class ApplianceType(Enum):
    COOLER = 1
    LIGHTING = 2
    HEATER = 3
    COOKER_MAKER = 4
    MIXER = 5
    CLOCK_ALEXA = 6
    HAIR_DRYER = 7
    CAMERA = 8
    WASHING_MACHINE = 9
    WASHER = 10
    DISHWASHER = 11
    CLOTHES_DRYER = 12
    IRON = 13
    VACUUM_CLEANER = 14
    AIR_PURIFIER = 15
    GAMES = 16
    DISPLAYER = 17
    AUDIO_OUTPUT = 18
    PRINTER = 19
    CHARGER = 20
    RECEIVER = 21
    SEWING_MACHINE = 22
    SPORTS_MACHINE = 23

    


class Appliance(db.EmbeddedDocument):
    _id = db.StringField(default=None)
    name = db.StringField()
    type = db.EnumField(ApplianceType)
    cloud_id = db.StringField()
    energy = db.FloatField(default=0.0)
    is_deleted = db.BooleanField(default=False)
    connection_status = db.BooleanField(default= True)
    status = db.BooleanField(default=True)
    baseline_threshold = db.FloatField(default=-1)
    e_type = db.EnumField(EType, default=EType.NONE)

    
    meta = {
        'collection': 'Appliances'  # the real collection name here
    }