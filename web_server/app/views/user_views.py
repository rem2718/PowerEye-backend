# app\views\user_views.py
from flask import Blueprint, request, jsonify
from app.controllers.user_controller import *




# Create a Blueprint to organize your routes
user_views = Blueprint('user_views', __name__)

# Define routes using the imported functions

@user_views.route('/signup', methods=['POST'])
def signup_route():
    data = request.get_json()
    email = data['email']
    power_eye_password = data['power_eye_password']
    meross_password = data['meross_password']
    return signup(email, power_eye_password, meross_password)

@user_views.route('/login', methods=['POST'])
def login_route():
    data = request.get_json()
    email = data['email']
    password = data['password']
    return login(email, password)

@user_views.route('/logout', methods=['POST'])
def logout_route():
    return logout()

@user_views.route('/user', methods=['GET'])
@login_required
def get_user_info_route():
    user_id = data['user_id']
    return get_user_info(user_id)

@user_views.route('/user/<user_id>', methods=['PUT'])
@login_required
def update_user_info_route(user_id):
    data = request.get_json()
    meross_password = data.get('meross_password')
    power_eye_password = data.get('power_eye_password')
    username = data.get('username')
    profile_picture = data.get('profile_picture')
    return update_user_info(user_id, meross_password, power_eye_password, username, profile_picture)

@user_views.route('/user/<user_id>', methods=['DELETE'])
@login_required
def delete_user_route(user_id):
    return delete_user(user_id)

@user_views.route('/goal', methods=['GET'])
@login_required
def get_goal_route():
    return get_goal()

@user_views.route('/goal', methods=['POST'])
@login_required
def set_goal_route():
    data = request.get_json()
    energy = data['energy']
    return set_goal(energy)

@user_views.route('/goal', methods=['DELETE'])
@login_required
def delete_goal_route():
    return delete_goal()

@user_views.route('/rooms', methods=['GET'])
@login_required
def get_rooms_route():
    return jsonify(get_rooms())
