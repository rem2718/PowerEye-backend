# app\controllers\appliance_controller.py
from flask import jsonify,make_response
from app.models.appliance_model import Appliance
from app.utils.enums import ApplianceType
from app.utils.enums import EType
from app.models.user_model import User
from app.models.room_model import Room
from mongoengine.errors import DoesNotExist
from bson import ObjectId
from app.utils.cloud_interface import cloud
import traceback


# Helper function to map the type of the appliances with (shiftable, phantom, none)
def map_appliance_type_to_e_type(appliance_type):
    appliance_type_to_e_type = {
        ApplianceType.COOLER: EType.NONE,
        ApplianceType.LIGHTING: EType.NONE,
        ApplianceType.HEATER: EType.NONE,
        ApplianceType.COOKER_MAKER: EType.NONE,
        ApplianceType.BLENDER: EType.NONE,
        ApplianceType.ALEXA: EType.NONE,
        ApplianceType.HAIR_DRYER: EType.NONE,
        ApplianceType.CAMERA: EType.NONE,
        ApplianceType.WASHING_MACHINE: EType.SHIFTABLE,
        ApplianceType.IRON: EType.SHIFTABLE,
        ApplianceType.VACUUM_CLEANER: EType.SHIFTABLE,
        ApplianceType.AIR_PURIFIER: EType.SHIFTABLE,
        ApplianceType.GAMES: EType.PHANTOM,
        ApplianceType.DISPLAYER: EType.PHANTOM,
        ApplianceType.AUDIO_OUTPUT: EType.PHANTOM,
        ApplianceType.PRINTER: EType.PHANTOM,
        ApplianceType.CHARGER: EType.PHANTOM,
        ApplianceType.RECEIVER: EType.PHANTOM,
        ApplianceType.SPORTS_MACHINE: EType.PHANTOM
    }
    return appliance_type_to_e_type.get(appliance_type)

# Helper function to validate appliance name
def validate_name(user_id, name, current_appliance_id=None):
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return jsonify({'message': 'User not found.'}), 404

        # Check if name is a string and has 2 or more characters
        if not isinstance(name, str) or len(name) < 2:
            return False, jsonify({'message': 'Name should be a string with 2 or more characters'}), 400

        # Check if the name is unique among active appliances in the user's account
        for appliance in user.appliances:
            # Exclude the current appliance being updated (if provided)
            if current_appliance_id and str(appliance._id) == current_appliance_id:
                continue

            if appliance.name == name:
                # Check if the existing appliance is deleted
                if appliance.is_deleted:
                    # If the appliance is deleted, the name is considered unique
                    continue
                return False, jsonify({'message': 'Name must be unique among all active appliances in your account'}), 400


        # Return True if the name is valid and unique
        return True, None, None

    except DoesNotExist:
        return False, jsonify({'message': 'User not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return False, jsonify({'message': f'Error occurred while validating name: {str(e)}'}), 500

# Helper function to validate plug id
def validate_cloud_id(user_id, cloud_id):
    '''validating the smart plug id (cloud could be Meross or Tuya)'''
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return jsonify({'message': 'User not found.'}), 404

        # Validate cloud_id
        if not cloud_id or not isinstance(cloud_id, str):
            return False, jsonify({'message': 'Invalid cloud_id'}), 400
        
        # Validate if the provided cloud_id belongs to the user's smart plugs
        smartplugs_result = get_smartplugs(user_id)

        # Check if the response indicates an error
        if len(smartplugs_result) < 2 or smartplugs_result[1] != 200:
            return False, jsonify({'message': 'Error retrieving smart plugs'}), 500

        user_smartplugs = smartplugs_result[0].get_json().get("Smart Plugs", [])
        # Extracting the list of ids from user_smartplugs
        smartplug_ids = [smartplug['id'] for smartplug in user_smartplugs]


        if cloud_id not in smartplug_ids:
            return False, jsonify({'message': 'Invalid cloud_id, or the plug is already in use'}), 400


        return True, None, None

    except DoesNotExist:
        return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({'message': f'Error occurred while validating cloud ID: {str(e)}'}), 500


def add_appliance(user_id, name, cloud_id, type):
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return jsonify({'message': 'User not found.'}), 404

        # Validate name
        is_valid_name, error_response, status_code = validate_name(user_id,name)
        if not is_valid_name:
            return error_response, status_code

        # Validate cloud_id
        is_valid_cloud_id, error_response, status_code = validate_cloud_id(user_id, cloud_id)
        if not is_valid_cloud_id:
            return error_response, status_code

        
        # Validate type
        if type not in [t.value for t in ApplianceType]:
            return jsonify({'message': 'Invalid appliance type'}), 400

        e_type = map_appliance_type_to_e_type(type)


        # Generate a unique ID for the appliance

        appliance_id = str(ObjectId())

        appliance = Appliance(
            _id=appliance_id,
            name=name,
            type=type,
            cloud_id=cloud_id,
            e_type=e_type
        )

        user.appliances.append(appliance)
        user.save()

        return jsonify({'message': f'Appliance {name} added successfully', 'appliance_id': appliance_id}), 201

    except DoesNotExist:
        return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({'message': f'Error occurred while adding appliance: {str(e)}'}), 500

def get_appliance_by_id(user_id, appliance_id):
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return jsonify({'message': 'User not found.'}), 404

        # Find the appliance within the user's appliances
        appliance = next((app for app in user.appliances if str(app._id) == appliance_id), None)

        if not appliance or appliance.is_deleted:
            return jsonify({'message': 'Appliance not found'}), 404

        # Convert appliance data to a dictionary
        appliance_data = {
            'id': str(appliance._id),
            'name': appliance.name,
            'type': ApplianceType(appliance['type']).value,
            'cloud_id': appliance.cloud_id,
            'energy': appliance.energy,
            'is_deleted': appliance.is_deleted,
            'connection_status': appliance.connection_status,
            'status': appliance.status,
            'baseline_threshold': appliance.baseline_threshold,
            'e_type': appliance.e_type.value 
        }

        return jsonify(appliance_data), 200

    except DoesNotExist:
        return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({'message': f'Error occurred while retrieving appliance: {str(e)}'}), 500

def get_all_appliances(user_id):
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return jsonify({'message': 'User not found.'}), 404

        # Retrieve the user's appliances
        appliances_data = []

        for appliance in user.appliances:
            if not appliance.is_deleted:
                appliance_data = {
                    'id': str(appliance._id),
                    'name': appliance.name,
                    'type': ApplianceType(appliance['type']).value,
                    # 'cloud_id': appliance.cloud_id,
                    'connection_status': appliance.connection_status,
                    'status': appliance.status,
                }
                appliances_data.append(appliance_data)

        return jsonify({'appliances': appliances_data}), 200

    except DoesNotExist:
        return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({'message': f'Error occurred while retrieving appliances: {str(e)}'}), 500

def delete_appliance(user_id, appliance_id):
    from app.controllers.room_controller import delete_appliance_from_room

    try:
        
        # Get user and appliance
        user = User.objects.get(id=user_id, is_deleted=False)

        appliance = next((app for app in user.appliances if str(app._id) == str(appliance_id) and not app.is_deleted), None)

        if not user or not appliance:
            message = 'User not found.' if not user else 'Appliance not found.'
            return make_response(jsonify({'message': message}), 404)


        # Soft delete the appliance by marking it as deleted
        appliance.is_deleted = True
        user.save()

        # Check if the appliance is associated with any rooms
        rooms_with_appliance = Room.objects(appliances=appliance_id)
        if not rooms_with_appliance:
            return jsonify({'message': 'Appliance deleted, it was not associated with any rooms'}), 200

        # Delete the appliance from each room where it's associated
        for room in rooms_with_appliance:
            delete_appliance_from_room(user_id, str(room.id), appliance_id)

        return jsonify({'message': 'Appliance deleted successfully'}), 200
    except DoesNotExist:
        return make_response(jsonify({'message': 'User or Appliance not found'}), 404)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'message': f'Error occurred while deleting appliance: {str(e)}'}), 500

def update_appliance_name(user_id, appliance_id, new_name):
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return jsonify({'message': 'User not found.'}), 404

        # Find the appliance within the user's appliances
        appliance = next((app for app in user.appliances if str(app._id) == appliance_id), None)

        if not appliance or appliance.is_deleted:
            return jsonify({'message': 'Appliance not found'}), 404


        # Validate name
        is_valid_name, error_response, status_code = validate_name(user_id, new_name, current_appliance_id=appliance_id)
        if not is_valid_name:
            return error_response, status_code

        # Update the name of the appliance
        appliance.name = new_name
        user.save()

        return jsonify({'message': f'Appliance name updated successfully to {new_name}.'}), 200
    except DoesNotExist:
        return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({'message': f'Error occurred while updating appliance: {str(e)}'}), 500

def switch_appliance(user_id, appliance_id, status):
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return jsonify({'message': 'User not found.'}), 404

        # Find the appliance within the user's appliances
        appliance = next((app for app in user.appliances if str(app._id) == appliance_id), None)

        if not appliance or appliance.is_deleted:
            return jsonify({'message': 'Appliance not found'}), 404

        # Retrieve the cloud ID of the appliance
        cloud_id = appliance.cloud_id
        
        
        
        status = bool(status)
        # Check if the status is a valid value 
        if not isinstance(status, bool):
            return jsonify({'error': 'Invalid status value. It should be a boolean (True or False)'}), 400
        
        
        # Switch based on the cloud ID and status
        
        cloud_user = {'id':user.id, 'email': user.email, 'password': user.cloud_password, 'dev1':cloud_id}  # Create user object
        plug_type = user.cloud_type

        
        # Check the result before returning success message
        switched, error_message,status_code=cloud.switch(plug_type, cloud_user, cloud_id, status)
        if not switched:
            return error_message, status_code
        
        return jsonify({'message': 'Appliance status updated successfully'}), 200

    except DoesNotExist:
        return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({'message': f'Error occurred while switching appliance status: {str(e)}'}), 500
    
def get_smartplugs(user_id):
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return jsonify({'message': 'User not found.'}), 404

        # Get a list of all `cloud_id` values from the user's appliances
        plugged_cloud_ids = [app.cloud_id for app in user.appliances if app.cloud_id and not app.is_deleted]

        cloud_user = {'id': user.id, 'email': user.email, 'password': user.cloud_password, 'dev1': 'bf16e0689159efb9c5xibt'}  # Create user object
        plug_type = user.cloud_type

        smart_plugs, error_message, status_code = cloud.get_smartplugs(plug_type, cloud_user)
        if not smart_plugs:
            return jsonify(error_message), status_code

        # Filter the smart plugs based on existing cloud IDs
        filtered_smart_plugs = [plug for plug in smart_plugs if plug.get('id') not in plugged_cloud_ids]

        return jsonify({'Smart Plugs': filtered_smart_plugs}), 200

    except DoesNotExist:
        return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({'message': f'Error occurred while retrieving smart plugs: {str(e)}'}), 500
