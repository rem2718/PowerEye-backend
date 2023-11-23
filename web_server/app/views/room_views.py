from flask import Blueprint, request, jsonify
from app.controllers.room_controller import *
from flask_jwt_extended import jwt_required, get_jwt_identity

# Create a Blueprint to organize  routes
room_views = Blueprint('room_views', __name__)

# Define routes using the imported functions
@room_views.route('/create_room', methods=['POST'])
@jwt_required()
def create_room_route():
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data['name']
    appliance_ids = data['appliance_ids']
    return create_room(user_id, name, appliance_ids)

@room_views.route('/get_room_appliances/<room_id>', methods=['GET'])
@jwt_required()
def get_room_appliances_route(room_id):
    user_id = get_jwt_identity()
    return get_room_appliances(user_id, room_id)

@room_views.route('/switch_room/<room_id>', methods=['PUT'])
@jwt_required()
def switch_room_route(room_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    new_status = data['new_status']
    return switch_room(user_id, room_id, new_status)

@room_views.route('/add_appliance_to_room/<room_id>', methods=['PUT'])
@jwt_required()
def add_appliances_to_room_route(room_id):
    user_id = get_jwt_identity()
    appliance_ids = request.json.get('appliance_ids', [])

    return add_appliances_to_room(user_id, room_id, appliance_ids)

@room_views.route('/get_all_user_rooms', methods=['GET'])
@jwt_required()
def get_all_user_rooms_route():
    user_id = get_jwt_identity()
    return get_all_user_rooms(user_id)

@room_views.route('/delete_appliance_from_room/<room_id>/<appliance_id>', methods=['DELETE'])
@jwt_required()
def delete_appliance_from_room_route(room_id, appliance_id):
    user_id = get_jwt_identity()
    return delete_appliance_from_room(user_id, room_id, appliance_id)

@room_views.route('/update_room_name/<room_id>', methods=['PUT'])
@jwt_required()
def update_room_name_route(room_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    new_name = data['new_name']
    return update_room_name(user_id, room_id, new_name)

@room_views.route('/delete_room/<room_id>', methods=['DELETE'])
@jwt_required()
def delete_room_route(room_id):
    user_id = get_jwt_identity()
    return delete_room(user_id, room_id)