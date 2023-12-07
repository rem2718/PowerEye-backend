"""
Module: energy_views

This module defines Flask routes related to energy consumption.


Each route handles functionality related to energy consumption readings, 
including retrieving daily, weekly, monthly, and yearly energy consumption 
for appliances, rooms, and the total.

Routes:
- GET /appliance_energy/daily/<appliance_id>: Get the daily energy consumption for an appliance.
- GET /room_energy/daily/<room_id>: Get the daily energy consumption for a room.
- GET /total_energy/daily: Get the daily total energy consumption.
- GET /appliance_energy/weekly/<appliance_id>: Get the weekly energy consumption for an appliance.
- GET /appliance_energy/monthly/<appliance_id>: Get the monthly energy consumption for an appliance.
- GET /appliance_energy/yearly/<appliance_id>: Get the yearly energy consumption for an appliance.
- GET /room_energy/weekly/<room_id>: Get the weekly energy consumption for a  room.
- GET /room_energy/monthly/<room_id>: Get the monthly energy consumption for a room.
- GET /room_energy/yearly/<room_id>: Get the yearly energy consumption for a room.
- GET /total_energy/weekly: Get the weekly total energy consumption.
- GET /total_energy/monthly: Get the monthly total energy consumption.
- GET /total_energy/yearly: Get the yearly total energy consumption.

Parameters:
- appliance_id (str): The ID of the appliance.
- room_id (str): The ID of the room.

Returns:
JSON: The energy consumption data for the specified appliance, room, or the total.
"""
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.energy_controller import (
    get_appliance_daily_energy,
    get_room_daily_energy,
    get_total_daily_energy,
    get_appliance_weekly_energy,
    get_appliance_monthly_energy,
    get_appliance_yearly_energy,
    get_room_weekly_energy,
    get_room_monthly_energy,
    get_room_yearly_energy,
    get_total_weekly_energy,
    get_total_monthly_energy,
    get_total_yearly_energy,
    get_past_month_energy, get_current_month_energy
)

# Create a Blueprint to organize routes
energy_views = Blueprint('energy_views', __name__)

@energy_views.route('/appliance_energy/daily/<appliance_id>', methods=['GET'])
@jwt_required()
def appliance_daily_energy_route(appliance_id):
    """
    Endpoint to retrieve the daily energy consumption for a specific appliance.

    Parameters:
    - appliance_id (str): The ID of the appliance.

    Returns:
    JSON: The daily energy consumption for the specified appliance.
    """
    user_id = get_jwt_identity()
    return get_appliance_daily_energy(user_id,appliance_id)

@energy_views.route('/room_energy/daily/<room_id>', methods=['GET'])
@jwt_required()
def room_daily_energy_route(room_id):
    """
    Endpoint to retrieve the daily energy consumption for a specific room.

    Parameters:
    - room_id (str): The ID of the room.

    Returns:
    JSON: The daily energy consumption for the specified room.
    """
    user_id = get_jwt_identity()
    return get_room_daily_energy(user_id,room_id)

@energy_views.route('/total_energy/daily', methods=['GET'])
@jwt_required()
def total_daily_energy_route():
    """
    Endpoint to retrieve the daily total energy consumption for the user.

    Returns:
    JSON: The daily total energy consumption for the user.
    """
    user_id = get_jwt_identity()
    return get_total_daily_energy(user_id)
# __________________________________________________________________

@energy_views.route('/appliance_energy/weekly/<appliance_id>', methods=['GET'])
@jwt_required()
def appliance_weekly_energy_route(appliance_id):
    """
    Endpoint to retrieve the weekly energy consumption for a specific appliance.

    Parameters:
    - appliance_id (str): The ID of the appliance.

    Returns:
    JSON: The weekly energy consumption for the specified appliance.
    """
    user_id = get_jwt_identity()
    return get_appliance_weekly_energy(user_id,appliance_id)

@energy_views.route('/appliance_energy/monthly/<appliance_id>', methods=['GET'])
@jwt_required()
def appliance_monthly_energy_route(appliance_id):
    """
    Endpoint to retrieve the monthly energy consumption for a specific appliance.

    Parameters:
    - appliance_id (str): The ID of the appliance.

    Returns:
    JSON: The monthly energy consumption for the specified appliance.
    """
    user_id = get_jwt_identity()
    return get_appliance_monthly_energy(user_id,appliance_id)

@energy_views.route('/appliance_energy/yearly/<appliance_id>', methods=['GET'])
@jwt_required()
def appliance_yearly_energy_route(appliance_id):
    """
    Endpoint to retrieve the yearly energy consumption for a specific appliance.

    Parameters:
    - appliance_id (str): The ID of the appliance.

    Returns:
    JSON: The yearly energy consumption for the specified appliance.
    """
    user_id = get_jwt_identity()
    return get_appliance_yearly_energy(user_id,appliance_id)
# _____________________________________________________________

@energy_views.route('/room_energy/weekly/<room_id>', methods=['GET'])
@jwt_required()
def room_weekly_energy_route(room_id):
    """
    Endpoint to retrieve the weekly energy consumption for a specific room.

    Parameters:
    - room_id (str): The ID of the room.

    Returns:
    JSON: The weekly energy consumption for the specified room.
    """
    user_id = get_jwt_identity()
    return get_room_weekly_energy(user_id,room_id)

@energy_views.route('/room_energy/monthly/<room_id>', methods=['GET'])
@jwt_required()
def room_monthly_energy_route(room_id):
    """
    Endpoint to retrieve the monthly energy consumption for a specific room.

    Parameters:
    - room_id (str): The ID of the room.

    Returns:
    JSON: The monthly energy consumption for the specified room.
    """
    user_id = get_jwt_identity()
    return get_room_monthly_energy(user_id,room_id)

@energy_views.route('/room_energy/yearly/<room_id>', methods=['GET'])
@jwt_required()
def room_yearly_energy_route(room_id):
    """
    Endpoint to retrieve the yearly energy consumption for a specific room.

    Parameters:
    - room_id (str): The ID of the room.

    Returns:
    JSON: The yearly energy consumption for the specified room.
    """
    user_id = get_jwt_identity()
    return get_room_yearly_energy(user_id,room_id)
# _______________________________________________________________

@energy_views.route('/total_energy/weekly', methods=['GET'])
@jwt_required()
def total_weekly_energy_route():
    """
    Endpoint to retrieve the weekly total energy consumption for the user.

    Returns:
    JSON: The weekly total energy consumption for the user.
    """
    user_id = get_jwt_identity()
    return get_total_weekly_energy(user_id)

@energy_views.route('/total_energy/monthly', methods=['GET'])
@jwt_required()
def total_monthly_energy_route():
    """
    Endpoint to retrieve the monthly total energy consumption for the user.
    Returns:
    JSON: The monthly total energy consumption for the user.
    """
    user_id = get_jwt_identity()
    return get_total_monthly_energy(user_id)

@energy_views.route('/total_energy/yearly', methods=['GET'])
@jwt_required()
def total_yearly_energy_route():
    """
    Endpoint to retrieve the yearly total energy consumption for the user.
    Returns:
    JSON: The yearly total energy consumption for the user.
    """
    user_id = get_jwt_identity()
    return get_total_yearly_energy(user_id)


@energy_views.route('/past_month_total_energy', methods=['GET'])
@jwt_required()
def get_past_month_energy_route():
    """
    Endpoint to retrieve the past month total energy.
    Returns:
    JSON: The past month total energy for the user.
    """
    user_id = get_jwt_identity()
    return get_past_month_energy(user_id)



@energy_views.route('/current_month_total_energy', methods=['GET'])
@jwt_required()
def get_current_month_energy_route():
    """
    Endpoint to retrieve the current month total energy.
    Returns:
    JSON: The current month total energy for the user.
    """
    user_id = get_jwt_identity()
    return get_current_month_energy(user_id)


