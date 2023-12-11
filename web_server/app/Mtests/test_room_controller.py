import pytest
from flask import Flask
import json
from mongoengine import connect
from app.controllers.room_controller import *
from unittest.mock import MagicMock  #to mock the massege
from unittest import mock

# Define a default connection
connect(db='hemsproject', host='mongodb+srv://219410523:Maya2001@hems.kcuurlg.mongodb.net/hemsproject')

# Create Flask app and push context
app = Flask(__name__)
app.config['DEBUG'] = True  # Set DEBUG mode
app.app_context().push()

# ---------------------------------------Validate Room Name Test-----------------------------------------------------------

# Test valid room name function
def test_validate_room_name_valid_name():
    result, message, status_code = validate_room_name(User(), "MayaRoom")
    assert result == True
    assert message == None
    assert status_code == None

# Test valid room name function for non-existanse user 
def test_validate_room_name_user_not_found():
    result, message, status_code = validate_room_name(None, "Maya")
    assert result == False
    assert json.loads(message.get_data(as_text=True)) == {'message': 'User not found'}
    assert status_code == 404

# Test room name function using invalid type
def test_validate_room_name_invalid_name_type():
    result, message, status_code = validate_room_name(User(), 123)
    assert result == False
    assert json.loads(message.get_data(as_text=True)) == {'message': 'The room name should be a string with 2 or more characters'}
    assert status_code == 400

# Test room name function using invalid length
def test_validate_room_name_invalid_name_length():
    result, message, status_code = validate_room_name(User(), "m")
    assert result == False
    assert json.loads(message.get_data(as_text=True)) == {'message': 'The room name should be a string with 2 or more characters'}
    assert status_code == 400

# Test room name function using duplicate name
def test_validate_room_name_duplicate_name():
    # Create a test user
    user = User()
    # Create a test room with the desired name and associate it with the user
    room = Room(user_id=user.id, name="Test")
    room.save()
    result, message, status_code = validate_room_name(user, "Test")
    assert result == False
    assert json.loads(message.get_data(as_text=True)) == {'message': 'The room name must be unique among all rooms in your account'}
    assert status_code == 400

# ---------------------------------------Create Room Test-----------------------------------------------------------

# Test create room function using valid info
def test_create_room_success():
    response, status_code = create_room('64d154bc94895e0b4c1bc080', 'Test Room', ['64d1659d93d44252699aa226'])
    # print(response.get_data(as_text=True))
    # print(status_code)
    assert status_code == 201

# Test create room function for non-existance user
def test_create_room_user_not_found():
    response, status_code = create_room('0062954c710c09f3b476eece', 'Test Room1', ['64d1656693d44252699aa225'])
    assert status_code == 404

# Test create room function without adding appliance
def test_create_room_no_appliances_provided():
    response, status_code = create_room('64d154bc94895e0b4c1bc080', 'Test Room1', [])
    assert status_code == 400
    assert json.loads(response.get_data(as_text=True)) == {'error': 'No appliances provided for the room.'}

# Test create room function without providing valid name
def test_create_room_invalid_room_name():
    response, status_code = create_room('64d154bc94895e0b4c1bc080', 'm', ['64d1656693d44252699aa225'])
    assert status_code == 400
    assert json.loads(response.get_data(as_text=True)) =={'message': 'The room name should be a string with 2 or more characters'}

# Test create room function for non-existance appliance
def test_create_room_appliance_not_found():
    response, status_code = create_room('64d154bc94895e0b4c1bc080', 'Test Room2', ['64d162ff93d44252699aa21d'])
    assert status_code == 404

# Test create room function for deleted appliance
def test_create_room_appliance_deleted():
    response, status_code = create_room('64d154bc94895e0b4c1bc080', 'Test Room', ['656d146ba0fcf7ee5f4b96d7'])
    assert status_code == 400

# ---------------------------------------Get Room Appliance Test-----------------------------------------------------------

# Test get room appliance function successsfully
def test_get_room_appliances_success():
    response, status_code = get_room_appliances('64d154bc94895e0b4c1bc080', '65732099827e8e413bc436f7')
    assert status_code == 200

# Test get room appliance function for non-existance user
def test_get_room_appliances_user_not_found():
    response, status_code = get_room_appliances('65678dba8535b0176edcda69', '65732099827e8e413bc436f7')
    assert status_code == 500

# Test get room appliance function for non-existance room
def test_get_room_appliances_room_not_found():
    response, status_code = get_room_appliances('64d154bc94895e0b4c1bc080', '65733c9ed7070c506570d469')
    assert status_code == 404
    assert json.loads(response.get_data(as_text=True)) == {'error': 'Room not found or does not belong to the user'}

# Test get room appliance function for empty room/user doesn't have appliance in the room
def test_get_room_appliances_no_user_appliances():
    response, status_code = get_room_appliances('65721306827e8e413bc436ee', '6576ea95bf88dda3ea0fac59')
    assert status_code == 200

# ---------------------------------------Switch Room Test-----------------------------------------------------------
def test_switch_room_some_appliances_not_updated():
    response, status_code = switch_room('64d154bc94895e0b4c1bc080', '65734345413329dd0d56e2b7', False)
    # print(response.get_data(as_text=True))
    # print(status_code)
    assert status_code == 400

# def test_switch_room_all_appliances_updated():
#     response, status_code = switch_room('64d154bc94895e0b4c1bc080', '65734345413329dd0d56e2b7', True)
#     print(response.get_data(as_text=True))
#     print(status_code)
#     assert status_code == 200

def test_switch_room_user_not_found():
    response, status_code = switch_room('65678dba8535b0176edcda69', '656d30f357fbb78f4d61e873', True)
    assert status_code == 404

def test_switch_room_room_not_found():
    response, status_code = switch_room('64d154bc94895e0b4c1bc080', '656d30f357fbb78f4d61e873', True)
    assert status_code == 404

def test_switch_room_invalid_status_value():
    response, status_code = switch_room('64d154bc94895e0b4c1bc080', '65734345413329dd0d56e2b7', 'T')
    assert status_code == 400

def test_switch_room_no_room_appliances():
    response, status_code = switch_room('65721306827e8e413bc436ee', '657344b9224316b09d57f038', True)
    assert status_code == 200

# ---------------------------------------Add Appliance To Room Test-----------------------------------------------------------
# if you run test multiple time it will fail since we added the appliance in the first run
# add appliance successfully to the room
def test_add_appliances_to_room_appliances_added_successfully():
    response, status_code = add_appliances_to_room('64d154bc94895e0b4c1bc080', '65734345413329dd0d56e2b7', ['64d1687493d44252699aa22c'])
    assert status_code == 200

def test_add_appliances_to_room_user_not_found():
    response, status_code = add_appliances_to_room('65678dba8535b0176edcda69', '65734345413329dd0d56e2b7', ['64d1659d93d44252699aa225'])
    assert status_code == 500

def test_add_appliances_to_room_room_not_found():
    response, status_code = add_appliances_to_room('64d154bc94895e0b4c1bc080', '656d30f357fbb78f4d61e873', ['64d1659d93d44252699aa225'])
    assert status_code == 404

def test_add_appliances_to_room_invalid_appliance_ids_not_list():
    response, status_code = add_appliances_to_room('64d154bc94895e0b4c1bc080', '65734345413329dd0d56e2b7', '64d1659d93d44252699aa225')
    assert status_code == 400

def test_add_appliances_to_room_appliance_not_found():
    response, status_code = add_appliances_to_room('64d154bc94895e0b4c1bc080', '65734345413329dd0d56e2b7', ['64d1629393d44252699aa21b'])
    assert status_code == 400

def test_add_appliances_to_room_appliance_marked_deleted():
    response, status_code = add_appliances_to_room('64d154bc94895e0b4c1bc080', '65734345413329dd0d56e2b7', ['64d1659d93d44252699aa225'])
    assert status_code == 400

def test_add_appliances_to_room_appliances_already_in_room():
    response, status_code = add_appliances_to_room('64d154bc94895e0b4c1bc080', '656df4efaba9ceb940072283', ['64d1682993d44252699aa22a'])
    assert status_code == 400

# ---------------------------------------Get All User Room Test-----------------------------------------------------------
def test_get_all_user_rooms_success():
    response, status_code = get_all_user_rooms('64d154bc94895e0b4c1bc080')
    assert status_code == 200

def test_get_all_user_rooms_user_not_found():
    response, status_code = get_all_user_rooms('65678dba8535b0176edcda69')
    assert status_code == 500

def test_get_all_user_rooms_no_rooms_found():
    response, status_code = get_all_user_rooms('64d154d494895e0b4c1bc081') #qatar
    print(response.get_data(as_text=True))
    print(status_code)
    assert status_code == 404

def test_get_all_user_rooms_appliance_not_found():
    response, status_code = get_all_user_rooms('656ef0fe08a5e799018f9771')
    assert status_code == 500

# ---------------------------------------Delete Appliance From Room Test-----------------------------------------------------------
def test_delete_appliance_from_room_success():
    response, status_code = delete_appliance_from_room('64d154bc94895e0b4c1bc080', '65734345413329dd0d56e2b7', '64d1685693d44252699aa22b')
    assert status_code == 200

def test_delete_appliance_from_room_user_not_found():
    response, status_code = delete_appliance_from_room('65678dba8535b0176edcda69', '656d0fc737f00ff90a3c9847', '656d146ba0fcf7ee5f4b96d7')
    assert status_code == 404

def test_delete_appliance_from_room_room_not_found():
    response, status_code = delete_appliance_from_room('64d154bc94895e0b4c1bc080', '656ebbae08a5e799018f976e', '64d1629393d44252699aa21b')
    assert status_code == 404

def test_delete_appliance_from_room_appliance_not_found():
    response, status_code = delete_appliance_from_room('64d154bc94895e0b4c1bc080', '65734345413329dd0d56e2b7', '64d167a193d44252699aa228')
    assert status_code == 404

# ---------------------------------------Update Room Name Test-----------------------------------------------------------
def test_update_room_name_success():
    response, status_code = update_room_name('656ef0fe08a5e799018f9771', '6574ef8ad5efe12fd9baea32', 'empty room test')
    assert status_code == 200

def test_update_room_name_user_not_found():
    response, status_code = update_room_name('65678dba8535b0176edcda69', '656d0fc737f00ff90a3c9847', 'Livingroom')
    assert status_code == 404

def test_update_room_name_room_not_found():
    response, status_code = update_room_name('656ef0fe08a5e799018f9771', '65734345413329dd0d56e2b7', 'Kitchen')
    assert status_code == 404

def test_update_room_name_invalid_name():
    response, status_code = update_room_name('656ef0fe08a5e799018f9771', '6574ef8ad5efe12fd9baea32', 'm')
    assert status_code == 400

# ---------------------------------------Delete Room Test-----------------------------------------------------------
def test_delete_room_success():
    response, status_code = delete_room('656ef0fe08a5e799018f9771', '65776b6e79a86c5419a4726c')
    assert status_code == 200

def test_delete_room_user_not_found():
    response, status_code = delete_room('65678dba8535b0176edcda69', '656d0fc737f00ff90a3c9847')
    assert status_code == 404

def test_delete_room_room_not_found():
    response, status_code = delete_room('656ef0fe08a5e799018f9771', '65734345413329dd0d56e2b7')
    assert status_code == 404