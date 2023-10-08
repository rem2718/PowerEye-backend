from app import db

class DailyEnergy(db.Document):
    timestamp = db.DateTimeField(required=True)
    user_id = db.ObjectIdField(required=True)
    energy_readings = db.DictField()  # DynamicFields pairs (applianceid: energy_reading)

    # Add any additional methods or properties as needed
