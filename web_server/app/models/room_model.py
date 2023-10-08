from app import db

class Room(db.Document):
    name = db.StringField(required=True)
    appliance_list = db.ListField(db.ObjectIdField())  # List of appliance IDs
    user_id = db.ObjectIdField(required=True)

    # Add any additional methods or properties as needed
