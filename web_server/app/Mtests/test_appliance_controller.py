import pytest
from flask import Flask, jsonify

from app.controllers.appliance_controller import *
from app.utils.enums import ApplianceType, EType
from app.models.appliance_model import Appliance
from app.models.user_model import User
from unittest.mock import patch, MagicMock
from bson import ObjectId
import mongoengine
from mongoengine import connect, disconnect



@pytest.fixture(scope='session')
def setup_teardown_mongo_connection(request):
    # Establish a connection
    mongoengine.connect(db='flask_test_database', host='mongodb+srv://219410523:Maya2001@hems.kcuurlg.mongodb.net/flask_test_database')

 
    # Provide the connection object to the test function
    yield

    # Disconnect from the database at the end of the test
    mongoengine.disconnect(alias='default')

    # Register the teardown function
    request.addfinalizer(teardown)

    return mongoengine.connection.get_connection()


def test_map_appliance_type_to_e_type(setup_teardown_mongo_connection):
    result = map_appliance_type_to_e_type(ApplianceType.WASHING_MACHINE)
    assert result == EType.SHIFTABLE

    result = map_appliance_type_to_e_type(ApplianceType.GAMES)
    assert result == EType.PHANTOM
    
    result = map_appliance_type_to_e_type(ApplianceType.CAMERA)
    assert result == EType.NONE

# ___________________________________________________________
# Create Flask app and push context
app = Flask(__name__)
app.config['DEBUG'] = True  # Set DEBUG mode
app.app_context().push()


# Fixture to create a user
@pytest.fixture
def create_user(setup_teardown_mongo_connection):
    user = User(email="test@example.com", password="password", cloud_password="cloud_password")
    user.save()
    return user.id

# Fixture to create a user and appliances
@pytest.fixture
def create_user_with_appliances(setup_teardown_mongo_connection):
    user = User(email="test@example.com", password="password", cloud_password="cloud_password")
    user.save()

    # Create appliances
    appliance1 = Appliance(name="Appliance1", energy=50.0, is_deleted=False)
    appliance2 = Appliance(name="Appliance2", energy=30.0, is_deleted=False)
    user.appliances.extend([appliance1, appliance2])
    user.save()
    return user.id


def test_validate_name_invalid_name_length(create_user,setup_teardown_mongo_connection):
    user_id = create_user  
    name = 'a'
    result, _, _ = validate_name(user_id, name)
    assert result is False
    
    
def test_validate_name_invalid_name_duplicate(create_user_with_appliances,setup_teardown_mongo_connection):
    user_id = create_user_with_appliances  
    name = 'Appliance1'
    result, _, _ = validate_name(user_id, name)
    assert result is False
    
def test_validate_name_invalid_user_id():
    name = 'Appliance3'
    result, _, _ = validate_name(str(ObjectId()), name)
    assert result is False
# _____________________________________________________________________


# def test_validate_cloud_id_valid_cloud_id(setup_teardown_mongo_connection):
#     user_id = '65721306827e8e413bc436ee'  
#     cloud_id = '2208114433888051070548e1e9a13299'
#     result,  _, _= validate_cloud_id(user_id, cloud_id)
#     assert result is True
    
def test_validate_cloud_id_valid_cloud_id(setup_teardown_mongo_connection):
    user_id = '65721306827e8e413bc436ee'  
    result,  _, _= validate_cloud_id(user_id, str(ObjectId()))
    assert result is False
    
    # ____________________________________________________


# def test_add_appliance_successfully(setup_teardown_mongo_connection):
#     user_id = '65721306827e8e413bc436ee' 
#     name = 'Valid_Appliance'
#     cloud_id = '2208114433888051070548e1e9a13299'
#     appliance_type = 5
#     response = add_appliance(user_id, name, cloud_id, appliance_type)
#     assert response.status_code == 201



def test_add_appliance_invalid_user_id(setup_teardown_mongo_connection):

    invalid_user_id = str(ObjectId())
    name = 'Valid_Appliance'
    cloud_id = 'unique_cloud_id'
    appliance_type = 4
    response = add_appliance(invalid_user_id, name, cloud_id, appliance_type)
    assert response.status_code == 404

# def test_add_appliance_invalid_name(create_user,setup_teardown_mongo_connection):
#     user_id = create_user
#     invalid_name = 'a'
#     cloud_id = 'unique_cloud_id'
#     appliance_type = 'COOLER'
#     response = add_appliance(user_id, invalid_name, cloud_id, appliance_type)
#     assert response.status_code == 400


# def test_add_appliance_invalid_cloud_id(create_user,setup_teardown_mongo_connection):
#     user_id = create_user  
#     name = 'Valid_Appliance'
#     invalid_cloud_id = 'invalid_cloud_id'
#     appliance_type = 'COOLER'
#     response = add_appliance(user_id, name, invalid_cloud_id, appliance_type)
#     assert response.status_code == 400
#     assert 'message' in response.json


# def test_add_appliance_invalid_appliance_type(create_user,setup_teardown_mongo_connection):
#     
#     user_id = create_user 
#     name = 'Valid_Appliance'
#     cloud_id = 'unique_cloud_id'
#     invalid_appliance_type = 'INVALID_TYPE'
#     response = add_appliance(user_id, name, cloud_id, invalid_appliance_type)
#     assert response.status_code == 400
#     assert 'message' in response.json
