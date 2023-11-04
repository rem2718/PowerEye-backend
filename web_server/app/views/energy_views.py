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

@energy_views.route('/energy/room/<string:timeframe>/<int:timeSinceCurrent>', methods=['GET']) 
def room_energy_route(time_frame, time_since_current):
    if time_frame == "Daily":
        return get_room_daily_energy(time_since_current)
    elif time_frame == "Weekly":
        return get_room_weekly_energy(time_since_current)
    elif time_frame == "Monthly":
        return get_room_monthly_energy(time_since_current)
    elif time_frame == "Yearly":
        return get_room_yearly_energy(time_since_current)
    else:
        return {'error': 'Invalid timeframe specified'}

@energy_views.route('/total/daily/<time_since_current>', methods=['GET'])
def get_total_daily_energy_route(time_since_current):
    return get_total_daily_energy(time_since_current)

@energy_views.route('/total/weekly/<time_since_current>', methods=['GET'])
def get_total_weekly_energy_route(time_since_current):
    return get_total_weekly_energy(time_since_current)

@energy_views.route('/total/monthly/<time_since_current>', methods=['GET'])
def get_total_monthly_energy_route(time_since_current):
    return get_total_monthly_energy(time_since_current)

@energy_views.route('/total/yearly/<time_since_current>', methods=['GET'])
def get_total_yearly_energy_route(time_since_current):
    return get_total_yearly_energy(time_since_current)
