# app\controllers\room_controller.py
from flask import jsonify
from app.models.room_model import Room
from app.models.appliance_model import Appliance
from app.controllers.appliance_controller import switch_appliance_status

# Helper function to validate room name
def validate_room_name(name, user):
    try:
        # Check if name is a string and has 2 or more characters
        if not isinstance(name, str) or len(name) < 2:
            return False, jsonify({'message': 'Name should be a string with 2 or more characters'}), 400

        # Check if the name is unique among all rooms in the user's account
        for room in user.rooms:
            if room.name == name:
                return False, jsonify({'message': 'Name must be unique among all rooms in your account'}), 400

        # Return True if the name is valid and unique
        return True, None, None

    except Exception as e:
        return False, jsonify({'error': str(e)}), 500

def get_room_appliances(user_id, room_id):
    try:
        # Find the room by its ID and user ID
        room = Room.objects(user_id=user_id, id=room_id).first()

        if room:
            if not room.appliances:
                return jsonify({'message': 'No appliances in the room.'}), 200

            # Fetch non-deleted appliances based on their IDs in the room
            appliances = Appliance.objects(id__in=room.appliances, is_deleted=False)

            if not appliances:
                return jsonify({'message': 'No active appliances in the room.'}), 200

            appliance_list = []
            for appliance in appliances:
                appliance_data = {
                    'id': str(appliance.id),
                    'name': appliance.name,
                    'type': appliance.type,
                    'cloud_id': appliance.cloud_id,
                    'energy': appliance.energy,
                    'is_deleted': appliance.is_deleted,
                    'connection_status': appliance.connection_status,
                    'status': appliance.status,
                    'baseline_threshold': appliance.baseline_threshold,
                    'e_type': appliance.e_type
                }
                # Add the appliance data to the list
                appliance_list.append(appliance_data)
                
            # Return the list of appliances
            return jsonify({'appliances': appliance_list}), 200
        else:
            return jsonify({'error': 'Room not found.'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def create_room(user_id, name, appliance_ids):
    try:
        # Check if there are appliances provided
        if not appliance_ids:
            return jsonify({'error': 'No appliances provided for the room.'}), 400

        # Validate room name
        if not is_valid_room_name(name):
            return jsonify({'error': 'Room name must consist of 2 or more characters.'}), 400

        # Check if all provided appliance IDs are valid
        for appliance_id in appliance_ids:
            if not Appliance.objects(id=appliance_id):
                return jsonify({'error': f'Appliance with ID {appliance_id} not found.'}), 404

        # Create the room
        room = Room(name=name, appliances=appliance_ids, user_id=user_id)
        room.save()

        return jsonify({'message': f'Room {name} created successfully.'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def switch_room(user_id, room_id, status):
    try:
        # Find the room by its ID and user ID
        room = Room.objects(user_id=user_id, id=room_id).first()

        if not room:
            return jsonify({'message': 'Room not found'}), 404

        for appliance_id in room.appliances:
            appliance = Appliance.objects.get(id=appliance_id)

            if appliance:
                switch_appliance_status(appliance.id, status)
            else:
                return jsonify({'message': f'Appliance with ID {appliance_id} not found.'}), 404

        return jsonify({'message': 'Room appliances status updated successfully'}), 200

    except DoesNotExist:
        return jsonify({'message': 'Room not found'}), 404

    except Exception as e:
        return jsonify({'message': f'Error occurred while switching room appliances status: {str(e)}'}), 500

def add_appliance_to_room(user_id, room_id, appliance_id):
    try:
        # Find the room by its ID and user ID
        room = Room.objects(user_id=user_id, id=room_id).first()

        if not room:
            return jsonify({'message': 'Room not found'}), 404

        # Check if the provided appliance ID is valid
        appliance = Appliance.objects.get(id=appliance_id)

        if not appliance:
            return jsonify({'message': f'Appliance with ID {appliance_id} not found.'}), 404

        # Add the appliance to the room
        if appliance.id not in room.appliances:
            room.appliances.append(appliance.id)
            room.save()

        return jsonify({'message': f'Appliance added to room {room.name} successfully.'}), 200

    except DoesNotExist:
        return jsonify({'message': 'Room or appliance not found'}), 404

    except Exception as e:
        return jsonify({'message': f'Error occurred while adding appliance to room: {str(e)}'}), 500

def get_user_rooms(user_id):
    try:
        # Find rooms by user ID
        rooms = Room.objects(user_id=user_id)

        if not rooms:
            return jsonify({'message': 'No rooms found for this user.'}), 404

        room_list = []
        for room in rooms:
            room_data = {
                'id': str(room.id),
                'name': room.name,
                'appliances': room.appliances
            }
            room_list.append(room_data)

        return jsonify({'rooms': room_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def delete_appliance_from_room(user_id, room_id, appliance_id):
    try:
        # Find the room by its ID and user ID
        room = Room.objects(user_id=user_id, id=room_id).first()

        if not room:
            return jsonify({'message': 'Room not found.'}), 404

        if appliance_id in room.appliances:
            room.appliances.remove(appliance_id)
            room.save()

            return jsonify({'message': 'Appliance removed from room successfully.'}), 200
        else:
            return jsonify({'message': 'Appliance not found in the room.'}), 404

    except DoesNotExist:
        return jsonify({'message': 'Room not found.'}), 404

    except Exception as e:
        return jsonify({'message': f'Error occurred while removing appliance from room: {str(e)}'}), 500

def update_room_name(user_id, room_id, new_name):
    try:
        # Find the room by its ID and user ID
        room = Room.objects(user_id=user_id, id=room_id).first()

        if not room:
            return jsonify({'error': 'Room not found.'}), 404

        # Validate the new room name
        valid, response, status_code = validate_room_name(new_name, current_user)
        if not valid:
            return response, status_code

        room.name = new_name
        room.save()

        return jsonify({'message': f'Room name updated successfully to {new_name}.'}), 200

    except DoesNotExist:
        return jsonify({'error': 'Room not found.'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def delete_room(user_id, room_id):
    try:
        # Find the room by its ID and user ID
        room = Room.objects(user_id=user_id, id=room_id).first()

        if not room:
            return jsonify({'message': 'Room not found'}), 404

        room.delete()

        return jsonify({'message': 'Room deleted successfully'}), 200

    except DoesNotExist:
        return jsonify({'message': 'Room not found'}), 404

    except Exception as e:
        return jsonify({'message': f'Error occurred while deleting room: {str(e)}'}), 500
