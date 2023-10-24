#app\tests\test_room.py
from flask import Flask
from app.controllers.room_controller import *
from app.models.user_model import User
import json
from mongoengine import connect

# Define a default connection
connect(db='flask_test_database', host='mongodb+srv://219410523:Maya2001@hems.kcuurlg.mongodb.net/flask_test_database')

# Create Flask app and push context
app = Flask(__name__)
app.config['DEBUG'] = True  # Set DEBUG mode
app.app_context().push()

def get_sample_user(user_id):
    try:
        user = User.objects.get(id=user_id)
        return user
    except DoesNotExist:
        return None

def test_create_room():
    # Sample data
    user_id = "6536ca862e1ebac02d028f4f"
    user = User.objects.get(id=user_id)
    if not user:
        print("User not found in general test")

    name = "Sample Room3"
    appliance_ids = ["6536cadde9773c46c5a5c0e6"]
    # Call the function
    response, status_code = create_room(user_id, name, appliance_ids)

    # Print the response
    print(response)
    print(status_code)
    
        
    # Print the JSON content of the response
    if response is not None:
        response_content = response.get_json()
        print(response_content)
    else:
        print("Response is None")

def test_get_all_appliances():
    user_id = "6536ca862e1ebac02d028f4f"
    user = get_sample_user(user_id)
    room_id= "653781772ab70da9a4a06dbd"

    if not user:
        print("User not found in general test")
        return

    response, status_code = get_room_appliances(user_id,room_id)

    # Assuming response is a Flask response object
    response_content = response.get_json()

    # Format the JSON content with indentation
    formatted_response = json.dumps(response_content, indent=4)

    # Print the formatted response
    print(formatted_response)

def test_add_appliance_to_room():
    user_id = "6536ca862e1ebac02d028f4f"
    room_id = "653781772ab70da9a4a06dbd"
    appliance_id = "6536cd3b176f465e45c0894b"

    response, status_code = add_appliance_to_room(user_id, room_id, appliance_id)

    # Assuming response is a Flask response object
    response_content = response.get_json()

    # Format the JSON content with indentation
    formatted_response = json.dumps(response_content, indent=4)

    # Print the formatted response
    print(formatted_response)


def test_get_user_rooms():
    user_id = "6536ca862e1ebac02d028f4f"
    response, status_code = get_all_user_rooms(user_id)

    # Assuming response is a Flask response object
    response_content = response.get_json()

    # Format the JSON content with indentation
    formatted_response = json.dumps(response_content, indent=4)

    # Print the formatted response
    print(formatted_response)
    
if __name__ == "__main__":
    # test_get_all_appliances()
    # test_create_room()
    # test_add_appliance_to_room()
    test_get_user_rooms()