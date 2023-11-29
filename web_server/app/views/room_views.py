"""
Module: room_views

This module defines Flask routes related to user rooms.

Each route corresponds to a specific functionality related to room management,
such as creating a new room, retrieving information about room appliances, switching
the status of a room, adding appliances to a room, getting all user rooms, deleting
an appliance from a room, updating the name of a room, and deleting a room.

Routes:
- POST /create_room: Create a new room.
- GET /get_room_appliances/<room_id>: Get all appliances in a specific room.
- PUT /switch_room/<room_id>: Switch the status of a room.
- PUT /add_appliance_to_room/<room_id>: Add appliances to a room.
- GET /get_all_user_rooms: Get all rooms belonging to the user.
- DELETE /delete_appliance_from_room/<room_id>/<appliance_id>: Delete an appliance from a room.
- PUT /update_room_name/<room_id>: Update the name of a room.
- DELETE /delete_room/<room_id>: Delete a room.

Request and Response Formats:
The request and response formats for each route are documented in the respective route's docstring.
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.room_controller import (
    create_room,
    get_room_appliances,
    switch_room,
    add_appliances_to_room,
    get_all_user_rooms,
    delete_appliance_from_room,
    update_room_name,
    delete_room,
)




# Create a Blueprint to organize routes
room_views = Blueprint('room_views', __name__)

# Define routes using the imported functions
@room_views.route('/create_room', methods=['POST'])
@jwt_required()
def create_room_route():
    """
    Endpoint to create a new room.

    Request Body:
    {
        "name": "room_name",
        "appliance_ids": ["appliance_id_1", "appliance_id_2", ...]
    }

    Returns:
    JSON: Response message.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get('name')
    appliance_ids = data.get('appliance_ids')
    return create_room(user_id, name, appliance_ids)

@room_views.route('/get_room_appliances/<room_id>', methods=['GET'])
@jwt_required()
def get_room_appliances_route(room_id):
    """
    Endpoint to get all appliances in a specific room.

    Returns:
    JSON: List of appliances in the room.
    """
    user_id = get_jwt_identity()
    return get_room_appliances(user_id, room_id)

@room_views.route('/switch_room/<room_id>', methods=['PUT'])
@jwt_required()
def switch_room_route(room_id):
    """
    Endpoint to switch the status of a room (ON/OFF).

    Request Body:
    {
        "new_status": "true" or "false"
    }

    Returns:
    JSON: Response message.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    new_status = data.get('new_status')
    return switch_room(user_id, room_id, new_status)

@room_views.route('/add_appliance_to_room/<room_id>', methods=['PUT'])
@jwt_required()
def add_appliances_to_room_route(room_id):
    """
    Endpoint to add appliances to a room.

    Request Body:
    {
        "appliance_ids": ["appliance_id_1", "appliance_id_2", ...]
    }

    Returns:
    JSON: Response message.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    appliance_ids = data.get('appliance_ids')

    return add_appliances_to_room(user_id, room_id, appliance_ids)


@room_views.route('/get_all_user_rooms', methods=['GET'])
@jwt_required()
def get_all_user_rooms_route():
    """
    Endpoint to get all rooms belonging to the user.

    Returns:
    JSON: List of user's rooms.
    """
    user_id = get_jwt_identity()
    return get_all_user_rooms(user_id)

@room_views.route('/delete_appliance_from_room/<room_id>/<appliance_id>', methods=['DELETE'])
@jwt_required()
def delete_appliance_from_room_route(room_id, appliance_id):
    """
    Endpoint to delete an appliance from a room.

    Returns:
    JSON: Response message.
    """
    user_id = get_jwt_identity()
    return delete_appliance_from_room(user_id, room_id, appliance_id)

@room_views.route('/update_room_name/<room_id>', methods=['PUT'])
@jwt_required()
def update_room_name_route(room_id):
    """
    Endpoint to update the name of a room.

    Request Body:
    {
        "new_name": "new_room_name"
    }

    Returns:
    JSON: Response message.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    new_name = data.get('new_name')
    return update_room_name(user_id, room_id, new_name)

@room_views.route('/delete_room/<room_id>', methods=['DELETE'])
@jwt_required()
def delete_room_route(room_id):
    """
    Endpoint to delete a room.

    Returns:
    JSON: Response message.
    """
    user_id = get_jwt_identity()
    return delete_room(user_id, room_id)
