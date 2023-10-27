# app\views\energy_views.py
from flask import Blueprint, jsonify, request
from app.controllers.energy_controller import *

# Create a Blueprint to organize your routes
energy_views = Blueprint('energy_views', __name__)

# Define routes using the imported functions

@energy_views.route('/appliance/daily/<time_since_current>', methods=['GET'])
def get_appliance_daily_energy_route(time_since_current):
    return get_appliance_daily_energy(time_since_current)

@energy_views.route('/appliance/weekly/<time_since_current>', methods=['GET'])
def get_appliance_weekly_energy_route(time_since_current):
    return get_appliance_weekly_energy(time_since_current)

@energy_views.route('/appliance/monthly/<time_since_current>', methods=['GET'])
def get_appliance_monthly_energy_route(time_since_current):
    return get_appliance_monthly_energy(time_since_current)

@energy_views.route('/appliance/yearly/<time_since_current>', methods=['GET'])
def get_appliance_yearly_energy_route(time_since_current):
    return get_appliance_yearly_energy(time_since_current)

@energy_views.route('/room/daily/<time_since_current>', methods=['GET'])
def get_room_daily_energy_route(time_since_current):
    return get_room_daily_energy(time_since_current)

@energy_views.route('/room/weekly/<time_since_current>', methods=['GET'])
def get_room_weekly_energy_route(time_since_current):
    return get_room_weekly_energy(time_since_current)

@energy_views.route('/room/monthly/<time_since_current>', methods=['GET'])
def get_room_monthly_energy_route(time_since_current):
    return get_room_monthly_energy(time_since_current)

@energy_views.route('/room/yearly/<time_since_current>', methods=['GET'])
def get_room_yearly_energy_route(time_since_current):
    return get_room_yearly_energy(time_since_current)

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
