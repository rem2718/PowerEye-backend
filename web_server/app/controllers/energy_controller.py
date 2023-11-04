# app\controllers\appliance_controller.py
from flask import Flask, jsonify
from app.models.energy_model import Energy 
from app.models.room_model import Room
from app.models.user_model import User
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def calculate_appliance_energy_consumption(user_id, appliance_id, start_date, end_date):
    try:
        # Verify the user ID
        print(f"User ID: {user_id}")
        # Get the user by ID
        user = User.objects.get(id=user_id)
        print(f"Retrieved User: {user}")

        if not user:
            return jsonify({'message': 'User not found'}), 404  # Return a response if user not found

        energy_data = Energy.objects(
            user_id=user.id,
            date__gte=start_date,
            date__lte=end_date
        )
        print(f"Energy Data: {energy_data}")

        # Convert the appliance ID to a string
        appliance_id_str = str(appliance_id)

        # retrieve the energy reading for the specific appliance. 
        # If not, it returns a default value of 0.
        appliance_energy_data = [
            data.energy_readings.get(appliance_id_str, 0) for data in energy_data
        ]
        print(f"Appliance Energy Data: {appliance_energy_data}")

        # Calculate the energy consumption
        energy_consumption = sum(appliance_energy_data)
        print(f"consumption = {energy_consumption}")
        return energy_consumption

    except Exception as e:
        print(f"An error occurred while calculating energy consumption: {str(e)}")
        return jsonify({'error': 'An error occurred while finding the energy'})

def get_appliance_energy(user_id, appliance_id, time_since_current, interval):
    try:
        # Calculate the start and end dates based on the interval
        # Get the current date
        end_date = datetime.now().date()
        print(end_date)

        if interval == 'daily':
            start_date = end_date - timedelta(days = time_since_current)
            print(start_date)
        elif interval == 'weekly':
            # if time_since_current is 1, it will be a range of 7 days. If time_since_current is 2, 
            # it will be a range of two weeks....
            start_date = end_date - timedelta(days = 7 * time_since_current)
            print(start_date)
        elif interval == 'monthly':
            start_date = end_date - relativedelta(months = time_since_current)
            print(start_date)
        elif interval == 'yearly':
            start_date = end_date - relativedelta(years = time_since_current)
            print(start_date)
        else:
            return jsonify({'error': 'Invalid interval'})

        # Calculate energy consumption for the specified interval
        energy_consumption = calculate_appliance_energy_consumption(user_id, appliance_id, start_date, end_date)

        # Return the energy consumption as a JSON response
        return jsonify({'appliance_id': appliance_id, 'time_frame': interval,
                         'energy_consumption': energy_consumption})

    except Exception as e:
        print(f"An error occurred while retrieving appliance energy: {str(e)}")
        return jsonify({'error': 'An error occurred while retrieving appliance energy'})


def get_room_daily_energy(time_since_current):
    return
def get_room_weekly_energy(time_since_current):
    return
def get_room_monthly_energy(time_since_current):
    return
def get_room_yearly_energy(time_since_current):
    return


def get_total_daily_energy(time_since_current):
    return
def get_total_weekly_energy(time_since_current):
    return
def get_total_monthly_energy(time_since_current):
    return
def get_total_yearly_energy(time_since_current):
    return