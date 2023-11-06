# Import necessary modules
from flask import Flask, jsonify, make_response
from app.models.energy_model import Energy
from app.models.room_model import Room
from app.models.user_model import User
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import traceback


# Function to validate date format
def validate_date_format(this_date):
    if not isinstance(this_date, (datetime, date)):
        return make_response(jsonify({'message': 'Invalid date format.'}), 400)
    return None

# Function to validate date range
def validate_date_range(start_date, end_date):
    if start_date > end_date:
        return make_response(jsonify({'message': 'start_date must be before or equal to end_date.'}), 400)
    return None

# Function to get energy consumption
def get_energy(user_id, interval, time_since_current, room_id=None, appliance_id=None):
    try:
        # Assuming current date is 11/6/2023
        current_date = datetime.now()  

        # Calculate start and end dates based on interval and time_since_current
        if interval == "daily":
            start_date = current_date - timedelta(days=time_since_current)
            end_date = start_date
        elif interval == "weekly":
            # Calculate the first day of the target week (Sunday)
            start_date = current_date - timedelta(weeks=time_since_current)

            # Find the nearest Sunday in the target week
            day_of_week = start_date.weekday()
            days_until_sunday = day_of_week -1
            start_date += timedelta(days=days_until_sunday)

            # Calculate the date of the following Saturday
            end_date = start_date + timedelta(days=6)
            
        elif interval == "monthly":
            # Find the first day of the target month
            start_date = (current_date.replace(day=1) - timedelta(weeks=time_since_current*4)).replace(day=1)
            # Calculate the last day of the target month
            end_date = (start_date.replace(month=start_date.month+1) - timedelta(days=1))
        elif interval == "yearly":
            # Find the first day of the target month
            start_date = current_date.replace(month=1, day=1, year=current_date.year - time_since_current)
            # Calculate the last day of the target month
            end_date = (start_date.replace(year=start_date.year + 1) - timedelta(days=1))
        else:
            raise ValueError(f"Invalid interval: {interval}")
        # Depending on the provided parameters, call specific energy calculation functions
        if room_id is not None:
            return calculate_room_energy_consumption(user_id, room_id, start_date, end_date)
        elif appliance_id is not None:
            return calculate_appliance_energy_consumption(user_id, appliance_id, start_date, end_date)
        else:
            return calculate_user_energy_consumption(user_id, start_date, end_date)

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while getting energy consumption: {str(e)}"}))

# Function to calculate energy consumption for a specific appliance
def calculate_appliance_energy_consumption(user_id, appliance_id, start_date, end_date):
    try:
        # Validate dates
        validate_date_format(start_date)
        validate_date_format(end_date)
        validate_date_range(start_date, end_date)

        # Get user and appliance
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return make_response(jsonify({'message': 'User not found.'}), 404)

        appliance = next((app for app in user.appliances if str(app._id) == appliance_id), None)
        if not appliance:
            return make_response(jsonify({'message': 'Appliance not found'}), 404)

        # Query energy documents for the specified date range
        energy_documents = Energy.objects(user=user_id, date__gte=start_date, date__lte=end_date)
        if not energy_documents:
            return make_response(jsonify({'message': 'No energy documents found for this user in the specified date range.'}), 404)

        # Calculate energy consumption values
        Energy_values = []

        for energy_doc in energy_documents:
            if appliance_id in energy_doc:
                Energy_value = abs(getattr(energy_doc, appliance_id))
                Energy_values.append(Energy_value)

        total_energy_consumption = sum(Energy_values)

        return make_response(jsonify({'total_energy_consumption': total_energy_consumption}))

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))

# Function to calculate energy consumption for a specific room
def calculate_room_energy_consumption(user_id, room_id, start_date, end_date):
    try:
        # Validate dates
        validate_date_format(start_date)
        validate_date_format(end_date)
        validate_date_range(start_date, end_date)

        # Get user and room
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return make_response(jsonify({'message': 'User not found.'}), 404)

        room = Room.objects(id=room_id, user_id=user_id).first()
        if not room:
            return make_response(jsonify({'message': 'Room not found'}), 404)

        appliances_in_room = room.appliances

        # Query energy documents for the specified date range
        energy_documents = Energy.objects(user=user_id, date__gte=start_date, date__lte=end_date)
        if not energy_documents:
            return make_response(jsonify({'message': 'No energy documents found for this user in the specified date range.'}), 404)

        # Calculate energy consumption values
        Energy_values = []

        for energy_doc in energy_documents:
            for appliance_id in appliances_in_room:
                if str(appliance_id) in energy_doc:
                    Energy_value = abs(getattr(energy_doc, str(appliance_id)))
                    Energy_values.append(Energy_value)

        total_energy_consumption = sum(Energy_values)

        return make_response(jsonify({'total_energy_consumption': total_energy_consumption}))

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))

# Function to calculate energy consumption for a user
def calculate_user_energy_consumption(user_id, start_date, end_date):
    try:
        # Validate dates
        validate_date_format(start_date)
        validate_date_format(end_date)
        validate_date_range(start_date, end_date)

        print(start_date)
        print(end_date)
        # Get user
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return make_response(jsonify({'message': 'User not found.'}), 404)

        # Query energy documents for the specified date range
        energy_documents = Energy.objects(user=user_id, date__gte=start_date, date__lte=end_date)
        if not energy_documents:
            return make_response(jsonify({'message': 'No energy documents found for this user in the specified date range.'}), 404)

        appliances = user.appliances

        # Calculate energy consumption values
        Energy_values = []

        for energy_doc in energy_documents:
            for appliance in appliances:
                if str(appliance._id) in energy_doc:
                    Energy_value = abs(getattr(energy_doc, str(appliance._id)))
                    Energy_values.append(Energy_value)

        total_energy_consumption = sum(Energy_values)

        return make_response(jsonify({'total_energy_consumption': total_energy_consumption}))

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))
