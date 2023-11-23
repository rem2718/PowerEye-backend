# Import necessary modules
from app.models.energy_model import Energy
from app.models.room_model import Room
from app.models.user_model import User

from datetime import datetime, timedelta,date
from collections import defaultdict
from flask import jsonify, make_response
from mongoengine.errors import DoesNotExist
import traceback
import calendar

def get_appliance_weekly_energy(user_id):
    try:
        current_date = datetime.now().date()
        
        # Get user 
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return make_response(jsonify({'message': 'User not found.'}), 404)
        
        # Initialize result list to store energy data for all appliances
        all_appliances_result = []

        # Loop through all appliances of the user
        for appliance in user.appliances:
            appliance_result = []

            # Get appliance
            if appliance.is_deleted:
                continue
            
            # Calculate energy consumption values
            
            result = defaultdict(float)

            for i in range(0, 29):  # Loop through dates from today to # weeks ago
                date_to_query = current_date - timedelta(days=i)
                
                if date_to_query == current_date:
                    energy_value = appliance.energy  # Update the last added value
                else:
                    # Query energy documents for the specified date and sort by date in ascending order
                    energy_documents = Energy.objects(user=user_id, date=date_to_query).order_by('date')

                    # If no energy document, append 0 to the result for each appliance
                    if not energy_documents:
                        energy_value = 0
                    else:
                        # Sum up the energy values for the specified appliance
                        for energy_doc in energy_documents:
                            energy_value = abs(getattr(energy_doc, str(appliance._id)))
                
                result[date_to_query.strftime('%Y-%m-%d')] += energy_value


            for i in range(4):
                title = 'this week' if i == 0 else f'{i} {"week" if i == 1 else "weeks"} ago'
                start_date = current_date - timedelta(days=current_date.weekday() + i * 7)
                labels = [start_date + timedelta(days=j) for j in range(7)]
                energy_values = [result[label.strftime('%Y-%m-%d')] for label in labels]

                appliance_result.append({
                    'title': title,
                    'label': [label.strftime('%A') for label in labels],
                    'energy': energy_values
                })


            # Create a dictionary for the current appliance
            appliance_data = {str(appliance._id): appliance_result}

            # Append the appliance data to the result list
            all_appliances_result.append(appliance_data)


        return make_response(jsonify(all_appliances_result), 200)

        
        
    except DoesNotExist:
        return False, jsonify({'message': 'User not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))
    
    
def get_room_weekly_energy(user_id):
    try:
        current_date = datetime.now()

        # Get user 
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return make_response(jsonify({'message': 'User not found.'}), 404)
        
        # Get room
        rooms = Room.objects(user_id=user_id)
        if not rooms:
            return make_response(jsonify({'message': ' No Rooms found'}), 404)

        
        # Initialize result list to store energy data for all rooms
        all_rooms_result = []


        for room in rooms:
            room_result = []
            # Filter out deleted appliances
            appliances_in_room = [app for app in user.appliances if app._id in room.appliances and not app.is_deleted]
            

            # Calculate energy consumption values
            
            result = defaultdict(list)

            for i in range(0, 29):  # Loop through dates from today to # weeks ago
                date_to_query = current_date - timedelta(days=i)
                # date_to_query= date_to_query.date()
                energy_value =0.0
                
                if date_to_query == current_date:
                    for appliance in appliances_in_room:
                        energy_value += abs(appliance.energy) 
                else:
                    # Query energy documents for the specified date and sort by date in ascending order
                    energy_documents = Energy.objects(user=user_id, date=date_to_query).order_by('date')
                    
                    # If no energy document, append (0, 0)
                    if not energy_documents:
                        energy_value =0.0
                    else:
                        for energy_doc in energy_documents:
                            for appliance in appliances_in_room:
                                if str(appliance._id) in energy_doc:
                                    energy_value += abs(energy_doc[str(appliance._id)])
                                    
                result[date_to_query.strftime('%Y-%m-%d')].append((str(room.id), energy_value))


            for i in range(4):
                title = 'this week' if i == 0 else f'{i} {"week" if i == 1 else "weeks"} ago'
                start_date = current_date - timedelta(days=current_date.weekday() + i * 7)
                labels = [start_date + timedelta(days=j) for j in range(7)]
                energy_values = [0] * 7

                for label in labels:
                    label_str = label.strftime('%Y-%m-%d')
                    if label_str in result:
                        energy_values[labels.index(label)] = sum([item[1] for item in result[label_str]])

                room_result.append({
                    'title': title,
                    'label': [label.strftime('%A') for label in labels],
                    'energy': energy_values
                })
                
            # Create a dictionary for the current appliance
            room_data = {str(room.id): room_result}

            # Append the appliance data to the result list
            all_rooms_result.append(room_data)


        return make_response(jsonify(all_rooms_result), 200)

        
    except DoesNotExist:
        return False, jsonify({'message': 'User not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))


def get_total_weekly_energy(user_id):
    try:
        current_date = datetime.now()

        # Get user 
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return make_response(jsonify({'message': 'User not found.'}), 404)
        

        # Filter out deleted appliances
        appliances = [app for app in user.appliances if not app.is_deleted]
        

        # Calculate energy consumption values
        
        result = defaultdict(list)

        for i in range(0, 29):  # Loop through dates from today to # weeks ago
            date_to_query = current_date - timedelta(days=i)
            date_to_query= date_to_query.date()
            energy_value =0.0
            
            if date_to_query == current_date.date():
                for appliance in appliances:
                    energy_value += abs(appliance.energy) 
            else:
                # Query energy documents for the specified date and sort by date in ascending order
                energy_documents = Energy.objects(user=user_id, date=date_to_query).order_by('date')
                # If no energy document, append (0, 0)
                if not energy_documents:
                    energy_value =0.0
                else:
                    for energy_doc in energy_documents:
                        for appliance in appliances:
                            if str(appliance._id) in energy_doc:
                                energy_value += abs(energy_doc[str(appliance._id)])
                                
            result[date_to_query.strftime('%Y-%m-%d')].append(energy_value)
        
        current_date = current_date.date()
        weeks_data = []

        #formatting
        
        for i in range(4):
            title = 'this week' if i == 0 else f'{i} {"week" if i == 1 else "weeks"} ago'
            start_date = current_date - timedelta(days=current_date.weekday() + i * 7)
            labels = [start_date + timedelta(days=j) for j in range(7)]
            energy_values = [0] * 7

            for label in labels:
                label_str = label.strftime('%Y-%m-%d')
                if label_str in result:
                    energy_values[labels.index(label)] = sum(result[label_str])

            weeks_data.append({
                'title': title,
                'label': [label.strftime('%A') for label in labels],
                'energy': energy_values
            })
        return make_response(jsonify(weeks_data), 200)
        
    except DoesNotExist:
        return False, jsonify({'message': 'User not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))


def get_appliance_monthly_energy(user_id):
    try:
        
        # Get user
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return make_response(jsonify({'message': 'User not found.'}), 404)

        # Get the current date
        current_date = datetime.now()

        # Extract the current month and year
        current_month = current_date.month
        current_year = current_date.year

        # Initialize result list to store energy data for all appliances
        all_appliances_result = []

        # Loop through all appliances of the user
        for appliance in user.appliances:
            appliance_result=[]
            
            if appliance.is_deleted:
                continue
            
            # Loop through each month since the beginning of the year
            for month in range(1, current_month + 1): #the loop iterates over the months from January (1) up to the current month (inclusive).
                # Get the first day of the month
                start_date = datetime(current_year, month, 1)

                # Calculate the last day of the month
                _, last_day_of_month = calendar.monthrange(current_year, month)#The first value in the tuple is the weekday of the first day of the month (0 for Monday, 1 for Tuesday, and so on). In this case, it's represented by _ (an underscore), which is a common convention in Python to indicate a variable that is not going to be used. The first value is ignored in this case.The second value in the tuple is the number of days in the month
                end_date = datetime(current_year, month, last_day_of_month)
                
                # Initialize the energy values for each day
                energy = []
                label = []
                
                
                energy_documents = Energy.objects(
                    user=user_id,
                    date__gte=start_date,
                    date__lte=end_date
                ).order_by('date')
                
                
                for day in range((end_date - start_date).days + 1):
                        date_to_query = start_date + timedelta(days=day)

                        # Check if it's the current date
                        if date_to_query.date() == current_date.date():
                            energy_value = appliance.energy
                        else:
                            # Filter energy documents for the specified day and appliance
                            energy_docs_for_day = [doc for doc in energy_documents if str(appliance._id) in doc and doc.date == date_to_query.date()]


                            # If no energy document, append (0, 0)
                            if not energy_docs_for_day:
                                energy_value =0.0
                            else:
                                energy_value = abs(energy_docs_for_day[0][str(appliance._id)])

                        energy.append(energy_value)
                        label.append(day+1)
                title = calendar.month_name[month]
            

                # Convert result to the desired format
                formatted_month_data = {
                    'title': title,
                    'label': label,
                    'energy': energy
                }

                appliance_result.append(formatted_month_data)
            # Create a dictionary for the current appliance
            appliance_data = {str(appliance._id): appliance_result}

            # Append the appliance data to the result list
            all_appliances_result.append(appliance_data)


        return make_response(jsonify(all_appliances_result), 200)



        return make_response(jsonify(formatted_data), 200)

    except DoesNotExist:
        return False, jsonify({'message': 'User not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))
    
    
def get_room_monthly_energy(user_id):
    try:
        current_date = datetime.now()

        # Extract the current month and year
        current_month = current_date.month
        current_year = current_date.year

        

        # Get user 
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return make_response(jsonify({'message': 'User not found.'}), 404)
        
        # Get room
        rooms = Room.objects(user_id=user_id)
        if not rooms:
            return make_response(jsonify({'message': ' No Rooms found'}), 404)

        
        # Initialize result list to store energy data for all rooms
        all_rooms_result = []

        
        for room in rooms:
            room_result = []
            # Filter out deleted appliances
            appliances_in_room = [app for app in user.appliances if app._id in room.appliances and not app.is_deleted]
            

                
            
            # Calculate energy consumption values

            formatted_data = []
            # Loop through each month since the beginning of the year
            for month in range(1, current_month + 1): #the loop iterates over the months from January (1) up to the current month (inclusive).
                # Get the first day of the month
                start_date = datetime(current_year, month, 1)

                # Calculate the last day of the month
                _, last_day_of_month = calendar.monthrange(current_year, month)#The first value in the tuple is the weekday of the first day of the month (0 for Monday, 1 for Tuesday, and so on). In this case, it's represented by _ (an underscore), which is a common convention in Python to indicate a variable that is not going to be used. The first value is ignored in this case.The second value in the tuple is the number of days in the month
                end_date = datetime(current_year, month, last_day_of_month)
                
                # Initialize the energy values for each day
                energy = []
                label = []
                
                
                energy_documents = Energy.objects(
                    user=user_id,
                    date__gte=start_date,
                    date__lte=end_date
                ).order_by('date')
                
                
                for day in range((end_date - start_date).days + 1):
                    energy_value=0
                    date_to_query = start_date + timedelta(days=day)

                    # Check if it's the current date
                    if date_to_query.date() == current_date.date():
                        for appliance in appliances_in_room:
                            energy_value += abs(appliance.energy)
                    else:
                        # Filter energy documents for the specified day and appliance
                        energy_docs_for_day = [doc for doc in energy_documents if doc.date == date_to_query.date()]

                        

                        # If no energy document, append (0, 0)
                        if not energy_docs_for_day:
                            energy_value = 0.0
                        else:
                            for energy_doc in energy_docs_for_day:
                                for appliance in appliances_in_room:
                                    if str(appliance._id) in energy_doc:                                        
                                        energy_value += abs(energy_doc[str(appliance._id)])

                    energy.append(energy_value)
                    label.append(day+1)
                title = calendar.month_name[month]
                

                # Convert result to the desired format
                formatted_month_data = {
                    'title': title,
                    'label': label,
                    'energy': energy
                }

                room_result.append(formatted_month_data)
                
            # Create a dictionary for the current appliance
            room_data = {str(room.id): room_result}

            # Append the appliance data to the result list
            all_rooms_result.append(room_data)


        return make_response(jsonify(all_rooms_result), 200)

    except DoesNotExist:
        return False, jsonify({'message': 'User not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))
    

def get_total_monthly_energy(user_id):
    try:
        # Get user
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return make_response(jsonify({'message': 'User not found.'}), 404)

        
        # Filter out deleted appliances
        appliances = [app for app in user.appliances if not app.is_deleted]
        
        # Get the current date
        current_date = datetime.now()

        # Extract the current month and year
        current_month = current_date.month
        current_year = current_date.year

        # Calculate energy consumption values

        formatted_data = []
        # Loop through each month since the beginning of the year
        for month in range(1, current_month + 1): #the loop iterates over the months from January (1) up to the current month (inclusive).
            # Get the first day of the month
            start_date = datetime(current_year, month, 1)

            # Calculate the last day of the month
            _, last_day_of_month = calendar.monthrange(current_year, month)#The first value in the tuple is the weekday of the first day of the month (0 for Monday, 1 for Tuesday, and so on). In this case, it's represented by _ (an underscore), which is a common convention in Python to indicate a variable that is not going to be used. The first value is ignored in this case.The second value in the tuple is the number of days in the month
            end_date = datetime(current_year, month, last_day_of_month)
            
            # Initialize the energy values for each day
            energy = []
            label = []
            
            
            energy_documents = Energy.objects(
                user=user_id,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date')
            
            
            for day in range((end_date - start_date).days + 1):
                energy_value=0
                date_to_query = start_date + timedelta(days=day)

                # Check if it's the current date
                if date_to_query.date() == current_date.date():
                    for appliance in appliances:
                        energy_value += abs(appliance.energy)
                else:
                    # Filter energy documents for the specified day and appliance
                    energy_docs_for_day = [doc for doc in energy_documents if doc.date == date_to_query.date()]

                    

                    # If no energy document, append (0, 0)
                    if not energy_docs_for_day:
                        energy_value = 0.0
                    else:
                        for energy_doc in energy_docs_for_day:
                            for appliance in appliances:
                                if str(appliance._id) in energy_doc:
                                    energy_value += abs(energy_doc[str(appliance._id)])
                energy.append(energy_value)
                label.append(day+1)
            title = calendar.month_name[month]
            

            # Convert result to the desired format
            formatted_month_data = {
                'title': title,
                'label': label,
                'energy': energy
            }

            formatted_data.append(formatted_month_data)


        return make_response(jsonify(formatted_data), 200)

    except DoesNotExist:
        return False, jsonify({'message': 'User not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))
    

def get_appliance_yearly_energy(user_id):
    try:
        # Get user
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return make_response(jsonify({'message': 'User not found.'}), 404)

        # Get the current date
        current_date = datetime.now()

        # Extract the current year
        current_year = current_date.year
        current_month = current_date.month

        
        # Initialize result list to store energy data for all appliances
        all_appliances_result = []

        # Loop through all appliances of the user
        for appliance in user.appliances:
            appliance_result=[]
            
            # Get appliance
            if appliance.is_deleted:
                continue
            
            # Calculate energy consumption values for the current year and the previous year
            for year_offset in range(0, 4):
                year_to_query = current_year - year_offset
                months_data = []

                
                # Determine the loop range based on the year_offset
                loop_range = range(1, current_month + 1) if year_offset == 0 else range(1, 13)
                # Loop through each month
                for month in loop_range:
                    start_date = datetime(year_to_query, month, 1)
                    _, last_day_of_month = calendar.monthrange(year_to_query, month)
                    end_date = datetime(year_to_query, month, last_day_of_month)

                    # Filter energy documents for the specified month and appliance
                    energy_documents = Energy.objects(
                        user=user_id,
                        date__gte=start_date,
                        date__lte=end_date
                    ).order_by('date')

                    # Initialize energy values for the month
                    monthly_energy = []

                    # Iterate over each day in the month
                    for day in range(1, last_day_of_month + 1):
                        date_to_query = datetime(year_to_query, month, day)

                        # Check if it's the current date
                        if date_to_query.date() == current_date.date() and year_offset == 0:
                            energy_value = appliance.energy
                        else:
                            # Filter energy documents for the specified day and appliance
                            energy_docs_for_day = [doc for doc in energy_documents if str(appliance._id) in doc and doc.date == date_to_query.date()]

                            # Sum up the energy values for all matching documents
                            energy_value = sum(abs(doc[str(appliance._id)]) for doc in energy_docs_for_day) if energy_docs_for_day else 0.0

                        monthly_energy.append(energy_value)

                    # Add monthly data to the list
                    months_data.append({
                        'title': calendar.month_name[month],
                        'label': list(range(1, last_day_of_month + 1)),
                        'energy': monthly_energy
                    })

                
                
                # Add yearly data to the list
                appliance_result.append({
                    'title': 'this year' if year_offset == 0 else f'{year_offset} {"year" if year_offset == 1 else "years"} ago',
                    'label': [calendar.month_name[i] for i in range(1, current_month + 1)] if year_offset == 0 else [calendar.month_name[i] for i in range(1,13)],
                    'energy': [sum(month['energy']) for month in months_data]
                })

            # Create a dictionary for the current appliance
            appliance_data = {str(appliance._id): appliance_result}

            # Append the appliance data to the result list
            all_appliances_result.append(appliance_data)


        return make_response(jsonify(all_appliances_result), 200)


    except DoesNotExist:
        return make_response(jsonify({'message': 'User not found'}), 404)

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))


def get_room_yearly_energy(user_id):
    try:

        # Get the current date
        current_date = datetime.now()

        # Extract the current year
        current_year = current_date.year
        current_month = current_date.month
        
        # Get user 
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return make_response(jsonify({'message': 'User not found.'}), 404)
        
        # Get room
        rooms = Room.objects(user_id=user_id)
        if not rooms:
            return make_response(jsonify({'message': ' No Rooms found'}), 404)

        
        # Initialize result list to store energy data for all rooms
        all_rooms_result = []

        # Loop through all appliances of the user
        for appliance in user.appliances:
            appliance_result=[]
        
        for room in rooms:
            room_result = []
            # Filter out deleted appliances
            appliances_in_room = [app for app in user.appliances if app._id in room.appliances and not app.is_deleted]
                
            for year_offset in range(0, 4):
                year_to_query = current_year - year_offset
                months_data = []

                
                # Determine the loop range based on the year_offset
                loop_range = range(1, current_month + 1) if year_offset == 0 else range(1, 13)
                # Loop through each month
                for month in loop_range:
                    start_date = datetime(year_to_query, month, 1)
                    _, last_day_of_month = calendar.monthrange(year_to_query, month)
                    end_date = datetime(year_to_query, month, last_day_of_month)

                    # Filter energy documents for the specified month and appliance
                    energy_documents = Energy.objects(
                        user=user_id,
                        date__gte=start_date,
                        date__lte=end_date
                    ).order_by('date')

                    # Initialize energy values for the month
                    monthly_energy = []

                    # Iterate over each day in the month
                    for day in range(1, last_day_of_month + 1):
                        energy_value=0
                        date_to_query = datetime(year_to_query, month, day)

                        # Check if it's the current date
                        if date_to_query.date() == current_date.date() and year_offset == 0:
                            for appliance in appliances_in_room:
                                energy_value += abs(appliance.energy)
                        else:
                            # Filter energy documents for the specified day and appliance
                            energy_docs_for_day = [doc for doc in energy_documents if doc.date == date_to_query.date()]


                            # If no energy document, append (0, 0)
                            if not energy_docs_for_day:
                                energy_value = 0.0
                            else:
                                for energy_doc in energy_docs_for_day:
                                    for appliance in appliances_in_room:
                                        if str(appliance._id) in energy_doc:
                                            energy_value += abs(energy_doc[str(appliance._id)])
                        monthly_energy.append(energy_value)

                    # Add monthly data to the list
                    months_data.append({
                        'title': calendar.month_name[month],
                        'label': list(range(1, last_day_of_month + 1)),
                        'energy': monthly_energy
                    })
                    

                
                
                # Add yearly data to the list
                room_result.append({
                    'title': 'this year' if year_offset == 0 else f'{year_offset} {"year" if year_offset == 1 else "years"} ago',
                    'label': [calendar.month_name[i] for i in range(1, current_month + 1)] if year_offset == 0 else [calendar.month_name[i] for i in range(1,13)],
                    'energy': [sum(month['energy']) for month in months_data]
                })

            # Create a dictionary for the current appliance
            room_data = {str(room.id): room_result}

            # Append the appliance data to the result list
            all_rooms_result.append(room_data)


        return make_response(jsonify(all_rooms_result), 200)


    except DoesNotExist:
        return make_response(jsonify({'message': 'User not found'}), 404)

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))


def get_total_yearly_energy(user_id):
    try:
        # Get user
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return make_response(jsonify({'message': 'User not found.'}), 404)

        # Filter out deleted appliances
        appliances = [app for app in user.appliances if not app.is_deleted]

        # Get the current date
        current_date = datetime.now()

        # Extract the current year
        current_year = current_date.year
        current_month = current_date.month

        # Calculate energy consumption values for the current year and the previous year
        yearly_data = []
        for year_offset in range(0, 4):
            year_to_query = current_year - year_offset
            months_data = []

            
            # Determine the loop range based on the year_offset
            loop_range = range(1, current_month + 1) if year_offset == 0 else range(1, 13)
            # Loop through each month
            for month in loop_range:
                start_date = datetime(year_to_query, month, 1)
                _, last_day_of_month = calendar.monthrange(year_to_query, month)
                end_date = datetime(year_to_query, month, last_day_of_month)

                # Filter energy documents for the specified month and appliance
                energy_documents = Energy.objects(
                    user=user_id,
                    date__gte=start_date,
                    date__lte=end_date
                ).order_by('date')

                # Initialize energy values for the month
                monthly_energy = []

                # Iterate over each day in the month
                for day in range(1, last_day_of_month + 1):
                    energy_value=0
                    date_to_query = datetime(year_to_query, month, day)

                    # Check if it's the current date
                    if date_to_query.date() == current_date.date() and year_offset == 0:
                        for appliance in appliances:
                            energy_value += abs(appliance.energy)
                    else:
                        # Filter energy documents for the specified day and appliance
                        energy_docs_for_day = [doc for doc in energy_documents if doc.date == date_to_query.date()]


                        # If no energy document, append (0, 0)
                        if not energy_docs_for_day:
                            energy_value = 0.0
                        else:
                            for energy_doc in energy_docs_for_day:
                                for appliance in appliances:
                                    if str(appliance._id) in energy_doc:
                                        energy_value += abs(energy_doc[str(appliance._id)])
                                        
                        monthly_energy.append(energy_value)

                # Add monthly data to the list
                months_data.append({
                    'title': calendar.month_name[month],
                    'label': list(range(1, last_day_of_month + 1)),
                    'energy': monthly_energy
                })
            
            # Add yearly data to the list
            yearly_data.append({
                'title': 'this year' if year_offset == 0 else f'{year_offset} {"year" if year_offset == 1 else "years"} ago',
                'label': [calendar.month_name[i] for i in range(1, current_month + 1)] if year_offset == 0 else [calendar.month_name[i] for i in range(1,13)],
                'energy': [sum(month['energy']) for month in months_data]
            })

        return make_response(jsonify(yearly_data), 200)

    except DoesNotExist:
        return make_response(jsonify({'message': 'User not found'}), 404)

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))