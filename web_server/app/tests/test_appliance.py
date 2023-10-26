from flask import Flask
from app.controllers.appliance_controller import *
from app.models.user_model import User
from app.models.appliance_model import ApplianceType, EType
import json
from mongoengine import connect

# Define a default connection
connect(db='flask_test_database', host='mongodb+srv://219410523:Maya2001@hems.kcuurlg.mongodb.net/flask_test_database')

# Create Flask app and push context
app = Flask(__name__)
app.config['DEBUG'] = True  # Set DEBUG mode
app.app_context().push()

def test_add_user():
        # Create a test user
    user = User(email='test@example.com', password='testpassword', cloud_password='your_cloud_password_here')
    user.save()
def get_sample_user(user_id):
    try:
        user = User.objects.get(id=user_id)
        return user
    except DoesNotExist:
        return None

def test_add_appliance():
    user_id = "6536ca862e1ebac02d028f4f"
    user = get_sample_user(user_id)

    if not user:
        print("User not found in general test")
        return

    name = "Sample Appliance8"
    cloud_id = "sample_cloud_id8"
    appliance_type = ApplianceType.CAMERA

    print(appliance_type.value)
    print(map_appliance_type_to_e_type(appliance_type).value)

    response, status_code = add_appliance(user_id, name, cloud_id, appliance_type)

    print(response)
    print(status_code)

    if response is not None:
        print(response.get_json()['message'])
    else:
        print("Response is None")

def test_appliance_type_mapping():
    for appliance_type in ApplianceType:
        e_type = map_appliance_type_to_e_type(appliance_type)
        print(f"ApplianceType: {appliance_type}, EType: {e_type}")

def test_get_all_appliances(user_id):
    response, status_code = get_all_appliances(user_id)

    # Assuming response is a Flask response object
    response_content = response.get_json()

    # Format the JSON content with indentation
    formatted_response = json.dumps(response_content, indent=4)

    # Print the formatted response
    print(formatted_response)

def test_delete_appliance():
    user_id = "6536ca862e1ebac02d028f4f"
    appliance_id = "65398f97e4da3793b9532605"  # Replace with a valid appliance ID

    response, status_code = delete_appliance(user_id, appliance_id)


    if response is not None:
        print(response.get_json()['message'])
    else:
        print("Response is None")

def test_update_appliance():
    user_id = "6536ca862e1ebac02d028f4f"
    appliance_id = "6536cd3b176f465e45c0894b"  # Replace with a valid appliance ID
    new_name = "New Appliance Name"

    response, status_code = update_appliance_name(user_id, appliance_id, new_name)

    print(response)
    print(status_code)

    if response is not None:
        print(response.get_json()['message'])
    else:
        print("Response is None")

def test_switch_appliance():
    user_id = "6536ca862e1ebac02d028f4f"
    appliance_id = "6536cd3b176f465e45c0894b"  # Replace with a valid appliance ID
    new_status = False

    response, status_code = switch_appliance(user_id, appliance_id, new_status)

    print(response)
    print(status_code)

    if response is not None:
        print(response.get_json()['message'])
    else:
        print("Response is None")

def test_get_appliance_by_id():
    # Assuming you have a valid user_id and appliance_id for testing
    user_id = "6536ca862e1ebac02d028f4f"
    appliance_id = "6536cd3b176f465e45c0894b"

    # Call the function
    response, status_code = get_appliance_by_id(user_id, appliance_id)

    # Assuming response is a Flask response object
    response_content = response.get_json()

    # Format the JSON content with indentation
    formatted_response = json.dumps(response_content, indent=4)

    # Print the formatted response
    print(formatted_response)

if __name__ == "__main__":
    # test_add_appliance()
    # test_appliance_type_mapping()
    # test_get_all_appliances("6536ca862e1ebac02d028f4f")
    # test_add_user()
    test_delete_appliance()
    # update_appliance_name()
    # test_switch_appliance()
    # test_get_appliance_by_id()
