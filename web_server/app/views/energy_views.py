# app\views\energy_views.py
from flask import Blueprint, jsonify, request
from app.controllers.energy_controller import *
from flask_jwt_extended import jwt_required, get_jwt_identity


# Create a Blueprint to organize routes
energy_views = Blueprint('energy_views', __name__)


@energy_views.route('/appliance_energy/weekly', methods=['GET']) 
@jwt_required()
def appliance_weekly_energy_route():
    user_id = get_jwt_identity()
    return get_appliance_weekly_energy(user_id)

@energy_views.route('/appliance_energy/monthly', methods=['GET']) 
@jwt_required()
def appliance_monthly_energy_route():
    user_id = get_jwt_identity()
    return get_appliance_monthly_energy(user_id)


@energy_views.route('/appliance_energy/yearly', methods=['GET']) 
@jwt_required()
def appliance_yearly_energy_route():
    user_id = get_jwt_identity()
    return get_appliance_yearly_energy(user_id)

@energy_views.route('/room_energy/weekly', methods=['GET']) 
@jwt_required()
def room_weekly_energy_route():
    user_id = get_jwt_identity()
    return get_room_weekly_energy(user_id)

@energy_views.route('/room_energy/monthly', methods=['GET']) 
@jwt_required()
def room_monthly_energy_route():
    user_id = get_jwt_identity()
    return get_room_monthly_energy(user_id)



@energy_views.route('/room_energy/yearly', methods=['GET']) 
@jwt_required()
def room_yearly_energy_route():
    user_id = get_jwt_identity()
    return get_room_yearly_energy(user_id)



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