# app\controllers\appliance_controller.py
from flask import jsonify
from app.models.user_model import User
from app.models.power_model import Power


# function to get the most recent power reading for a specific appliance
def get_most_recent_reading(user_id, appliance_id):
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return jsonify({'message': 'User not found.'}), 404
        
        # Check if the specified appliance exists and is not deleted
        appliance = next((app for app in user.appliances if str(app._id) == appliance_id and not app.is_deleted), None)

        if not appliance:
            return jsonify({'message': 'Appliance not found or deleted.'}), 404
        
        # Get the most recent power reading for the specified user
        power_reading = Power.objects(user=user).order_by('-timestamp').first()

        # Check if the power_reading exists and has the specified appliance_id as a field
        if power_reading and hasattr(power_reading, appliance_id):
            # Retrieve the power value using getattr
            power_value = getattr(power_reading, appliance_id)
            return jsonify({'power': power_value}), 200  # Return the power value
        else:
            return jsonify({'error': 'No power data available for this appliance.'}), 404  # Return an error message

    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Handle exceptions and return an error message if needed