# Import necessary modules
from flask import Flask, jsonify, make_response
from app.models.energy_model import Energy
from app.models.room_model import Room
from app.models.user_model import User
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import traceback
from app.utils.enums import Timeframe
from calendar import month_name,day_name


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

        current_date = datetime.now()  

        # Calculate start and end dates based on interval and time_since_current
        if interval == Timeframe.DAILY:
            start_date = current_date - timedelta(days=time_since_current)
            end_date = start_date
        elif interval == Timeframe.WEEKLY:
            # Calculate the first day of the target week (Sunday)
            start_date = current_date - timedelta(weeks=time_since_current, days=current_date.weekday() + 1)  # Adjust to Sunday of the target week

            # Calculate the date of the following Saturday
            end_date = current_date
            
        elif interval == Timeframe.MONTHLY:
            # Find the first day of the target month
            start_date = (current_date.replace(day=1) - timedelta(weeks=time_since_current*4)).replace(day=1)
            # Calculate the last day of the target month
            end_date = (start_date.replace(month=start_date.month+1) - timedelta(days=1))
            name= month_name[start_date.month]
        elif interval == Timeframe.YEARLY:
            # Find the first day of the target year
            start_date = current_date.replace(month=1, day=1, year=current_date.year - time_since_current)
            # Calculate the last day of the target year
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
        if not appliance or appliance.is_deleted:
            return make_response(jsonify({'message': 'Appliance not found'}), 404)
        print(start_date)
        print(end_date)
        
        # Query energy documents for the specified date range and sort by date in ascending order
        energy_documents = Energy.objects(user=user_id, date__gte=start_date, date__lte=end_date).order_by('date')

        if not energy_documents:
            return make_response(jsonify({'message': 'No energy documents found for this user in the specified date range.'}), 404)

        for energy_doc in energy_documents:
                print (energy_doc.date)
        
        # Calculate energy consumption values
        if (end_date - start_date).days > 31:  # Check if yearly
            monthly_energy_values = {month: 0 for month in range(1, 13)}

            for energy_doc in energy_documents:
                total_energy_value = 0
                if energy_doc.date == datetime.now().date():
                    total_energy_value += appliance.energy 
                else:
                    total_energy_value += abs(getattr(energy_doc, str(appliance._id)))

                month = energy_doc.date.month
                monthly_energy_values[month] += total_energy_value

            # Return the result with month names
            month_names = [month_name[month] for month in range(1, 13)]
            result = [{'month': month_names[i], 'energy_value': monthly_energy_values[i + 1]} for i in range(12)]
        
            return make_response(jsonify({'energy_values': result}), 200)

        
        else:
            Energy_values = []

            for energy_doc in energy_documents:
                print(energy_doc.date)
                if appliance_id in energy_doc:
                    if energy_doc.date == datetime.now().date():
                        Energy_value = appliance.energy  # Update the last added value
                    else:
                        Energy_value = abs(getattr(energy_doc, appliance_id))

                    # Get the day name of the current energy document
                    day_name_value = day_name[energy_doc.date.weekday()]

                    # Append a list containing [day_name, Energy_value] to the Energy_values list
                    Energy_values.append([day_name_value, Energy_value])

                    print (day_name_value)
                    
            result = Energy_values
            month = month_name[start_date.month]

            return make_response(jsonify({'month': month, 'energy_values': result}), 200) 


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
        
        print (room.appliances)

        # Filter out deleted appliances
        appliances_in_room = [app for app in user.appliances if app._id in room.appliances and not app.is_deleted]

        
        # Query energy documents for the specified date range and sort by date in ascending order
        energy_documents = Energy.objects(user=user_id, date__gte=start_date, date__lte=end_date).order_by('date')

        if not energy_documents:
            return make_response(jsonify({'message': 'No energy documents found for this user in the specified date range.'}), 404)

        # Calculate energy consumption values
        
        if (end_date - start_date).days > 31:  # Check if yearly
            monthly_energy_values = {month: 0 for month in range(1, 13)}
            for energy_doc in energy_documents:
                total_energy_value = 0

                for appliance in appliances_in_room:
                    if str(appliance._id) in energy_doc:
                        if energy_doc.date == datetime.now().date():
                            total_energy_value+= appliance.energy 
                        else:
                            total_energy_value += abs(getattr(energy_doc, str(appliance._id)))
                        month = energy_doc.date.month
                        monthly_energy_values[month] += total_energy_value
            # Return the result with month names
            month_names = [month_name[month] for month in range(1, 13)]
            result = [{'month': month_names[i], 'energy_value': monthly_energy_values[i + 1]} for i in range(12)]    
            return make_response(jsonify({'energy_values': result}), 200)
        else:
            Energy_values = []

            for energy_doc in energy_documents:
                total_energy_value = 0

                for appliance in appliances_in_room:
                    if str(appliance._id) in energy_doc:
                        if energy_doc.date == datetime.now().date():
                            total_energy_value+= appliance.energy 
                        else:
                            total_energy_value += abs(getattr(energy_doc, str(appliance._id)))
                # Get the day name of the current energy document            
                day_name_value = day_name[energy_doc.date.weekday()]
                # Append a tuple containing (day_name, Energy_value) to the Energy_values list
                Energy_values.append((day_name_value, total_energy_value))

            result=Energy_values
            month = month_name[start_date.month]
                
                
            return make_response(jsonify({'month_name':month,'energy_values': result}), 200)

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


        # Get user
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return make_response(jsonify({'message': 'User not found.'}), 404)

        # Filter out deleted appliances
        appliances = [app for app in user.appliances if not app.is_deleted]

        
        # Query energy documents for the specified date range and sort by date in ascending order
        energy_documents = Energy.objects(user=user_id, date__gte=start_date, date__lte=end_date).order_by('date')

        if not energy_documents:
            return make_response(jsonify({'message': 'No energy documents found for this user in the specified date range.'}), 404)


        # Calculate energy consumption values
        if (end_date - start_date).days > 31:  # Check if yearly
            Energy_values = []
            monthly_energy_values = {month: 0 for month in range(1, 13)}
            for energy_doc in energy_documents:
                total_energy_value = 0
                for appliance in appliances:
                    if str(appliance._id) in energy_doc:
                        if energy_doc.date == datetime.now().date():
                            total_energy_value += appliance.energy 
                        else:
                            total_energy_value += abs(getattr(energy_doc, str(appliance._id)))
                        month = energy_doc.date.month
                        monthly_energy_values[month] += total_energy_value
            # Return the result with month names
            month_names = [month_name[month] for month in range(1, 13)]
            result = [{'month': month_names[i], 'energy_value': monthly_energy_values[i + 1]} for i in range(12)]    
            return make_response(jsonify({'energy_values': result}), 200)
        else:
        
            Energy_values = []
            for energy_doc in energy_documents:
                total_energy_value = 0
                for appliance in appliances:
                    if str(appliance._id) in energy_doc:
                        if energy_doc.date == datetime.now().date():
                            total_energy_value += appliance.energy 
                        else:
                            total_energy_value += abs(getattr(energy_doc, str(appliance._id)))
                    print (energy_doc.date)     
                # Get the day name of the current energy document            
                day_name_value = day_name[energy_doc.date.weekday()]
                # Append a tuple containing (day_name, Energy_value) to the Energy_values list
                Energy_values.append((day_name_value, total_energy_value))            
                            

            result=Energy_values
            month = month_name[start_date.month]
                    
                    
            return make_response(jsonify({'month_name':month,'energy_values': result}), 200)
    

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))

