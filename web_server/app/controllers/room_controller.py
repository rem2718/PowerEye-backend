# app\controllers\room_controller.py
from flask import jsonify
from app.models.room_model import Room
from app.models.user_model import User
from app.models.appliance_model import Appliance
from mongoengine.errors import DoesNotExist

# Helper function to validate room name
def validate_room_name(user, name):
    try:
        if not user:
            return False, jsonify({'message': 'User not found'}), 404

        # Check if name is a string and has 2 or more characters
        if not isinstance(name, str) or len(name) < 2:
            return False, jsonify({'message': 'The room name should be a string with 2 or more characters'}), 400

        # Check if the name is unique among all rooms in the user's account
        existing_rooms = Room.objects(user_id=user.id, name=name)
        if existing_rooms:
            return False, jsonify({'message': 'The room name must be unique among all rooms in your account'}), 400

        # Return True if the name is valid and unique
        return True, None, None

    except Exception as e:
        return False, jsonify({'message': f'Error occurred while validating name: {str(e)}'}), 500

def create_room(user_id, name, appliance_ids):
    try:
        # Check if the user exists
        user = User.objects.get(id=user_id)
        if not user:
            return jsonify({'error': 'User not found.'}), 404

        # Check if there are appliances provided
        if not appliance_ids:
            return jsonify({'error': 'No appliances provided for the room.'}), 400

        # Validate room name
        is_valid_name, error_response, status_code = validate_room_name(user,name)
        if not is_valid_name:
            return error_response, status_code

        for aid in appliance_ids:
            appliance = next((app for app in user.appliances if str(app._id) == aid), None)
            if not appliance:
                return jsonify({'error': f'Appliance with ID {aid} not found.'}), 404


        # Create the room
        room = Room(name=name, appliances=appliance_ids, user_id=user_id)
        room.save()

        return jsonify({'message': f'Room {name} created successfully.'}), 201

    except DoesNotExist:
        return jsonify({'message': 'User not found'}), 404
    
    except Exception as e:
        return jsonify({'message': f'Error occurred while creating room: {str(e)}'}), 500

def get_room_appliances(user_id, room_id):
    try:
        # Find the user by ID
        user = User.objects.get(id=user_id)

        if not user:
            return jsonify({'message': 'User not found.'}), 404

        # Find the room
        room = Room.objects(id=room_id, user_id=user_id).first()
        if not room:
            return jsonify({'error': 'Room not found or does not belong to the user'}), 404
        
        # Check if the user has any appliances
        if not user.appliances:
            return jsonify({'message': 'User has no appliances.'}), 200


        # Retrieve appliances for the specified room
        room_appliances = []
        for appliance_id in room.appliances:
            appliance = next((app for app in user.appliances if app['_id'] == appliance_id), None)
            if appliance:
                room_appliances.append({
                    'name': appliance['name'],
                    'type': appliance['type'].value,
                    'cloud_id': appliance['cloud_id'],
                    'energy': appliance['energy'],
                    'is_deleted': appliance['is_deleted'],
                    'connection_status': appliance['connection_status'],
                    'status': appliance['status'],
                    'baseline_threshold': appliance['baseline_threshold'],
                    'e_type': appliance['e_type'].value
                })
                
        return jsonify({'appliances': room_appliances}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# def switch_room(user_id, room_id, status):
#     try:
#         # Find the room by its ID and user ID
#         room = Room.objects(user_id=user_id, id=room_id).first()

#         if not room:
#             return jsonify({'message': 'Room not found'}), 404

#         for appliance_id in room.appliances:
#             appliance = Appliance.objects.get(id=appliance_id)

#             if appliance:
#                 switch_appliance_status(appliance.id, status)
#             else:
#                 return jsonify({'message': f'Appliance with ID {appliance_id} not found.'}), 404

#         return jsonify({'message': 'Room appliances status updated successfully'}), 200

#     except DoesNotExist:
#         return jsonify({'message': 'Room not found'}), 404

#     except Exception as e:
#         return jsonify({'message': f'Error occurred while switching room appliances status: {str(e)}'}), 500

def add_appliance_to_room(user_id, room_id, appliance_id):
    try:
        # Find and validate the user by ID
        user = User.objects.get(id=user_id)
        if not user:
            return jsonify({'message': 'User not found.'}), 404

        # Find and validate the room
        room = Room.objects(id=room_id, user_id=user_id).first()
        if not room:
            return jsonify({'error': 'Room not found or does not belong to the user'}), 404

        # Find and validate if the user has that appliance
        appliance = next((app for app in user.appliances if str(app['_id']) == appliance_id), None)
        if not appliance:
            return jsonify({'error': 'Appliance not found for the user'}), 404

        # Find and validate if the appliance.is_deleted = False
        if appliance['is_deleted']:
            return jsonify({'error': 'Appliance is marked as deleted'}), 400

        # Add the appliance id to the room
        if appliance_id not in room.appliances:
            room.update(push__appliances=appliance_id)

        return jsonify({'message': 'Appliance added to room successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_all_user_rooms(user_id):
    try:
        # Find and validate the user by ID
        user = User.objects.get(id=user_id)
        if not user:
            return jsonify({'message': 'User not found.'}), 404

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
