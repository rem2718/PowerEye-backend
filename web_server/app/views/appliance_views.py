from app import app
from flask import Blueprint, request, jsonify
from app.controllers.appliance_controller import add_appliance, delete_appliance, get_most_recent_reading, update_appliance, get_appliances, switch_appliance


# Create a Blueprint for appliances
# appliance_bp = Blueprint('appliance', __name__)

# @app.route('/smartplug', methods=['get'])
# def get_smartPlugs_route():
#     return get_smartPlugs()

@app.route('/add_appliance', methods=['POST'])
def add_appliance_route():
    return add_appliance(
        request.json.get('user_id'),
        request.json.get('name'),
        request.json.get('cloud_id'),
        request.json.get('type')
    )
    
@app.route('/get_appliances/<user_id>', methods=['GET'])
def get_appliances_route(user_id):
    return get_appliances(user_id)

@app.route('/delete_appliance/<user_id>/<appliance_id>', methods=['DELETE'])
def delete_appliance_route(user_id, appliance_id):
    return delete_appliance(user_id, appliance_id)

@app.route('/update_appliance/<user_id>/<appliance_id>', methods=['PUT'])
def update_appliance_route(user_id, appliance_id):
    return update_appliance(
        user_id,
        appliance_id,
        request.json.get('name')
    )
    
@app.route('/get_most_recent_reading/<user_id>/<appliance_id>', methods=['GET'])
def get_most_recent_reading_route(user_id, appliance_id):
    return get_most_recent_reading(user_id, appliance_id)

# @app.route('/switch_appliance/<user_id>/<appliance_id>/<status>', methods=['PUT'])
# def switch_appliance_route(user_id, appliance_id, status):
#     return switch_appliance(user_id, appliance_id, status)