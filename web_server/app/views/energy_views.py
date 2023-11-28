# app\views\energy_views.py
from flask import Blueprint
from app.controllers.energy_controller import *
from flask_jwt_extended import jwt_required, get_jwt_identity


# Create a Blueprint to organize routes
energy_views = Blueprint('energy_views', __name__)


@energy_views.route('/appliance_energy/daily/<appliance_id>', methods=['GET']) 
@jwt_required()
def appliance_daily_energy_route(appliance_id):
    user_id = get_jwt_identity()
    return get_appliance_daily_energy(user_id,appliance_id)


@energy_views.route('/room_energy/daily/<room_id>', methods=['GET']) 
@jwt_required()
def room_daily_energy_route(room_id):
    user_id = get_jwt_identity()
    return get_room_daily_energy(user_id,room_id)


@energy_views.route('/total_energy/daily', methods=['GET']) 
@jwt_required()
def total_daily_energy_route():
    user_id = get_jwt_identity()
    return get_total_daily_energy(user_id)

# __________________________________________________________________

@energy_views.route('/appliance_energy/weekly/<appliance_id>', methods=['GET']) 
@jwt_required()
def appliance_weekly_energy_route(appliance_id):
    user_id = get_jwt_identity()
    return get_appliance_weekly_energy(user_id,appliance_id)

@energy_views.route('/appliance_energy/monthly/<appliance_id>', methods=['GET']) 
@jwt_required()
def appliance_monthly_energy_route(appliance_id):
    user_id = get_jwt_identity()
    return get_appliance_monthly_energy(user_id,appliance_id)


@energy_views.route('/appliance_energy/yearly/<appliance_id>', methods=['GET']) 
@jwt_required()
def appliance_yearly_energy_route(appliance_id):
    user_id = get_jwt_identity()
    return get_appliance_yearly_energy(user_id,appliance_id)

# ______________________________________________________________

@energy_views.route('/room_energy/weekly/<room_id>', methods=['GET']) 
@jwt_required()
def room_weekly_energy_route(room_id):
    user_id = get_jwt_identity()
    return get_room_weekly_energy(user_id,room_id)

@energy_views.route('/room_energy/monthly/<room_id>', methods=['GET']) 
@jwt_required()
def room_monthly_energy_route(room_id):
    user_id = get_jwt_identity()
    return get_room_monthly_energy(user_id,room_id)



@energy_views.route('/room_energy/yearly/<room_id>', methods=['GET']) 
@jwt_required()
def room_yearly_energy_route(room_id):
    user_id = get_jwt_identity()
    return get_room_yearly_energy(user_id,room_id)

# _______________________________________________________________

@energy_views.route('/total_energy/weekly', methods=['GET']) 
@jwt_required()
def total_weekly_energy_route():
    user_id = get_jwt_identity()
    return get_total_weekly_energy(user_id)


@energy_views.route('/total_energy/monthly', methods=['GET']) 
@jwt_required()
def total_monthly_energy_route():
    user_id = get_jwt_identity()
    return get_total_monthly_energy(user_id)


@energy_views.route('/total_energy/yearly', methods=['GET']) 
@jwt_required()
def total_yearly_energy_route():
    user_id = get_jwt_identity()
    return get_total_yearly_energy(user_id)