# app\controllers\appliance_controller.py
from flask import jsonify
from app.models.appliance_model import Appliance,ApplianceType, EType
from app.models.user_model import User
from app.models.power_model import Power
from app.controllers.room_controller import delete_appliance_from_room
# from app.utils.cloud_interface import get_smartplugs, switch

# Helper function to map the type of the appliances with (shiftable, phantom, none)
def map_appliance_type_to_e_type(appliance_type):
    appliance_type_to_e_type = {
        ApplianceType.COOLER: EType.NONE,
        ApplianceType.LIGHTING: EType.NONE,
        ApplianceType.HEATER: EType.NONE,
        ApplianceType.COOKER_MAKER: EType.NONE,
        ApplianceType.MIXER: EType.NONE,
        ApplianceType.CLOCK_ALEXA: EType.NONE,
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
        ApplianceType.SEWING_MACHINE: EType.PHANTOM,
        ApplianceType.SPORTS_MACHINE: EType.PHANTOM,
    }
    return appliance_type_to_e_type.get(appliance_type)

# Helper function to validate appliance name
def validate_name(user, name):
    try:
        if not user:
            return False, jsonify({'message': 'User not found'}), 404

        # Check if name is a string and has 2 or more characters
        if not isinstance(name, str) or len(name) < 2:
            return False, jsonify({'message': 'Name should be a string with 2 or more characters'}), 400

        # Check if the name is unique among all appliances in the user's account
        for appliance in user.appliances:
            if appliance.name == name:
                return False, jsonify({'message': 'Name must be unique among all appliances in your account'}), 400

        return True, None, None

    except DoesNotExist:
        return False, jsonify({'message': 'User not found'}), 404

    except Exception as e:
        return False, jsonify({'message': f'Error occurred while validating name: {str(e)}'}), 500

def validate_cloud_id(user, cloud_id):
    '''validating the smart plug id (cloud could be Meross or Tuya)'''
    try:
        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Validate cloud_id 
        if not cloud_id or not isinstance(cloud_id, str):
            return jsonify({'message': 'Invalid cloud_id'}), 400

        # Validate if the provided cloud_id belongs to the user's smart plugs
        user_cloud_ids = get_smartplugs(user)
        if cloud_id not in user_cloud_ids:
            return jsonify({'message': 'Invalid cloud_id'}), 400

        # Validate if the smart plug is not already in use
        for appliance in user.appliances:
            if appliance.cloud_id == cloud_id:
                return jsonify({'message': 'Smart plug is already in use'}), 400

        return None, None  # No validation errors

    except DoesNotExist:
        return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'message': f'Error occurred while validating cloud ID: {str(e)}'}), 500

def add_appliance(user_id, name, cloud_id, type):
    try:
        # Retrieve the user by ID
        user = User.objects.get(id=user_id)

        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Validate name
        is_valid_name, error_response, status_code = validate_name(name, user)
        if not is_valid_name:
            return error_response, status_code

        # Validate cloud_id using the new function
        validation_result, error_response = validate_cloud_id(user, cloud_id)
        if validation_result is not None:
            return error_response

        # Validate type
        if type not in [t.value for t in ApplianceType]:
            return jsonify({'message': 'Invalid appliance type'}), 400

        e_type = map_appliance_type_to_e_type(type)

        appliance = Appliance(
            name=name,
            type=type,
            cloud_id=cloud_id,
            e_type=e_type
        )

        user.appliances.append(appliance)
        user.save()

        return jsonify({'message': 'Appliance added successfully'}), 201

    except DoesNotExist:
        return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'message': f'Error occurred while adding appliance: {str(e)}'}), 500

def get_appliances(user_id):
    try:
        # Retrieve the user by ID
        user = User.objects.get(id=user_id)

        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Retrieve the user's appliances
        appliances = user.appliances

        # Convert appliances to a list of dictionaries
        appliance_data = [appliance.to_dict() for appliance in appliances]

        return jsonify({'appliances': appliance_data}), 200

    except DoesNotExist:
        return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'message': f'Error occurred while retrieving appliances: {str(e)}'}), 500

def delete_appliance(user_id, appliance_id):
    try:
        # Get the user by ID
        user = User.objects.get(id=user_id)

        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Find the appliance within the user's appliances
        appliance = next((app for app in user.appliances if str(app.id) == appliance_id), None)

        if not appliance:
            return jsonify({'message': 'Appliance not found'}), 404

        # Soft delete the appliance by marking it as deleted
        appliance.is_deleted = True
        user.save()
        # # delete_appliance_from_room
        # delete_appliance_from_room(user_id, room_id, appliance_id)

        return jsonify({'message': 'Appliance deleted successfully'}), 200

    except Exception as e:
        return jsonify({'message': f'Error occurred while deleting appliance: {str(e)}'}), 500

def update_appliance(user_id, appliance_id, name):
    try:
        # Get the user by ID
        user = User.objects.get(id=user_id)

        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Find the appliance within the user's appliances
        appliance = next((app for app in user.appliances if str(app.id) == appliance_id), None)

        if not appliance:
            return jsonify({'message': 'Appliance not found'}), 404

        # Validate name
        is_valid_name, error_response, status_code = validate_name(name, user)
        if not is_valid_name:
            return error_response, status_code

        # Update the name of the appliance
        appliance.name = name
        user.save()

        return jsonify({'message': 'Appliance updated successfully'}), 200

    except Exception as e:
        return jsonify({'message': f'Error occurred while updating appliance: {str(e)}'}), 500

# def switch_appliance(user_id, appliance_id, status):
#     try:
#         # Get the user by ID
#         user = User.objects.get(id=user_id)

#         if not user:
#             return jsonify({'message': 'User not found'}), 404

#         # Find the appliance within the user's appliances
#         appliance = next((app for app in user.appliances if str(app.id) == appliance_id), None)

#         if not appliance:
#             return jsonify({'message': 'Appliance not found'}), 404

#         # Retrieve the cloud ID of the appliance
#         cloud_id = appliance.cloud_id

#         # Switch based on the cloud ID and status
#         switch(cloud_id, status)

#         # Update the status of the appliance
#         appliance.status = status
#         user.save()

#         return jsonify({'message': 'Appliance status updated successfully'}), 200

#     except Exception as e:
#         return jsonify({'message': f'Error occurred while switching appliance status: {str(e)}'}), 500

def get_most_recent_reading(user_id, appliance_id):
    try:
        # Get the user by ID
        user = User.objects.get(id=user_id)

        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Find the appliance within the user's appliances
        appliance = next((app for app in user.appliances if str(app.id) == appliance_id), None)

        if not appliance:
            return jsonify({'message': 'Appliance not found'}), 404

        # Get the most recent power reading for the specified appliance
        power_reading = Power.objects(appliances_powers__has_key=str(appliance.id)).order_by('-timestamp').first()

        if power_reading:
            power_value = power_reading.appliances_powers.get(str(appliance.id))
            return jsonify({'power': power_value}), 200
        else:
            return jsonify({'error': 'No power data available for this appliance.'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
