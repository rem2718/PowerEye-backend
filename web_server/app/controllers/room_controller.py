# app\controllers\goal_controller.py
from flask import jsonify
from app.models.room_model import Room
from app.models.appliance_model import Appliance


def get_room_appliances(room_id):
    # Implementation details for retrieving a list of appliances in a room
    room = Room.objects.get(id=room_id)
    appliances = room.appliances
    appliance_list = [{'id': str(appliance.id), 'name': appliance.name, 'type': appliance.type} for appliance in appliances]
    return {'appliances': appliance_list}


def create_room(name, appliance_ids):
    # Implementation details for creating a room
    room = Room(name=name)
    room.save()

    for appliance_id in appliance_ids:
        appliance = Appliance.objects.get(id=appliance_id)
        room.appliances.append(appliance)
    
    room.save()

    return {'message': 'Room created successfully'}

# need separation to on/off
def switch_room(room_id, status):
    # Implementation details for switching a room's status
    room = Room.objects.get(id=room_id)
    room.status = status
    room.save()

    return {'message': 'Room status updated successfully'}

def add_appliance_to_room(room_id, appliance_id):
    # Implementation details for adding an appliance to a room
    room = Room.objects.get(id=room_id)
    appliance = Appliance.objects.get(id=appliance_id)

    if appliance not in room.appliances:
        room.appliances.append(appliance)
        room.save()
        return {'message': 'Appliance added to room successfully'}
    else:
        return {'error': 'Appliance is already in the room'}

def delete_room_appliance(room_id, appliance_id):
    # Implementation details for deleting an appliance from a room
    room = Room.objects.get(id=room_id)
    appliance = Appliance.objects.get(id=appliance_id)

    if appliance in room.appliances:
        room.appliances.remove(appliance)
        room.save()
        return {'message': 'Appliance removed from room successfully'}
    else:
        return {'error': 'Appliance is not in the room'}
