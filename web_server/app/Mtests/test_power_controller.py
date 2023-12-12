import pytest
from flask import Flask
import json
import mongoengine
from mongoengine import connect, disconnect
from app.controllers.power_controller import *


@pytest.fixture(scope='function')  # Use 'function' scope for per-function setup/teardown
def setup_teardown_mongo_hemsproject_connection(request):
    
    # Disconnect if already connected
    mongoengine.disconnect(alias='default')
    # Establish a connection
    mongoengine.connect(db='hemsproject', host='mongodb+srv://219410523:Maya2001@hems.kcuurlg.mongodb.net/hemsproject', alias='default')

    # Define a teardown function to disconnect after the test
    def teardown():
        mongoengine.disconnect(alias='default')


    # Register the teardown function
    request.addfinalizer(teardown)

    return mongoengine.connection.get_connection()


# Create Flask app and push context
app = Flask(__name__)
app.config['DEBUG'] = True  # Set DEBUG mode
app.app_context().push()

# Your test cases go here...

# Test case for successful retrieval of power value
def test_get_most_recent_reading_success(setup_teardown_mongo_hemsproject_connection):
    user_id = "64d154bc94895e0b4c1bc080"
    appliance_id = "64d1650b93d44252699aa223"
    # Call the method
    response, status_code = get_most_recent_reading(user_id, appliance_id)
    # Assertion
    assert status_code == 200

# Test case for appliance not found or deleted
def test_get_most_recent_reading_appliance_not_found_or_deleted(setup_teardown_mongo_hemsproject_connection):
    user_id = "64d154bc94895e0b4c1bc080"
    appliance_id = "64d162ff93d44252699aa21d"
    # Call the method
    response, status_code = get_most_recent_reading(user_id, appliance_id)
    # Assertion
    assert status_code == 404

# Test case for no power data available
def test_get_most_recent_reading_no_power_data_available(setup_teardown_mongo_hemsproject_connection):
    user_id = "64d154bc94895e0b4c1bc080"
    appliance_id = "64d162ff93d44252699aa21d"
    # Call the method
    response, status_code = get_most_recent_reading(user_id, appliance_id)
    # Assertion
    assert status_code == 404

# Test case for exception handling
def test_get_most_recent_reading_exception(setup_teardown_mongo_hemsproject_connection):
    user_id = "6536ca862e1ebac02d028f4f"
    appliance_id = "6536cadde9773c46c5a5c0e6"
    # Call the method
    response, status_code = get_most_recent_reading(user_id, appliance_id)
    # Assertion
    assert status_code == 500
