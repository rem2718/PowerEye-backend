from flask import Blueprint, request, jsonify
from app.controllers.room_controller import *

# Create a Blueprint to organize your routes
room_views = Blueprint('room_views', __name__)

# Define routes using the imported functions
@room_views.route('/create_room', methods=['POST'])
def create_room_route():
    data = request.get_json()
    user_id = data['user_id']
    name = data['name']
    appliance_ids = data['appliance_ids']
    return create_room(user_id, name, appliance_ids)

@room_views.route('/get_room_appliances/<user_id>/<room_id>', methods=['GET'])
def get_room_appliances_route(user_id, room_id):
    return get_room_appliances(user_id, room_id)

@room_views.route('/switch_room/<user_id>/<room_id>', methods=['PUT'])
def switch_room_route(user_id, room_id):
    data = request.get_json()
    new_status = data['new_status']
    return switch_room(user_id, room_id, new_status)

@room_views.route('/add_appliance_to_room/<user_id>/<room_id>/<appliance_id>', methods=['POST'])
def add_appliance_to_room_route(user_id, room_id, appliance_id):
    return add_appliance_to_room(user_id, room_id, appliance_id)

@room_views.route('/get_all_user_rooms/<user_id>', methods=['GET'])
def get_all_user_rooms_route(user_id):
    return get_all_user_rooms(user_id)

@room_views.route('/delete_appliance_from_room/<user_id>/<room_id>/<appliance_id>', methods=['DELETE'])
def delete_appliance_from_room_route(user_id, room_id, appliance_id):
    return delete_appliance_from_room(user_id, room_id, appliance_id)

@room_views.route('/update_room_name/<user_id>/<room_id>', methods=['PUT'])
def update_room_name_route(user_id, room_id):
    data = request.get_json()
    new_name = data['new_name']
    return update_room_name(user_id, room_id, new_name)

@room_views.route('/delete_room/<user_id>/<room_id>', methods=['DELETE'])
def delete_room_route(user_id, room_id):
    return delete_room(user_id, room_id)
