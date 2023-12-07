import pytest
from flask import Flask
import json
from mongoengine import connect
from app.controllers.room_controller import *
from unittest.mock import MagicMock  #to mock the massege

# Define a default connection
connect(db='flask_test_database', host='mongodb+srv://219410523:Maya2001@hems.kcuurlg.mongodb.net/flask_test_database')

# Create Flask app and push context
app = Flask(__name__)
app.config['DEBUG'] = True  # Set DEBUG mode
app.app_context().push()

# Test valid room name function
def test_validate_room_name_valid_name():
    user_id = "6552954c710c09f3b476eece"
    room_name = "MayatiRoom"
    result, message, status_code = validate_room_name(user_id, room_name)
    assert result == True
    assert message == None
    assert status_code == None

# def test_validate_room_name_invalid_user():
#     user = None
#     name = "Room 1"
#     result = validate_room_name(user, name)
#     expected = (False, {'message': 'User not found'}, 404)
#     assert result == expected

# def test_validate_room_name_invalid_name():
#     user = mock_user
#     invalid_name = "R"
#     result = validate_room_name(user, invalid_name)
#     expected = (False, {'message': 'The room name should be a string with 2 or more characters'}, 400)
#     assert result == expected

# def test_validate_room_name_duplicate_name(mock_user, mocker):
#     name = "Room 1"
#     mocker.patch('mymodule.Room.objects', return_value=[mock_room])
#     result = validate_room_name(mock_user, name)
#     expected = (False, {'message': 'The room name must be unique among all rooms in your account'}, 400)
#     assert result == expected

# def test_validate_room_name_exception(mock_user, mocker):
#     name = "Room 1"
#     mocker.patch('mymodule.Room.objects', side_effect=Exception("Some error occurred"))
#     result = validate_room_name(mock_user, name)
#     expected = (False, {'message': 'Error occurred while validating name: Some error occurred'}, 500)
#     assert result == expected
