from flask import Blueprint, request, jsonify
from app.controllers.appliance_controller import *
from flask_jwt_extended import jwt_required, get_jwt_identity


# Create a Blueprint to organize your routes
appliance_views = Blueprint('appliance_views', __name__)

# Define routes using the imported functions
@appliance_views.route('/add_appliance', methods=['POST'])
@jwt_required()
def add_appliance_route():
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data['name']
    cloud_id = data['cloud_id']
    type = data['type']
    return add_appliance(user_id, name, cloud_id, type)

@appliance_views.route('/get_appliance/<appliance_id>', methods=['GET'])
@jwt_required()
def get_appliance_by_id_route(appliance_id):
    user_id = get_jwt_identity()
    return get_appliance_by_id(user_id, appliance_id)

@appliance_views.route('/get_all_appliances', methods=['GET'])
@jwt_required()
def get_all_appliances_route():
    user_id = get_jwt_identity()
    return get_all_appliances(user_id)

@appliance_views.route('/delete_appliance/<appliance_id>', methods=['DELETE'])
@jwt_required()
def delete_appliance_route(appliance_id):
    user_id = get_jwt_identity()
    return delete_appliance(user_id, appliance_id)

@appliance_views.route('/update_appliance_name/<appliance_id>', methods=['PUT'])
@jwt_required()
def update_appliance_name_route(appliance_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    new_name = data['new_name']
    return update_appliance_name(user_id, appliance_id, new_name)

@appliance_views.route('/switch_appliance/<appliance_id>', methods=['PUT'])
@jwt_required()
def switch_appliance_route(appliance_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    status = data['status']
    return switch_appliance(user_id, appliance_id, status)