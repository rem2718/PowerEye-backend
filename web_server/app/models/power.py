from app import db

class Power(db.Document):
    timestamp = db.DateTimeField(required=True)
    user_id = db.ObjectIdField(required=True)
    power_readings = db.DictField()  # DynamicFields pairs (applianceid: power_reading)

    # Add any additional methods or properties as needed
