# Import necessary modules
from app.models.energy_model import Energy
from app.models.room_model import Room
from app.models.user_model import User


from datetime import datetime, timedelta
from collections import defaultdict
from flask import jsonify, make_response
from mongoengine.errors import DoesNotExist
import traceback
from calendar import month_abbr
from dateutil.relativedelta import relativedelta  # Add this import
from mongoengine import FloatField



WEEKS= 4
YEARS= 4
CURRENT_DATE = datetime.now()
CURRENT_MONTH = CURRENT_DATE.month
CURRENT_YEAR = CURRENT_DATE.year


CURRENT_YEAR_START_DATE = datetime(CURRENT_YEAR, 1, 1)
CURRENT_YEAR_END_DATE = datetime(CURRENT_YEAR, 12, 31)

def convert_to_weekly_energy_format(data):
    # Convert date strings to datetime objects
    formatted_data = {datetime.strptime(date_str, '%Y-%m-%d').date(): values for date_str, values in data.items()}

    # Sort the data by date in ascending order
    sorted_data = sorted(formatted_data.items(), key=lambda x: x[0])

    # Initialize result list
    result_list = []

    # Group the data into weeks
    week_data = defaultdict(list)
    current_week_start = None

    for date, values in sorted_data:
        if not current_week_start:
            current_week_start = date

        week_data[current_week_start].append(values)

        if date.weekday() == 6:  # Sunday
            current_week_start = None

    # Generate the final result
    for i, (week_start, week_values) in enumerate(reversed(list(week_data.items()))):
        if i == 0:
            week_title = "This Week"
        else:
            weeks_ago= (datetime.now().date() - week_start).days // 7
            week_title = f'{weeks_ago} Week{"s" if weeks_ago > 1 else ""} ago'
        energy_values = defaultdict(list)

        # Ensure the week starts from Monday and fill missing days with zeros
        for day_values in week_values:
            current_day = day_values['day']
            energy_values[current_day].append(day_values['energy'])

        # Fill missing days with zeros
        for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            if day not in energy_values:
                energy_values[day] = [0]

        result_list.append({
            'title': week_title,
            'label': list(energy_values.keys()),
            'energy': [sum(values) / len(values) if values else 0 for values in energy_values.values()]
        })

    return result_list

def convert_to_monthly_energy_format(data):
    monthly_data = []

    # Extract unique month names from the data
    month_names = list(set(date.split('-')[1] for date in data.keys()))
    month_names.sort()  # Sort month names

    for month in month_names:
        # Filter data for the current month
        month_data = {date: value for date, value in data.items() if date.startswith(f'2023-{month}')}
        
        # Extract day labels and energy values
        day_labels = list(range(1, len(month_data) + 1))
        energy_values = list(month_data.values())

        # Get the month abbreviation
        month_abbrv = month_abbr[int(month)]

        # Create a monthly entry
        monthly_entry = {
            'title': month_abbrv,
            'label': day_labels,
            'energy': energy_values
        }

        # Append the entry to the result list
        monthly_data.append(monthly_entry)

    return monthly_data

def convert_to_yearly_energy_format(data):
    current_year = datetime.now().year
    monthly_data = [[0] * 12 for _ in range(current_year - min(map(lambda x: int(x[:4]), data.keys())) + 1)]

    for date, value in data.items():
        year, month, _ = map(int, date.split('-'))
        year_index = current_year - year
        if 0 <= year_index < len(monthly_data):
            monthly_data[year_index][month - 1] += value

    # Extract unique month names from the data
    unique_month_names = sorted(set(date.split('-')[1] for date in data.keys()), key=lambda x: int(x))
    labels = [month_abbr[int(month)] for month in unique_month_names]

    yearly_data = [
        {
            'title': f'Year {current_year - i}',
            'label': labels,
            'energy': month_values
        }
        for i, month_values in enumerate(monthly_data)
    ]

    return yearly_data
# ____________________________________________________________________________________________________________________________________

def convert_to_total_weekly_energy_format(data):
    # Convert date strings to datetime objects
    formatted_data = {datetime.strptime(date_str, '%Y-%m-%d').date(): values for date_str, values in data.items()}

    # Sort the data by date in ascending order
    sorted_data = sorted(formatted_data.items(), key=lambda x: x[0])

    # Initialize result list
    result_list = []

    # Group the data into weeks
    week_data = defaultdict(list)
    current_week_start = None

    for date, values in sorted_data:
        if not current_week_start:
            current_week_start = date

        week_data[current_week_start].append(values)

        if date.weekday() == 6:  # Sunday
            current_week_start = None

    # Generate the final result
    for i, (week_start, week_values) in enumerate(reversed(list(week_data.items()))):
        if i == 0:
            week_title = "This Week"
        else:
            week_title = f"{(datetime.now().date() - week_start).days // 7 } week(s) ago"

        energy_values = defaultdict(list)

        # Ensure the week starts from Monday and fill missing days with zeros
        for day_values in week_values:
            current_day = day_values['day']
            energy_values[current_day].append(day_values['energy'])

        # Fill missing days with zeros
        for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            if day not in energy_values:
                energy_values[day] = [0]

        result_list.append({
            'title': week_title,
            'label': list(energy_values.keys()),
            'energy': [sum(values) / len(values) if values else 0 for values in energy_values.values()]
        })

    return result_list
# _____________________________________________________________________________________________________________________________________

def get_appliance_daily_energy(user_id, appliance_id):
    try:

        # Get user
        user = User.objects.get(id=user_id, is_deleted=False)
        appliance = next((app for app in user.appliances if str(app._id) == str(appliance_id) and not app.is_deleted), None)

        if not user or not appliance:
            message = 'User not found.' if not user else 'Appliance not found.'
            return make_response(jsonify({'message': message}), 404)
        
        return make_response(jsonify(appliance.energy), 200)
    
    except DoesNotExist:
        return make_response(jsonify({'message': 'User or Appliance not found'}), 404)

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))


def get_room_daily_energy(user_id, room_id):
    try:

        # Get user and room
        user = User.objects.get(id=user_id, is_deleted=False)
        room = Room.objects.get(id=room_id)
        if not user or not room:
            message = 'User not found.' if not room else 'Room not found.'
            return make_response(jsonify({'message': message}), 404)

        # Filter appliances by matching IDs and not deleted
        room_appliances = [
            app for app in user.appliances
            if str(app._id) in map(str, room.appliances) and not app.is_deleted
        ]

        # Calculate total energy consumption for the room
        total_energy_consumption = sum(appliance.energy for appliance in room_appliances)

        return make_response(jsonify(total_energy_consumption), 200)

    except DoesNotExist:
        return make_response(jsonify({'message': 'User or Room not found'}), 404)


    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}), 500)


def get_total_daily_energy(user_id):
    try:
        # Get user 
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return make_response(jsonify({'message': 'User not found.'}), 404)
        
        # Filter out deleted appliances
        appliances = [app for app in user.appliances if not app.is_deleted]

        # Calculate total energy consumption for the room
        total_energy_consumption = sum(appliance.energy for appliance in appliances)

        return make_response(jsonify(total_energy_consumption), 200)

    except DoesNotExist:
        return make_response(jsonify({'message': 'User not found'}), 404)

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}), 500)

# _____________________________________________________________________________________________________________________________________

def get_appliance_weekly_energy(user_id, appliance_id):
    try:
        # Get user and appliance
        user = User.objects.get(id=user_id, is_deleted=False)
        appliance = next((app for app in user.appliances if str(app._id) == str(appliance_id) and not app.is_deleted), None)

        if not user or not appliance:
            message = 'User not found.' if not user else 'Appliance not found.'
            return make_response(jsonify({'message': message}), 404)

        # Fetch energy documents for the last 28 days (4 weeks)
        last_date_to_query = CURRENT_DATE - timedelta(WEEKS*7)
        energy_docs = Energy.objects(user=user_id, date__gte=last_date_to_query)

        # Create a dictionary to store energy values for each date along with the day name prefix
        result = {date.strftime('%Y-%m-%d'): {'day': date.strftime('%a'), 'energy': 0} for date in (CURRENT_DATE - timedelta(days=i) for i in range((WEEKS*7)+1))}

        # Populate the result dictionary with energy values
        for energy_doc in energy_docs:
            date_str = energy_doc.date.strftime('%Y-%m-%d')
            result[date_str]['energy'] = abs(getattr(energy_doc, str(appliance._id), 0))

        # CURRENT_DATE energy is taken from the appliance document
        result[CURRENT_DATE.strftime('%Y-%m-%d')] = {'day': CURRENT_DATE.strftime('%a'), 'energy': appliance.energy}
        

        

        # Create the response data
        response_data = {
            'appliance_id': str(appliance._id),
            'weekly_energy_data': convert_to_weekly_energy_format(result)
        }

        return make_response(jsonify(response_data), 200)

    except DoesNotExist:
        return make_response(jsonify({'message': 'User or Appliance not found'}), 404)

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))

    
def get_room_weekly_energy(user_id, room_id):
    try:

        # Get user and room
        user = User.objects.get(id=user_id, is_deleted=False)
        room = Room.objects.get(id=room_id)
        if not user or not room:
            message = 'User not found.' if not room else 'Room not found.'
            return make_response(jsonify({'message': message}), 404)
        weeks= 5
        # Fetch energy documents for the last 28 days (4 weeks)
        date_to_query = CURRENT_DATE - timedelta(days=weeks*7)
        energy_docs = Energy.objects(user=user_id, date__gte=date_to_query)

        # Create a dictionary to store energy values for each date along with the day name prefix
        result = {date.strftime('%Y-%m-%d'): {'day': date.strftime('%a'), 'energy': 0} for date in (CURRENT_DATE - timedelta(days=i) for i in range(weeks*7 +1))}

        # Populate the result dictionary with energy values
        for energy_doc in energy_docs:
            for appliance_id in room.appliances:
                date_str = energy_doc.date.strftime('%Y-%m-%d')
                result[date_str]['energy'] += abs(getattr(energy_doc, str(appliance_id), 0))

        # CURRENT_DATE energy is taken from the appliance document
        today_energy=0.0
        for appliance_id in room.appliances:
            appliance = next((app for app in user.appliances if str(app._id) == str(appliance_id) and not app.is_deleted), None)
            today_energy += appliance.energy
        result[CURRENT_DATE.strftime('%Y-%m-%d')] = {'day': CURRENT_DATE.strftime('%a'), 'energy': today_energy}


        # Create the response data
        response_data = {
            'room_id': str(room.id),
            'weekly_energy_data': convert_to_weekly_energy_format(result)
        }
        return make_response(jsonify(response_data), 200)

    except DoesNotExist:
        return make_response(jsonify({'message': 'User or Room not found'}), 404)
    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))




def get_total_weekly_energy(user_id):
    try:
        # Get user and appliances
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            message = 'User not found.'
            return make_response(jsonify({'message': message}), 404)

        appliances = [app for app in user.appliances if not app.is_deleted]

        # Fetch energy documents for the entire duration except for today
        energy_docs = Energy.objects(user=user_id, date__gte=(CURRENT_DATE - timedelta(weeks=WEEKS, days=CURRENT_DATE.weekday())), date__lt=CURRENT_DATE)

        # Fetch today's energy directly from the appliances
        today_energy = [{'energy': appliance.energy, 'name': appliance.name} for appliance in appliances]

        # Create a list to store weekly energy data
        weekly_energy_data = []

        for weeks_ago in range(WEEKS):
            # Calculate the start and end date for the current week
            start_date = (CURRENT_DATE - timedelta(weeks=weeks_ago, days=CURRENT_DATE.weekday())).date()
            end_date = (CURRENT_DATE - timedelta(weeks=weeks_ago, days=CURRENT_DATE.weekday() - 6)).date()

            # Filter energy documents for the current week
            weekly_energy_docs = [doc for doc in energy_docs if start_date <= doc.date <= end_date]

            # Create a dictionary to accumulate energy values for each appliance for the current week
            total_energy_by_appliance = {appliance.name: 0 for appliance in appliances}

            # Accumulate energy values for each appliance for the current week
            for energy_doc in weekly_energy_docs:
                for appliance in appliances:
                    appliance_name = str(appliance.name)
                    total_energy_by_appliance[appliance_name] += abs(getattr(energy_doc, str(appliance._id), 0))
                    

            # Add today's energy directly from the appliances
            # If this is the current week, add today's energy to the energy of the current week
            if weeks_ago == 0:
                for entry in today_energy:
                    total_energy_by_appliance[entry['name']] += entry['energy']

            # Create the weekly energy data entry
            if weeks_ago == 0:
                title = 'This Week'
            else:
                title = f'{weeks_ago} Week{"s" if weeks_ago > 1 else ""} ago'

            weekly_entry = {
                'appliancesEnergy': [{'energy': energy, 'name': name} for name, energy in total_energy_by_appliance.items()],
                'title': title
            }

            # Add the weekly entry to the list
            weekly_energy_data.append(weekly_entry)

        return make_response(jsonify(weekly_energy_data), 200)

    except DoesNotExist:
        return False, jsonify({'message': 'User not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))

# _____________________________________________________________________________________________________________________________________

def get_appliance_monthly_energy(user_id, appliance_id):
    try:
        # Get user and appliance
        user = User.objects.get(id=user_id, is_deleted=False)
        appliance = next((app for app in user.appliances if str(app._id) == str(appliance_id) and not app.is_deleted), None)

        if not user or not appliance:
            message = 'User not found.' if not user else 'Appliance not found.'
            return make_response(jsonify({'message': message}), 404)


        # Fetch energy documents for the current year data

        energy_docs = Energy.objects(
            user=user_id,
            date__gte=CURRENT_YEAR_START_DATE,
            date__lte=CURRENT_YEAR_END_DATE
        ).order_by('date')

        # Create a dictionary to store energy values for each date
        date_range = [CURRENT_YEAR_START_DATE.date() + timedelta(days=i) for i in range((CURRENT_YEAR_END_DATE - CURRENT_YEAR_START_DATE).days + 1)]
        result = {date.strftime('%Y-%m-%d'): 0 for date in date_range}
        
        # Populate the result dictionary with energy values
        for energy_doc in energy_docs:
            date_str = energy_doc.date.strftime('%Y-%m-%d')
            result[date_str] = abs(getattr(energy_doc, str(appliance._id), 0))

        # CURRENT_DATE energy is taken from the appliance document
        result[CURRENT_DATE.strftime('%Y-%m-%d')] = appliance.energy
        

        # Create the response data
        response_data = {
            'appliance_id': str(appliance._id),
            'monthly_energy_data': convert_to_monthly_energy_format(result)
        }

        return make_response(jsonify(response_data), 200)

    except DoesNotExist:
        return make_response(jsonify({'message': 'User or Appliance not found'}), 404)

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))
    
def get_room_monthly_energy(user_id,room_id):
    try:
        
        # Get user and room
        user = User.objects.get(id=user_id, is_deleted=False)
        room = Room.objects.get(id=room_id)
        if not user or not room:
            message = 'User not found.' if not room else 'Room not found.'
            return make_response(jsonify({'message': message}), 404)

        
        # Fetch energy documents for the current year data
        energy_docs = Energy.objects(
            user=user_id,
            date__gte=CURRENT_YEAR_START_DATE,
            date__lte=CURRENT_YEAR_END_DATE
        ).order_by('date')
        
        # Create a dictionary to store energy values for each date
        date_range = [CURRENT_YEAR_START_DATE.date() + timedelta(days=i) for i in range((CURRENT_YEAR_END_DATE - CURRENT_YEAR_START_DATE).days + 1)]
        result = {date.strftime('%Y-%m-%d'): 0 for date in date_range}
            
            
        # Populate the result dictionary with energy values
        for energy_doc in energy_docs:
            for appliance_id in room.appliances:
                date_str = energy_doc.date.strftime('%Y-%m-%d')
                result[date_str] += abs(getattr(energy_doc, str(appliance_id), 0))
                
        # CURRENT_DATE energy is taken from the appliance document
        today_energy=0.0
        for appliance_id in room.appliances:
            appliance = next((app for app in user.appliances if str(app._id) == str(appliance_id) and not app.is_deleted), None)
            today_energy += appliance.energy
        result[CURRENT_DATE.strftime('%Y-%m-%d')]=today_energy


        # Create the response data
        response_data = {
            'room_id': str(room.id),
            'monthly_energy_data': convert_to_monthly_energy_format(result)
        }
        return make_response(jsonify(response_data), 200)

    except DoesNotExist:
        return make_response(jsonify({'message': 'User or Room not found'}), 404)

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))
    

def get_total_monthly_energy(user_id):
    try:
        # Get user and appliances
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            message = 'User not found.'
            return make_response(jsonify({'message': message}), 404)

        appliances = [app for app in user.appliances if not app.is_deleted]

        # Fetch energy documents for the entire duration except for today
        energy_docs = Energy.objects(user=user_id, date__gte=CURRENT_YEAR_START_DATE , date__lte=CURRENT_YEAR_END_DATE )
        # Fetch today's energy directly from the appliances
        today_energy = [{'energy': appliance.energy, 'name': appliance.name} for appliance in appliances]
        # Create a list to store monthly energy data
        monthly_energy_data = []

        for months_ago in range(1, 13):  # Iterate through the months of the current year
            # Calculate the start and end date for the current month
            start_date = datetime(CURRENT_YEAR, months_ago, 1).date()
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            # Filter energy documents for the current month
            monthly_energy_docs = [doc for doc in energy_docs if start_date <= doc.date <= end_date]

            # Create a dictionary to accumulate energy values for each appliance for the current month
            total_energy_by_appliance = {appliance.name: 0 for appliance in appliances}

            # Accumulate energy values for each appliance for the current month
            for energy_doc in monthly_energy_docs:
                for appliance in appliances:
                    appliance_name = str(appliance.name)
                    total_energy_by_appliance[appliance_name] += abs(getattr(energy_doc, str(appliance._id), 0))

            # If this is the current month, add today's energy to the energy of the current month
            if months_ago == CURRENT_MONTH:
                for entry in today_energy:
                    total_energy_by_appliance[entry['name']] += entry['energy']


            # Create the monthly energy data entry
            title = start_date.strftime('%b')  # Abbreviation of the month name
            monthly_entry = {
                'appliancesEnergy': [{'energy': energy, 'name': name} for name, energy in total_energy_by_appliance.items()],
                'title': title,
            }

            # Add the monthly entry to the list
            monthly_energy_data.append(monthly_entry)

        return make_response(jsonify(monthly_energy_data), 200)

    except DoesNotExist:
        return False, jsonify({'message': 'User not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))
    
# ______________________________________________________________________________________________________
def get_appliance_yearly_energy(user_id, appliance_id):
    try:
        # Get user and appliance
        user = User.objects.get(id=user_id, is_deleted=False)
        appliance = next((app for app in user.appliances if str(app._id) == str(appliance_id) and not app.is_deleted), None)

        if not user or not appliance:
            message = 'User not found.' if not user else 'Appliance not found.'
            return make_response(jsonify({'message': message}), 404)


        start_date = CURRENT_YEAR_START_DATE - relativedelta(years=YEARS)


        # Fetch energy documents for the current year data
        energy_docs = Energy.objects(
            user=user_id,
            date__gte=start_date,
            date__lte=CURRENT_YEAR_END_DATE
        ).order_by('date')
        
        # Create a dictionary to store energy values for each date
        date_range = [start_date.date() + timedelta(days=i) for i in range((CURRENT_YEAR_END_DATE - start_date).days + 1)]
        result = {date.strftime('%Y-%m-%d'): 0 for date in date_range}


        # Populate the result dictionary with energy values
        for energy_doc in energy_docs:
            date_str = energy_doc.date.strftime('%Y-%m-%d')
            result[date_str] = abs(getattr(energy_doc, str(appliance._id), 0))

        # CURRENT_DATE energy is taken from the appliance document
        result[CURRENT_DATE.strftime('%Y-%m-%d')] = appliance.energy
        
        # Create the response data
        response_data = {
            'appliance_id': str(appliance._id),
            'monthly_energy_data': convert_to_yearly_energy_format(result)
        }

        return make_response(jsonify(response_data), 200)

    except DoesNotExist:
        return make_response(jsonify({'message': 'User or Appliance not found'}), 404)

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))


def get_room_yearly_energy(user_id,room_id):
    try:

        # Get user and room
        user = User.objects.get(id=user_id, is_deleted=False)
        room = Room.objects.get(id=room_id)
        if not user or not room:
            message = 'User not found.' if not room else 'Room not found.'
            return make_response(jsonify({'message': message}), 404)

        
        # Fetch energy documents for the current year data
        
        start_date = CURRENT_YEAR_START_DATE - relativedelta(years=YEARS)
        
        energy_docs = Energy.objects(
            user=user_id,
            date__gte=start_date,
            date__lte=CURRENT_YEAR_END_DATE
        ).order_by('date')

        
        # Create a dictionary to store energy values for each date
        date_range = [start_date.date() + timedelta(days=i) for i in range((CURRENT_YEAR_END_DATE - start_date).days + 1)]
        result = {date.strftime('%Y-%m-%d'): 0 for date in date_range}
            
            
        # Populate the result dictionary with energy values
        for energy_doc in energy_docs:
            for appliance_id in room.appliances:
                date_str = energy_doc.date.strftime('%Y-%m-%d')
                result[date_str] += abs(getattr(energy_doc, str(appliance_id), 0))
                
        # CURRENT_DATE energy is taken from the appliance document
        today_energy=0.0
        for appliance_id in room.appliances:
            appliance = next((app for app in user.appliances if str(app._id) == str(appliance_id) and not app.is_deleted), None)
            today_energy += appliance.energy
        result[CURRENT_DATE.strftime('%Y-%m-%d')]=today_energy


        # Create the response data
        response_data = {
            'room_id': str(room.id),
            'yearly_energy_data': convert_to_yearly_energy_format(result)
        }
        return make_response(jsonify(response_data), 200)



    except DoesNotExist:
        return make_response(jsonify({'message': 'User not found'}), 404)

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))



def get_total_yearly_energy(user_id):
    try:
        # Get user and appliances
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            message = 'User not found.'
            return make_response(jsonify({'message': message}), 404)

        appliances = [app for app in user.appliances if not app.is_deleted]

        # Fetch energy documents for the past 4 years
        years_ago_start = CURRENT_YEAR_START_DATE - timedelta(days=365 * YEARS)
        energy_docs = Energy.objects(user=user_id, date__gte=years_ago_start, date__lte=CURRENT_YEAR_END_DATE)

        # Fetch today's energy directly from the appliances
        today_energy = [{'energy': appliance.energy, 'name': appliance.name} for appliance in appliances]

        # Create a list to store yearly energy data
        yearly_energy_data = []

        for years_ago in range(0, 4):  # Iterate through the past 4 years
            # Calculate the start and end date for the current year
            start_date = (CURRENT_YEAR_START_DATE - timedelta(days=365 * years_ago)).date()
            end_date = start_date + timedelta(days=365)

            # Filter energy documents for the current year
            yearly_energy_docs = [doc for doc in energy_docs if start_date <= doc.date <= end_date]

            # Create a dictionary to accumulate energy values for each appliance for the current year
            total_energy_by_appliance = {appliance.name: 0 for appliance in appliances}

            # Accumulate energy values for each appliance for the current year
            for energy_doc in yearly_energy_docs:
                for appliance in appliances:
                    appliance_name = str(appliance.name)
                    total_energy_by_appliance[appliance_name] += abs(getattr(energy_doc, str(appliance._id), 0))

            # If this is the current year, add today's energy to the energy of the current year
            if years_ago == 0:
                for entry in today_energy:
                    total_energy_by_appliance[entry['name']] += entry['energy']

            # Create the yearly energy data entry
            title = start_date.strftime('%Y')  # Year as the title
            yearly_entry = {
                'appliancesEnergy': [{'energy': energy, 'name': name} for name, energy in total_energy_by_appliance.items()],
                'title': title,
            }

            # Add the yearly entry to the list
            yearly_energy_data.append(yearly_entry)

        return make_response(jsonify(yearly_energy_data), 200)

    except DoesNotExist:
        return False, jsonify({'message': 'User not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))
# _____________________________________________________________________
def get_past_month_energy(user_id):
    try:
        # Get user and appliances
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            message = 'User not found.'
            return make_response(jsonify({'message': message}), 404)

        appliances = [app for app in user.appliances if not app.is_deleted]
        
        
        
        # Calculate the first day of the current month
        first_day_of_current_month = CURRENT_DATE.replace(day=1)

        # Calculate the last day of the previous month
        last_day_of_past_month = first_day_of_current_month - timedelta(days=1)

        # Calculate the first day of the previous month
        first_day_of_past_month = last_day_of_past_month.replace(day=1)

        # Fetch energy documents for the entire duration
        energy_docs = Energy.objects(user=user_id, date__gte=first_day_of_past_month , date__lte=last_day_of_past_month )


        # Accumulate energy values for each appliance for the past month
        total_energy=0
        for energy_doc in energy_docs:
            for appliance in appliances:
                total_energy += abs(getattr(energy_doc, str(appliance._id), 0))


        return make_response(jsonify(total_energy), 200)

    except DoesNotExist:
        return False, jsonify({'message': 'User not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))

def get_current_month_energy(user_id):
    try: 
        # Get user and appliances
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            message = 'User not found.'
            return make_response(jsonify({'message': message}), 404)

        appliances = [app for app in user.appliances if not app.is_deleted]
        total_energy= user.current_month_energy

        for appliance in appliances:
            total_energy += appliance.energy
        return make_response(jsonify(total_energy), 200)
    except DoesNotExist:
        return False, jsonify({'message': 'User not found'}), 404

    except Exception as e:
        traceback.print_exc()
        return make_response(jsonify({'error': f"An error occurred while calculating energy consumption: {str(e)}"}))