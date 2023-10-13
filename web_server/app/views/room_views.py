from app import app
from flask import request
from app.controllers.room_controller import create_room, switch_room, add_appliance_to_room, delete_room_appliance, get_rooms, get_room_appliances


@app.route('/room', methods=['POST'])
def create_room_route():
    name = request.json.get('name')
    appliance_ids = request.json.get('appliance_ids')
    return create_room(name, appliance_ids)

@app.route('/room/<int:id>', methods=['PUT'])
def switch_room_route(id):
    status = request.json.get('status')
    return switch_room(id, status)

@app.route('/room/<int:room_id>/appliance/<int:appliance_id>', methods=['PUT'])
def add_appliance_to_room_route(room_id, appliance_id):
    return add_appliance_to_room(room_id, appliance_id)

@app.route('/room/<int:room_id>/appliance/<int:appliance_id>', methods=['DELETE'])
def delete_room_appliance_route(room_id, appliance_id):
    return delete_room_appliance(room_id, appliance_id)

@app.route('/rooms', methods=['GET'])
def get_rooms_route():
    return get_rooms()

@app.route('/room/<int:room_id>/appliances', methods=['GET'])
def get_room_appliances_route(room_id):
    return get_room_appliances(room_id)
