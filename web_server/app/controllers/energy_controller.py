# app\controllers\energy_controller.py
from flask import Flask, jsonify
from app.models.energy_model import Energy 
from app.models.room_model import Room
from app.models.user_model import User
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from flask import jsonify
import traceback


def get_energy(user_id, interval, time_since_current, room_id=None, appliance_id=None):
    try:
        # Calculate the start and end dates based on the interval
        end_date = datetime(2023, 10, 28).date()

        if interval == 'daily':
            start_date = end_date - timedelta(days = time_since_current)
        elif interval == 'weekly':
            start_date = end_date - timedelta(days = 7 * time_since_current)
        elif interval == 'monthly':
            start_date = end_date - relativedelta(months = time_since_current)
        elif interval == 'yearly':
            start_date = end_date - relativedelta(years = time_since_current)
        else:
            return jsonify({'error': 'Invalid interval'})

        if room_id is not None:
            # Calculate room energy consumption
            return calculate_room_energy_consumption(user_id, room_id, start_date, end_date)
        
        elif appliance_id is not None:
            # Calculate appliance energy consumption
            return calculate_appliance_energy_consumption(user_id, appliance_id, start_date, end_date)
        
        else:
            # Calculate total user energy consumption
            return calculate_user_energy_consumption(user_id, start_date, end_date)

    except Exception as e:
        return jsonify({'error': f"An error occurred while getting energy consumption: {str(e)}"})

def calculate_appliance_energy_consumption(user_id, appliance_id, start_date, end_date):
    try:
        # Validate start_date and end_date
        if not isinstance(start_date, (datetime, date)):
            return jsonify({'message': 'Invalid start_date format.'}), 400

        if not isinstance(end_date, (datetime, date)):
            return jsonify({'message': 'Invalid end_date format.'}), 400

        # Check if start_date is before or equal to end_date
        if start_date > end_date:
            return jsonify({'message': 'start_date must be before or equal to end_date.'}), 400

        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return jsonify({'message': 'User not found.'}), 404

        # Find the appliance within the user's appliances
        appliance = next((app for app in user.appliances if str(app._id) == appliance_id), None)
        if not appliance:
            return jsonify({'message': 'Appliance not found'}), 404

        print(f"end date: {end_date}")
        print(f"start date: {start_date}")

        # Filter energy documents by user ID and date range
        energy_documents = Energy.objects(user=user_id, date__gte=start_date, date__lte=end_date)
        if not energy_documents:
            return {'message': 'No energy documents found for this user in the specified date range.'}, 404
        
        Energy_values = []

        for energy_doc in energy_documents:
            # Check if the appliance_id exists in energy_readings
            if appliance_id in energy_doc:
                # Retrieve the power value using getattr and take absolute value
                Energy_value = abs(getattr(energy_doc, appliance_id))
                Energy_values.append(Energy_value)
                
        # Calculate the total energy consumption
        total_energy_consumption = sum(Energy_values)
        
        # Return the total energy consumption as JSON
        return jsonify({'total_energy_consumption': total_energy_consumption})
    except Exception as e:
        return jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"})

def calculate_room_energy_consumption(user_id, room_id, start_date, end_date):
    try:
        # Validate start_date and end_date
        if not isinstance(start_date, (datetime, date)):
            return jsonify({'message': 'Invalid start_date format.'}), 400

        if not isinstance(end_date, (datetime, date)):
            return jsonify({'message': 'Invalid end_date format.'}), 400

        # Check if start_date is before or equal to end_date
        if start_date > end_date:
            return jsonify({'message': 'start_date must be before or equal to end_date.'}), 400
        
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return jsonify({'message': 'User not found.'}), 404
        
        # Find the room with the specified room_id and user_id
        room = Room.objects(id=room_id, user_id=user_id).first()
        if not room:
            return jsonify({'message': 'Room not found'}), 404

        print(f"end date: {end_date}")
        print(f"start date: {start_date}")

        # Get the list of appliances in the room
        appliances_in_room = room.appliances

        
        # Filter energy documents by user ID and date range
        energy_documents = Energy.objects(user=user_id, date__gte=start_date, date__lte=end_date)
        if not energy_documents:
            return {'message': 'No energy documents found for this user in the specified date range.'}, 404
        
        
        Energy_values = []
        for energy_doc in energy_documents:
            # Iterate over the appliances in the room
            for appliance_id in appliances_in_room:
                # Check if the appliance_id exists in energy_readings
                if str(appliance_id) in energy_doc:
                    # Retrieve the power value using getattr and take absolute value
                    Energy_value = abs(getattr(energy_doc, str(appliance_id)))
                    Energy_values.append(Energy_value)
                
        # Calculate the total energy consumption
        total_energy_consumption = sum(Energy_values)
        
        # Return the total energy consumption as JSON
        return jsonify({'total_energy_consumption': total_energy_consumption})

    except Exception as e:
        traceback.print_exc()  # This will print the full traceback to the console
        return jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"})

def calculate_user_energy_consumption(user_id, start_date, end_date):
    try:
        # Validate start_date and end_date
        if not isinstance(start_date, (datetime, date)):
            return jsonify({'message': 'Invalid start_date format.'}), 400

        if not isinstance(end_date, (datetime, date)):
            return jsonify({'message': 'Invalid end_date format.'}), 400

        # Check if start_date is before or equal to end_date
        if start_date > end_date:
            return jsonify({'message': 'start_date must be before or equal to end_date.'}), 400

        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return jsonify({'message': 'User not found.'}), 404

        print(f"end date: {end_date}")
        print(f"start date: {start_date}")


        # Filter energy documents by user ID and date range
        energy_documents = Energy.objects(user=user_id, date__gte=start_date, date__lte=end_date)
        if not energy_documents:
            return {'message': 'No energy documents found for this user in the specified date range.'}, 404
        
        appliances = user.appliances
        
        Energy_values = []

        for energy_doc in energy_documents:
            # Iterate over the user's appliances
            for appliance in appliances:
                # Check if the appliance_id exists in energy_readings
                if str(appliance._id) in energy_doc:
                    # Retrieve the power value using getattr and take absolute value
                    Energy_value = abs(getattr(energy_doc, str(appliance._id)))
                    Energy_values.append(Energy_value)

        # Calculate the total energy consumption
        total_energy_consumption = sum(Energy_values)
        
        # Return the total energy consumption as JSON
        return jsonify({'total_energy_consumption': total_energy_consumption})

    except Exception as e:
        traceback.print_exc()  # This will print the full traceback to the console
        return jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"})