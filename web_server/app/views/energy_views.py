# app\views\energy_views.py
from flask import Blueprint, jsonify, request
from app.controllers.energy_controller import *
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.enums import Timeframe


# Create a Blueprint to organize your routes
energy_views = Blueprint('energy_views', __name__)


@energy_views.route('/appliance_energy/<user_id>/<appliance_id>/<int:timeframe>/<int:time_since_current>', methods=['GET']) 
def appliance_energy_route(user_id, appliance_id, timeframe, time_since_current):
    try:
        timeframe_enum = Timeframe(timeframe)
    except ValueError:
        return jsonify({'error': 'Invalid timeframe specified'}), 400

    return get_energy(user_id, timeframe_enum, time_since_current, room_id=None, appliance_id=appliance_id)

@energy_views.route('/room_energy/<user_id>/<room_id>/<int:timeframe>/<int:time_since_current>', methods=['GET']) 
def room_energy_route(user_id, room_id, timeframe, time_since_current):
    try:
        timeframe_enum = Timeframe(timeframe)
    except ValueError:
        return jsonify({'error': 'Invalid timeframe specified'}), 400

    return get_energy(user_id, timeframe_enum, time_since_current, room_id=room_id, appliance_id=None)

@energy_views.route('/total_energy/<user_id>/<int:timeframe>/<int:time_since_current>', methods=['GET']) 
def total_energy_route(user_id, timeframe, time_since_current):
    try:
        timeframe_enum = Timeframe(timeframe)
    except ValueError:
        return jsonify({'error': 'Invalid timeframe specified'}), 400

    return get_energy(user_id, timeframe_enum, time_since_current, room_id=None, appliance_id=None)
