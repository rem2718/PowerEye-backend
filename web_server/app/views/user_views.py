# app\views\user_views.py
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.user_controller import *


# Create a Blueprint to organize routes
user_views = Blueprint('user_views', __name__)

# Define routes using the imported functions
@user_views.route('/signup', methods=['POST'])
def signup_route():
    data = request.get_json()
    email = data.get('email')
    power_eye_password = data.get('power_eye_password')
    cloud_password = data.get('cloud_password')
    return signup(email, power_eye_password, cloud_password)

@user_views.route('/login', methods=['POST'])
def login_route():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    return login(email, password)

@user_views.route('/logout', methods=['POST'])
@jwt_required()
def logout_route():
    return logout()

@user_views.route('/user', methods=['GET'])
@jwt_required()
def get_user_info_route():
    user_id = get_jwt_identity()
    return get_user_info(user_id)

@user_views.route('/user', methods=['PUT'])
@jwt_required()
def update_user_info_route():
    user_id = get_jwt_identity()
    data = request.get_json()
    meross_password = data.get('meross_password')
    power_eye_password = data.get('power_eye_password')
    username = data.get('username')
    return update_user_info(user_id, meross_password, power_eye_password, username)

@user_views.route('/user', methods=['DELETE'])
@jwt_required()
def delete_user_route():
    user_id = get_jwt_identity()
    return delete_user(user_id)

@user_views.route('/goal', methods=['GET'])
@jwt_required()
def get_goal_route():
    user_id = get_jwt_identity()
    return get_goal(user_id)

@user_views.route('/goal', methods=['POST'])
@jwt_required()
def set_goal_route():
    user_id = get_jwt_identity()
    data = request.get_json()
    energy = data.get('energy_goal')
    return set_goal(user_id,energy)

@user_views.route('/goal', methods=['DELETE'])
@jwt_required()
def delete_goal_route():
    user_id = get_jwt_identity()
    return delete_goal(user_id)


@user_views.route('/profile_pic', methods=["POST"])
@jwt_required()
def upload_profile_pic_route():
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
    user_id = get_jwt_identity()
    return get_profile_pic(user_id)



@user_views.route('/FCM_token', methods=["POST"])
@jwt_required()
def set_FCM_token_route():
    user_id = get_jwt_identity()
    data = request.get_json()
    device_id = data.get('device_id')
    fcm_token = data.get('fcm_token')
    return set_FCM_token(user_id, device_id, fcm_token)