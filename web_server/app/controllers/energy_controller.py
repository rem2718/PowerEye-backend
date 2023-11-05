# app\controllers\appliance_controller.py
from flask import Flask, jsonify
from app.models.energy_model import Energy 
from app.models.room_model import Room
from app.models.user_model import User
from app.models.appliance_model import Appliance
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil import parser
from app import db  # Import your mongoengine instance
from mongoengine import Q
from bson import ObjectId

def calculate_appliance_energy_consumption(user_id, appliance_id, start_date, end_date):
    try:
        # Verify the user ID
        print(f"User ID: {user_id}")
        print(f"Appliance ID: {appliance_id}")
        # Get the user by ID
        user = User.objects.get(id=user_id)
        print(f"Retrieved User: {user}")
        # Convert the user_id to the appropriate data type
        user_id_obj = ObjectId(user_id)

        if not user:
            return jsonify({'message': 'User not found'}), 404  # Return a response if user not found

        # Convert start_date and end_date to datetime.datetime objects if they are of type datetime.date
        if type(start_date) == datetime.date:
            start_date = datetime.datetime.combine(start_date, datetime.datetime.min.time())
        if type(end_date) == datetime.date:
            end_date = datetime.datetime.combine(end_date, datetime.datetime.min.time())

        print(f"end date: {end_date}")
        print(f"start date: {start_date}")

        # # Get the energy readings within the specified date range for the user and appliance
        # energy_readings = Energy.objects.filter(
        #     user_id=user,
        #     date__gte=start_date,
        #     date__lte=end_date
        # ).all()
        # Construct the query using the Q object
        query = Q(user_id=user_id_obj) & Q(date__gte=start_date) & Q(date__lte=end_date)
        print(f"Query Conditions: {query}")

        # Retrieve the energy readings matching the query
        energy_readings = Energy.objects(query)
        print(f"Raw Query: {energy_readings._query}")

        # Calculate the energy consumption for the specified appliance
        energy_consumption = 0
        print(f"Energy Readings Count: {energy_readings.count()}")
        for energy_reading in energy_readings:
            print(f"User ID: {energy_reading.user_id}")
            print(f"Date: {energy_reading.date}")
            print(f"Energy Readings: {energy_reading.energy_readings}")
            if energy_reading.energy_readings and appliance_id in energy_reading.energy_readings:
                energy_value = energy_reading.energy_readings[appliance_id]
                energy_consumption += energy_value

        print(f"Energy Consumption: {energy_consumption}")
        return energy_consumption

        # # Calculate the energy consumption for the specified appliance
        # energy_consumption = 0
        # for energy in energy_data:
        #     appliance_reading = energy.energy_readings.get(str(appliance_id))
        #     if appliance_reading is not None:
        #         energy_consumption += appliance_reading

        # print(f"Energy Consumption: {energy_consumption}")
        # return energy_consumption

    except Exception as e:
        print(f"An error occurred while calculating energy consumption: {str(e)}")
        return jsonify({'error': 'An error occurred while finding the energy'})

def get_appliance_energy(user_id, appliance_id, time_since_current, interval):
    try:
        # Calculate the start and end dates based on the interval
        # Get the current date
        # end_date = datetime.now().date()
        end_date = datetime(2023, 8, 20).date()
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
        energy_consumption = calculate_appliance_energy_consumption(user_id, appliance_id, 
                                                                    start_date, end_date)

        # Return the energy consumption as a JSON response
        return jsonify({'appliance_id': appliance_id, 'time_frame': interval,
                         'energy_consumption': energy_consumption})

    except Exception as e:
        print(f"An error occurred while retrieving {interval} appliance energy: {str(e)}")
        return jsonify({'error': 'An error occurred while retrieving appliance energy'})


def get_room_energy(user_id, room, time_since_current, interval):
    try:
        # Calculate the start and end dates based on the interval
        #end_date = datetime.now().date()
        end_date = datetime(2023, 10, 28).date()
        print(end_date)

        if interval == 'daily':
            start_date = end_date - timedelta(days = time_since_current)
            print(start_date)
        elif interval == 'weekly':
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

        # Retrieve the rooms from the database
        rooms = Room.objects()

        # Calculate the energy data for each room
        for room in rooms:
            room_energy = calculate_room_energy(user_id, room, start_date, end_date)
            print(f"room = {room_energy}")
        
        return jsonify({
            'room_id': str(room.id),
            'time_frame': interval,
            'room_energy_consumption': room_energy
        })
    
    except Exception as e:
        print(f"An error occurred while retrieving {interval} room energy: {str(e)}")
        return jsonify({'error': 'An error occurred while retrieving {interval} room energy'})

def calculate_room_energy(user_id, room, start_date, end_date):
    try:
        # Make sure room is a valid Room object
        if not isinstance(room, Room):
            return 0
        
        # Calculate the energy consumption for the room within the specified interval
        total_energy = 0
        for appliance_id in room.appliances:
            appliance_energy = calculate_appliance_energy_consumption(user_id, appliance_id, start_date, end_date)
            total_energy += appliance_energy

        return total_energy

    except Exception as e:
        print(f"An error occurred while calculating room energy: {str(e)}")
        return 0

def get_total_energy(user_id, interval, time_since_current):
    try:
        # Calculate the start and end dates based on the interval
        #end_date = datetime.now().date()
        end_date = datetime(2023, 10, 28).date()
        print(end_date)

        if interval == 'daily':
            start_date = end_date - timedelta(days = time_since_current)
            print(start_date)
        elif interval == 'weekly':
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

        # Call the calculate_user_energy_consumption method with the provided user_id and date range
        total_energy = calculate_user_energy_consumption(user_id, start_date, end_date)

        return jsonify({
            'user_id': user_id,
            'time_frame': interval,
            'total_energy_consumption': total_energy
        })

    except Exception as e:
        print(f"An error occurred while calculating total {interval} energy: {str(e)}")
        return jsonify({'error': f"An error occurred while calculating total {interval} energy"})
    
def calculate_user_energy_consumption(user_id, start_date, end_date):
    try:
        # Retrieve the user instance based on user_id
        user = User.objects.get(id=user_id)
        
        # Calculate the total energy consumption for the user within the specified interval
        total_energy = 0 #hold the cumulative energy consumption for all appliances
        #Iterate over each appliance belonging to the user
        for appliance_id in user.appliances:
            # calculates the energy consumption for the specific appliance
            appliance_energy = calculate_appliance_energy_consumption(user_id, appliance_id, start_date, end_date)
            # Add the energy consumption for the current appliance to the total
            total_energy += appliance_energy

        return total_energy
    
    except Exception as e:
        print(f"An error occurred while calculating user energy consumption: {str(e)}")