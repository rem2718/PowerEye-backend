import pytest
from flask import Flask
import json
from mongoengine import connect
from app.controllers.user_controller import *
from unittest.mock import MagicMock  #to mock the massege

# Define a default connection
connect(db='flask_test_database', host='mongodb+srv://219410523:Maya2001@hems.kcuurlg.mongodb.net/flask_test_database')

# Create Flask app and push context
app = Flask(__name__)
app.config['DEBUG'] = True  # Set DEBUG mode
app.app_context().push()

# Test validate_password function
def test_valid_password():
    password = "@SmartMaya1"
    result, message, status_code = validate_password(password)
    assert result == True
    assert message == None
    assert status_code == None

def test_password_length():
    password = "maya1!"
    response = validate_password(password)
    result, message, status_code = response
    assert result is False
    assert json.loads(message.get_data(as_text=True)) == {'message': 'Password should contain at least 8 characters, including at least one uppercase letter, one lowercase letter, one digit, and one special character'}
    assert status_code == 400

def test_no_special_character_password():
    password = "SmartMaya1"
    response = validate_password(password)
    result, message, status_code = response
    assert result is False
    assert json.loads(message.get_data(as_text=True)) == {'message': 'Password should contain at least 8 characters, including at least one uppercase letter, one lowercase letter, one digit, and one special character'}
    assert status_code == 400

def test_empty_password():
    password = ""
    response = validate_password(password)
    result, message, status_code = response
    assert result is False
    assert json.loads(message.get_data(as_text=True)) == {'message': 'Password should contain at least 8 characters, including at least one uppercase letter, one lowercase letter, one digit, and one special character'}
    assert status_code == 400

def test_no_upper_case_password():
    password = "@smartmaya1"
    response = validate_password(password)
    result, message, status_code = response
    assert result is False
    assert json.loads(message.get_data(as_text=True)) == {'message': 'Password should contain at least 8 characters, including at least one uppercase letter, one lowercase letter, one digit, and one special character'}
    assert status_code == 400

def test_no_lower_case_password():
    password = "@SMARTMAYA1"
    response = validate_password(password)
    result, message, status_code = response
    assert result is False
    assert json.loads(message.get_data(as_text=True)) == {'message': 'Password should contain at least 8 characters, including at least one uppercase letter, one lowercase letter, one digit, and one special character'}
    assert status_code == 400

def test_no_digit_password():
    password = "@SmartMaya"
    response = validate_password(password)
    result, message, status_code = response
    assert result is False
    assert json.loads(message.get_data(as_text=True)) == {'message': 'Password should contain at least 8 characters, including at least one uppercase letter, one lowercase letter, one digit, and one special character'}
    assert status_code == 400

# Test signup function
def test_signup_valid_credentials():
    # Test case with valid credentials
    email = 'mayakhalide2001@gmail.com'
    power_eye_password = '@MayaEmar2001'
    cloud_password = 'smarthomemaya'

    response, status_code = signup(email, power_eye_password, cloud_password)
    json_response = response.get_json()

    # assert json_response == {'message': 'User created successfully.'}
    # assert status_code == 201

def test_signup_invalid_meross_credentials():
    email = "mayakhalide2001@gmail.com"
    power_eye_password = "Smarthomemaya#1"
    cloud_password = "smarthome"
    # Mock the invalid credentials message
    cloud.verify_credentials = MagicMock(return_value=(False, {'error': 'Invalid username/Password combination'}, 401))

    response, status_code = signup(email, power_eye_password, cloud_password)

    assert status_code == 401
    # Assert that the response matches the expected error response
    expected_response = {'error': 'Invalid username/Password combination'}
    assert response == expected_response
    # ensures that if valid credentials are provided, the test will fail
    success_message = {'message': 'User created successfully.'}
    assert response != success_message

def valid_user_credentials():
    valid_user_credentials = {'email': 'mayakhalide2001@gmail.com', 'password': 'Smarthomemaya#1'}
    response = login(valid_user_credentials['email'], valid_user_credentials['password'])
    assert response.status_code == 200
    assert response.json == {'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTY3OTk5NTIwYzA0NGQxNzUwMGM1ZDUiLCJleHAiOjE3MDQwNDQ1NzF9.jzV-kqAT63koiG-toEtQ1ULUmIiM1lpXw0wwLt3uWWM'}

def test_login_missing_email():
    response, _ = login('', 'Smarthomemaya#1')
    assert response.status_code == 200
    assert response.json == {'error': 'Email is required.'}

def test_login_missing_password():
    response, _ = login('mayakhalide2001@gmail.com', '')
    assert response.status_code == 200
    assert response.json == {'error': 'Password is required.'}

def test_login_invalid_credentials():
    invalid_user_credentials = {'email': 'mayakhalid@gmail.com', 'password': 'Smarthomemaya'}
    response, _ = login(invalid_user_credentials['email'], invalid_user_credentials['password'])
        # print(f"Actual status code: {response.status_code}")
    assert response.status_code == 200
    assert response.json == {'error': 'Invalid email or password.'}

# Test logout function
def test_logout():
    response, status_code = logout()
    assert status_code == 200
    assert response.json == {'message': 'Logged out successfully.'}

# Test get_user_info function
def test_valid_get_user_info():
    user_id = "6552954c710c09f3b476eece"
    user = User(id=user_id, email="mayakhalide2001@gmail.com", username="maya1",current_month_energy=0,
                energy_goal=500, password="Smarthomemaya1#", cloud_password="smarthomemaya" )
    user.save()

    # Call the function being tested
    response, status_code = get_user_info(user_id)
    # Assert the response is as expected
    assert status_code == 200

def test_nonexistent_user():
    user_id = "0002954c710c09f3b476eece"
    response, status_code = get_user_info(user_id)
    assert status_code == 500

def test_deleted_user():
    user_id = "65529056710c09f3b476eecd"
    user = User(
        id=user_id,
        email="mayakhalide2001@gmail.com",
        username="",
        current_month_energy=0,
        energy_goal=-1,
        password="Smarthomemaya1#",
        cloud_password="smarthomemaya",
        is_deleted=True
    )
    user.save()

    # Call the function being tested
    response, status_code = get_user_info(user_id)
    assert status_code == 500

def test_exceptionfor_signup_handling():
    user_id = "6552954c710c09f3b476eece"
    # Simulate an exception by providing an invalid user ID
    invalid_user_id = "65529056710c09f3b476eecd"

    # Call the function being tested
    response, status_code = get_user_info(invalid_user_id)
    assert status_code == 500

# Test case for updating all user information
def test_update_all_user_info():
    user_id = "6552954c710c09f3b476eece"
    meross_password = "smarthomemaya"
    power_eye_password = "Smartmaya1#"
    username = "Mayati"

    response, status_code = update_user_info(user_id, meross_password, power_eye_password, username)
    assert status_code == 200

# Test updating username and PowerEye password
def test_update_username_and_power_eye_passwords():
    user_id = "6552954c710c09f3b476eece"
    power_eye_password = "Smarthome1#"
    username = "Mayoosh"
    response, status_code = update_user_info(user_id, username=username, power_eye_password=power_eye_password)
    assert status_code == 200

# Test updating PowerEye password
def test_update_PowerEye_password():
    user_id = "6552954c710c09f3b476eece"
    power_eye_password = "Smarthomemaya1#"
    response, status_code = update_user_info(user_id, power_eye_password=power_eye_password)
    assert status_code == 200

# Test updating username
def test_update_username():
    user_id = "6552954c710c09f3b476eece"
    username = "maya2001"
    response, status_code = update_user_info(user_id, username=username)
    assert status_code == 200

# Test updating PowerEye password by using invalid pass
def test_invalid_PowerEye_password():
    user_id = "6552954c710c09f3b476eece"
    power_eye_password = "maya"
    response, status_code = update_user_info(user_id, power_eye_password=power_eye_password)
    assert status_code == 200

# -------This function may failed when running test multiple time because the user will be deleted-------
# # Test delete_user function
# def test_valid_delete_user():
#     user_id = "65662ce49238abde429a454c"
#     response, status_code = delete_user(user_id)
#     assert status_code == 200

# # Test case for deleting a non-existing user
# def test_delete_non_existing_user():
#     user_id = "000611595a971ddd4cebf0a1"
#     response, status_code = delete_user(user_id)
#     assert status_code == 500

# Test case when user exists and has a goal
def test_get_goal_user_exists():
    user_id = "6552954c710c09f3b476eece"
    response, status_code = get_goal(user_id)
    assert status_code == 200

# @pytest.mark.parametrize allows one to define multiple sets of arguments at the test function.
@pytest.mark.parametrize("user_id, energy, expected_status, expected_message", [
    # test setting goal to valid value (+ve)
    ("6552954c710c09f3b476eece", 500, 201, "Goal set successfully"),
    # test setting goal to -ve
    ("6552954c710c09f3b476eece", -500, 400, "Energy goal must be a positive value."),
    # test setting goal into invalid goal (not numeric)
    ("6552954c710c09f3b476eece", ".", 400, "Energy goal must be a numeric value."),
    # invalid goal (Energy goal isn't greater than or equal to the total energy cost incurred this month)
    # ("6552954c710c09f3b476eece", 0.0001, 400, "Energy goal must be greater than or equal to the total energy cost incurred this month.")
])
def test_set_goal(user_id, energy, expected_status, expected_message):
    response, status_code = set_goal(user_id, energy)
    assert status_code == expected_status
    assert response.json == {'message': expected_message}

@pytest.mark.parametrize("user_id, expected_status, expected_message", [
    # Test case for deleting goal of an existing user
    ("6552954c710c09f3b476eece", 200, "Goal deleted successfully")
])
def test_delete_goal(user_id, expected_status, expected_message):
    response, status_code = delete_goal(user_id)
    assert status_code == expected_status
    assert response.get_json()["message"] == expected_message

@pytest.mark.parametrize("user_id, file, filename_with_extension, expected_status", [
    # Test case for a valid user and all required inputs
    ("6552954c710c09f3b476eece", "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAIAAAACDbGyAAABYmlDQ1BpY2MAACiRdZC9S8NQFMVPq1LQOogOHRwyiUPU0gp2cWgrFEUwVAWrU5p+CW18JClScRNXKfgfWMFZcLCIVHBxcBBEBxHdnDopuGh43pdU2iLex+X9OJxzuVzAG1AZK/YCKOmWkUzEpLXUuuR7g4eeU6pmsqiiLAr+/bvr89H13k+IWU27dhDZT1yXzi6Xdp4CU3/9XdWfyZoa/d/UQY0ZFuCRiZVtiwneJR4xaCniquC8y8eC0y6fO56VZJz4lljSCmqGuEkspzv0fAeXimWttYPY3p/VV5fFHOpRzGETJhiKUFGBBAXhf/zTjj+OLXJXYFAujwIsykRJEROyxPPQoWESMnEIQeqQuHPrfg+t+8ltbe8VmG1wzi/a2kIDOJ2hk9Xb2ngEGBoAbupMNVRH6qH25nLA+wkwmAKG7yizYebCIXd7fwzoe+H8YwzwHQJ2lfOvI87tGoWfgSv9BxcparzsG/VjAAAAA3NCSVQICAjb4U/gAAAAV0lEQVQImWO4d+fmhvVrREVEeLm4eLm4mL99/Tp1yrTPnz4xQICYiMjf37/evX3Ny8Wlq6XB8v37t5SkpBs3r3/6+oWBgYGRl5uL4T8DAyPDmzdvREVEAFccIMQKUjhqAAAAAElFTkSuQmCC", 
     "unnamed.png", 200),
    # Test case for a valid user but missing image data
    ("6552954c710c09f3b476eece", None, "unnamed.png", 400),
    # Test case for a valid user but missing filename
    ("6552954c710c09f3b476eece", "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAIAAAACDbGyAAABYmlDQ1BpY2MAACiRdZC9S8NQFMVPq1LQOogOHRwyiUPU0gp2cWgrFEUwVAWrU5p+CW18JClScRNXKfgfWMFZcLCIVHBxcBBEBxHdnDopuGh43pdU2iLex+X9OJxzuVzAG1AZK/YCKOmWkUzEpLXUuuR7g4eeU6pmsqiiLAr+/bvr89H13k+IWU27dhDZT1yXzi6Xdp4CU3/9XdWfyZoa/d/UQY0ZFuCRiZVtiwneJR4xaCniquC8y8eC0y6fO56VZJz4lljSCmqGuEkspzv0fAeXimWttYPY3p/VV5fFHOpRzGETJhiKUFGBBAXhf/zTjj+OLXJXYFAujwIsykRJEROyxPPQoWESMnEIQeqQuHPrfg+t+8ltbe8VmG1wzi/a2kIDOJ2hk9Xb2ngEGBoAbupMNVRH6qH25nLA+wkwmAKG7yizYebCIXd7fwzoe+H8YwzwHQJ2lfOvI87tGoWfgSv9BxcparzsG/VjAAAAA3NCSVQICAjb4U/gAAAAV0lEQVQImWO4d+fmhvVrREVEeLm4eLm4mL99/Tp1yrTPnz4xQICYiMjf37/evX3Ny8Wlq6XB8v37t5SkpBs3r3/6+oWBgYGRl5uL4T8DAyPDmzdvREVEAFccIMQKUjhqAAAAAElFTkSuQmCC",
      None, 400)
])
def test_upload_profile_pic(user_id, file, filename_with_extension, expected_status):
    response, status_code = upload_profile_pic(user_id, file, filename_with_extension)
    assert status_code == expected_status

@pytest.mark.parametrize("user_id, file_exists, allowed_extensions, expected_status", [
    # Test case for a valid user with an existing profile picture file
    ("6552954c710c09f3b476eece", True, ['png'], 200),
    # Test case for a valid user with a non-existent profile picture file
    ("6552954c710c09f3b476eece", False, ['png'], 200),   
    # Test case for a valid user with an existing profile picture file but no allowed extensions
    ("6552954c710c09f3b476eece", True, [], 200),  
    # Test case for a valid user with multiple allowed extensions and an existing profile picture file
    ("6552954c710c09f3b476eece", True, ['png', 'jpeg'], 200),
    # Test case for a valid user with multiple allowed extensions but no existing profile picture file
    ("6552954c710c09f3b476eece", False, ['png', 'jpeg'], 200)
])
def test_get_profile_pic(user_id, file_exists, allowed_extensions, expected_status):
    response, status_code = get_profile_pic(user_id)
    assert status_code == expected_status

@pytest.mark.parametrize("user_id, device_id, fcm_token, expected_status", [
    # Test case for an existing user and existing device_id
    ("6552954c710c09f3b476eece", "6570b20848a7178af2b61c55", 
     "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTY3OTk5NTIwYzA0NGQxNzUwMGM1ZDUiLCJleHAiOjE3MDQwNDQ1NzF9.jzV-kqAT63koiG-toEtQ1ULUmIiM1lpXw0wwLt3uWWM", 200),
    # Test case for an existing user and non-existent device_id
    ("6552954c710c09f3b476eece", "5670b20848a7178af2b61c55", 
     "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTY3OTk5NTIwYzA0NGQxNzUwMGM1ZDUiLCJleHAiOjE3MDQwNDQ1NzF9.jzV-kqAT63koiG-toEtQ1ULUmIiM1lpXw0wwLt3uWWM", 200),
])
def test_set_FCM_token(user_id, device_id, fcm_token, expected_status):
    response, status_code = set_FCM_token(user_id, device_id, fcm_token)
    assert status_code == expected_status

