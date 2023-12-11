import pytest
from flask import Flask
import json
from mongoengine import connect
from app.controllers.power_controller import *
from unittest.mock import MagicMock  #to mock the massege

# Define a default connection
connect(db='hemsproject', host='mongodb+srv://219410523:Maya2001@hems.kcuurlg.mongodb.net/hemsproject')

# Create Flask app and push context
app = Flask(__name__)
app.config['DEBUG'] = True  # Set DEBUG mode
app.app_context().push()

# Test case for successful retrieval of power value
def test_get_most_recent_reading_success():
    user_id = "64d154bc94895e0b4c1bc080"
    appliance_id = "64d1650b93d44252699aa223"
    # Call the method
    response, status_code = get_most_recent_reading(user_id, appliance_id)
    # Assertion
    assert status_code == 200

# Test case for appliance not found or deleted
def test_get_most_recent_reading_appliance_not_found_or_deleted():
    user_id = "64d154bc94895e0b4c1bc080"
    appliance_id = "64d162ff93d44252699aa21d"
    # Call the method
    response, status_code = get_most_recent_reading(user_id, appliance_id)
    # Assertion
    assert status_code == 404

# Test case for no power data available
def test_get_most_recent_reading_no_power_data_available():
    user_id = "64d154bc94895e0b4c1bc080"
    appliance_id = "64d162ff93d44252699aa21d"
    # Call the method
    response, status_code = get_most_recent_reading(user_id, appliance_id)
    # Assertion
    assert status_code == 404

# Test case for exception handling
def test_get_most_recent_reading_exception():
    user_id = "6536ca862e1ebac02d028f4f"
    appliance_id = "6536cadde9773c46c5a5c0e6"
    # Call the method
    response, status_code = get_most_recent_reading(user_id, appliance_id)
    # Assertion
    assert status_code == 500