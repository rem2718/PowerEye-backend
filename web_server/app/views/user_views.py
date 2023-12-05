"""
Module: user_views

This module defines Flask routes related to user operations.

Each route corresponds to a specific functionality related to user management,
such as user registration, login, logout, updating user information, managing energy goals,
uploading and retrieving profile pictures, and setting FCM tokens for push notifications.

Routes:
- POST /signup: User registration.
- POST /login: User login.
- POST /logout: User logout.
- GET /user: Retrieve user information.
- PUT /user: Update user information.
- DELETE /user: Delete the user.
- GET /goal: Retrieve user's energy goal.
- POST /goal: Set user's energy goal.
- DELETE /goal: Delete user's energy goal.
- POST /profile_pic: Upload user's profile picture.
- GET /profile_pic: Retrieve user's profile picture.
- POST /FCM_token: Set FCM token for push notifications.

Request and Response Formats:
The request and response formats for each route are documented in the respective route's docstring.
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.user_controller import (
    signup,
    login,
    logout,
    get_user_info,
    update_user_info,
    delete_user,
    get_goal,
    set_goal,
    delete_goal,
    upload_profile_pic,
    get_profile_pic,
    set_fcm_token,
)


# Create a Blueprint to organize routes
user_views = Blueprint('user_views', __name__)

# Define routes using the imported functions
@user_views.route('/signup', methods=['POST'])
def signup_route():
    """
    Endpoint for user registration.

    Request Body:
    {
        "email": "user@example.com",
        "power_eye_password": "password123",
        "cloud_password": "cloudpass456"
    }

    Returns:
    JSON: Response message.
    """
    data = request.get_json()
    email = data.get('email')
    power_eye_password = data.get('power_eye_password')
    cloud_password = data.get('cloud_password')
    return signup(email, power_eye_password, cloud_password)

@user_views.route('/login', methods=['POST'])
def login_route():
    """
    Endpoint for user login.

    Request Body:
    {
        "email": "user@example.com",
        "password": "password123"
    }

    Returns:
    JSON: Response message.
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    return login(email, password)

@user_views.route('/logout', methods=['POST'])
@jwt_required()
def logout_route():
    """
    Endpoint for user logout. The device id is needed to stop sending notifications when the user is logged out

    Request Body:
    {
        "device_id": "123456789"  # The unique identifier of the device to be logged out.
    }

    Returns:
    JSON: Response message indicating the success or failure of the logout operation.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    device_id=data.get('device_id')
    return logout(user_id,device_id)

@user_views.route('/user', methods=['GET'])
@jwt_required()
def get_user_info_route():
    """
    Endpoint to get user information.

    Returns:
    JSON: User information.
    """
    user_id = get_jwt_identity()
    return get_user_info(user_id)

@user_views.route('/user', methods=['PUT'])
@jwt_required()
def update_user_info_route():
    """
    Endpoint to update user information.

    Request Body:
    {
        "meross_password": "meross_pass",
        "power_eye_password": "new_password",
        "username": "new_username"
    }

    Returns:
    JSON: Response message.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    meross_password = data.get('meross_password', None)
    power_eye_password = data.get('power_eye_password', None)
    username = data.get('username', None)
    return update_user_info(user_id, meross_password, power_eye_password, username)

@user_views.route('/user', methods=['DELETE'])
@jwt_required()
def delete_user_route():
    """
    Endpoint to delete the user.

    Returns:
    JSON: Response message.
    """
    user_id = get_jwt_identity()
    return delete_user(user_id)

@user_views.route('/goal', methods=['GET'])
@jwt_required()
def get_goal_route():
    """
    Endpoint for getting user's energy goal.

    Returns:
    JSON: User's energy goal.
    """
    user_id = get_jwt_identity()
    return get_goal(user_id)

@user_views.route('/goal', methods=['POST'])
@jwt_required()
def set_goal_route():
    """
    Endpoint to set user's energy goal.

    Request Body:
    {
        "energy_goal": 1000
    }

    Returns:
    JSON: Response message.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    energy = data.get('energy_goal')
    return set_goal(user_id,energy)

@user_views.route('/goal', methods=['DELETE'])
@jwt_required()
def delete_goal_route():
    """
    Endpoint to delete user's energy goal.

    Returns:
    JSON: Response message.
    """
    user_id = get_jwt_identity()
    return delete_goal(user_id)


@user_views.route('/profile_pic', methods=["POST"])
@jwt_required()
def upload_profile_pic_route():
    """
    Endpoint to upload user's profile picture.

    Request Body:
    {
        "file": "base64_encoded_image",
        "filename": "profile_pic",
        "extension": "png"
    }

    Returns:
    JSON: Response message.
    """
    user_id = get_jwt_identity()
    file = request.json['file']
    filename = request.json['filename']
    extension = request.json['extension']
    # Concatenate the filename and extension
    filename_with_extension = filename + '.' + extension
    return upload_profile_pic(user_id,file,filename_with_extension)

@user_views.route('/profile_pic', methods=["GET"])
@jwt_required()
def get_profile_pic_route():
    """
    Endpoint to get user's profile picture.

    Returns:
    JSON: User's profile picture.
    """
    user_id = get_jwt_identity()
    return get_profile_pic(user_id)




@user_views.route('/FCM_token', methods=["POST"])
@jwt_required()
def set_fcm_token_route():
    """
    Endpoint for setting the FCM token for push notifications.


    Request Body:
    {
        "device_id": "device_identifier",
        "fcm_token": "user_fcm_token"
    }

    Returns:
    JSON: Response message.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    device_id = data.get('device_id')
    fcm_token = data.get('fcm_token')
    return set_fcm_token(user_id, device_id, fcm_token)
