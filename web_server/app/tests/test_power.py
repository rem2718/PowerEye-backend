#app\tests\test_power.py
from flask import Flask
from datetime import datetime
from app.controllers.power_controller import *
from app.models.user_model import User
from app.models.power_model import Power
import json
from mongoengine import connect

# Define a default connection
connect(db='flask_test_database', host='mongodb+srv://219410523:Maya2001@hems.kcuurlg.mongodb.net/flask_test_database')

# Create Flask app and push context
app = Flask(__name__)
app.config['DEBUG'] = True  # Set DEBUG mode
app.app_context().push()



def insert_power_data():
    user_id = "6536ca862e1ebac02d028f4f"
    power_data = {}  # Create an empty dictionary to store power data for multiple appliances

    # Define a list of dictionaries containing appliance IDs and their corresponding power values
    appliance_readings = [
        {"appliance_id": "6536cadde9773c46c5a5c0e6", "power_value": 99.0},
        {"appliance_id": "6536ee0bdf4c2713e782d03b", "power_value": 5.0},
        # Add more appliances and their readings as needed
    ]

    # Retrieve the user by ID
    user = User.objects.get(id=user_id)

    if not user:
        print("User not found")

    for reading in appliance_readings:
        appliance_id = reading["appliance_id"]
        power_value = reading["power_value"]

        # Find the appliance within the user's appliances
        appliance = next((app for app in user.appliances if str(app._id) == appliance_id), None)

        if not appliance:
            print(f"Appliance {appliance_id} not found")
            continue

        # Add the power reading as a field to the power_data dictionary
        power_data[str(appliance._id)] = power_value

    # Create a new Power instance
    power = Power(
        timestamp=datetime.now(),
        user=user,
        **power_data  # Unpack the power data as keyword arguments
    )

    # Save the power document
    power.save()

    print("Power data inserted successfully")


    
def test_get_most_recent_reading():
    # Assuming you have a valid user_id and appliance_id for testing
    user_id = "6536ca862e1ebac02d028f4f"
    appliance_id = "6536cadde9773c46c5a5c0e6"

    # Call the function
    response, status_code = get_most_recent_reading(user_id, appliance_id)

    # Assuming response is a Flask response object
    response_content = response.get_json()

    # Format the JSON content with indentation
    formatted_response = json.dumps(response_content, indent=4)

    # Print the formatted response
    print(formatted_response)
    
if __name__ == "__main__":
    # insert_power_data()
    test_get_most_recent_reading()