"""
Module: appliance_views

This module defines Flask routes related to user appliances.

Each route corresponds to a specific functionality related to user appliances,
such as adding a new appliance, retrieving information about an appliance, updating
appliance details, and more.

Routes:
- POST /appliance: Add a new appliance.
- GET /appliance/<appliance_id>: Retrieve information about a specific appliance.
- GET /get_all_appliances: Retrieve information about all user appliances.
- DELETE /delete_appliance/<appliance_id>: Delete a specific appliance.
- PUT /update_appliance_name/<appliance_id>: Update the name of a specific appliance.
- PUT /switch_appliance/<appliance_id>: Switch the status of a specific appliance.
- GET /smartplugs: Retrieve information about smart plugs.

Request and Response Formats:
The request and response formats for each route are documented in the respective route's docstring.
"""


from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.appliance_controller import (
    add_appliance,
    get_appliance_by_id,
    get_all_appliances,
    delete_appliance,
    update_appliance_name,
    switch_appliance,
    get_smartplugs,
)


# Create a Blueprint to organize  routes
appliance_views = Blueprint('appliance_views', __name__)

# Define routes using the imported functions
@appliance_views.route('/appliance', methods=['POST'])
@jwt_required()
def add_appliance_route():
    """
    Endpoint to add a new appliance for the user.

    Request Body:
    {
        "name": "My Appliance",
        "cloud_id": "cloud123",
        "type": "4"
    }

    Returns:
    JSON: Information about the added appliance.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get('name')
    cloud_id = data.get('cloud_id')
    type = data.get('type')
    return add_appliance(user_id, name, cloud_id, type)

@appliance_views.route('/appliance/<appliance_id>', methods=['GET'])
@jwt_required()
def get_appliance_by_id_route(appliance_id):
    """
    Endpoint to retrieve information about a specific appliance.

    Parameters:
    - appliance_id (str): The ID of the appliance.

    Returns:
    JSON: Information about the specified appliance.
    """
    user_id = get_jwt_identity()
    return get_appliance_by_id(user_id, appliance_id)

@appliance_views.route('/get_all_appliances', methods=['GET'])
@jwt_required()
def get_all_appliances_route():
    """
    Endpoint to retrieve information about all appliances for the user.

    Returns:
    JSON: Information about all user appliances.
    """
    user_id = get_jwt_identity()
    return get_all_appliances(user_id)

@appliance_views.route('/delete_appliance/<appliance_id>', methods=['DELETE'])
@jwt_required()
def delete_appliance_route(appliance_id):
    """
    Endpoint to delete a specific appliance.

    Parameters:
    - appliance_id (str): The ID of the appliance to be deleted.

    Returns:
    JSON: Confirmation of the deletion.
    """
    user_id = get_jwt_identity()
    return delete_appliance(user_id, appliance_id)

@appliance_views.route('/update_appliance_name/<appliance_id>', methods=['PUT'])
@jwt_required()
def update_appliance_name_route(appliance_id):
    """
    Endpoint to update the name of a specific appliance.

    Parameters:
    - appliance_id (str): The ID of the appliance to be updated.
    - new_name (str): The new name for the appliance.

    Request Body:
    {
        "new_name": "New Appliance Name"
    }

    Returns:
    JSON: Information about the updated appliance.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    new_name = data.get('new_name')
    return update_appliance_name(user_id, appliance_id, new_name)

@appliance_views.route('/switch_appliance/<appliance_id>', methods=['PUT'])
@jwt_required()
def switch_appliance_route(appliance_id):
    """
    Endpoint to switch the status of a specific appliance.

    Parameters:
    - appliance_id (str): The ID of the appliance to switch.
    - status (bool): The new status (True for ON, False for OFF).

    Request Body:
    {
        "status": true
    }

    Returns:
    JSON: Information about the updated status of the appliance.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    status = data.get('status')
    return switch_appliance(user_id, appliance_id, status)


@appliance_views.route('/smartplugs', methods=['GET'])
@jwt_required()
def get_smart_plugs():
    """
    Endpoint to retrieve information about not used smart plugs for the user.

    Returns:
    JSON: Information about smart plugs.
    """
    user_id = get_jwt_identity()
    return get_smartplugs(user_id)
