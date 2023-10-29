from flask import Blueprint, request, jsonify
from app.controllers.appliance_controller import *

# Create a Blueprint to organize your routes
appliance_views = Blueprint('appliance_views', __name__)

# Define routes using the imported functions
@appliance_views.route('/add_appliance', methods=['POST'])
def add_appliance_route():
    data = request.get_json()
    user_id = data['user_id']
    name = data['name']
    cloud_id = data['cloud_id']
    type = data['type']
    return add_appliance(user_id, name, cloud_id, type)

@appliance_views.route('/get_appliance/<user_id>/<appliance_id>', methods=['GET'])
def get_appliance_by_id_route(user_id, appliance_id):
    return get_appliance_by_id(user_id, appliance_id)

@appliance_views.route('/get_all_appliances/<user_id>', methods=['GET'])
def get_all_appliances_route(user_id):
    return get_all_appliances(user_id)

@appliance_views.route('/delete_appliance/<user_id>/<appliance_id>', methods=['DELETE'])
def delete_appliance_route(user_id, appliance_id):
    return delete_appliance(user_id, appliance_id)

@appliance_views.route('/update_appliance_name/<user_id>/<appliance_id>', methods=['PUT'])
def update_appliance_name_route(user_id, appliance_id):
    data = request.get_json()
    new_name = data['new_name']
    return update_appliance_name(user_id, appliance_id, new_name)

@appliance_views.route('/switch_appliance/<user_id>/<appliance_id>', methods=['PUT'])
def switch_appliance_route(user_id, appliance_id):
    data = request.get_json()
    status = data['status']
    return switch_appliance(user_id, appliance_id, status)