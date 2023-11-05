#app\views\energy_views.py
from flask import Flask, Blueprint, jsonify
from app.controllers.energy_controller import *

# Create a Blueprint to organize your routes
energy_views = Blueprint('energy_views', __name__)

@energy_views.route('/appliance_energy/<user_id>/<appliance_id>/<string:timeframe>/<int:time_since_current>', methods=['GET']) 
def appliance_energy_route(user_id, appliance_id, timeframe, time_since_current):
    valid_timeframes = ["daily", "weekly", "monthly", "yearly"]

    #lower() --> allows the route to handle timeframes specified in any case (e.g., "Daily", "daily", "DAILY")
    if timeframe.lower() in valid_timeframes:
        return get_appliance_energy(user_id, appliance_id, time_since_current, timeframe.lower())
    else:
        return jsonify({'error': 'Invalid timeframe specified'})

@energy_views.route('/room_energy/<user_id>/<room_id>/<string:timeframe>/<int:time_since_current>', methods=['GET']) 
def room_energy_route(user_id, room_id, timeframe, time_since_current):
    valid_timeframes = ["daily", "weekly", "monthly", "yearly"]

    if timeframe.lower() in valid_timeframes:
        return get_room_energy(user_id, room_id, time_since_current, timeframe.lower())
    else:
        return jsonify({'error': 'Invalid timeframe specified'})

@energy_views.route('/total_energy/<user_id>/<string:timeframe>/<int:time_since_current>', methods=['GET'])
def total_energy_route(user_id, timeframe, time_since_current):
    valid_timeframes = ["daily", "weekly", "monthly", "yearly"]

    if timeframe.lower() in valid_timeframes:
        return get_total_energy(user_id, timeframe.lower(), time_since_current)
    else:
        return jsonify({'error': 'Invalid timeframe specified'})
    
