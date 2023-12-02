"""
Module: power_views

This module defines Flask routes related to power consumption readings.

Each route corresponds to a specific functionality related to power consumption readings,
such as retrieving the most recent power reading for a specific appliance.

Routes:
- GET /get_most_recent_reading/<appliance_id>: Get the most recent power reading for an appliance.
"""
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.power_controller import get_most_recent_reading




# Create a Blueprint to organize  routes
power_views = Blueprint('power_views', __name__)

# Define routes using the imported functions
@power_views.route('/get_most_recent_reading/<appliance_id>', methods=['GET'])
@jwt_required()
def get_most_recent_reading_route(appliance_id):
    """
    Endpoint to retrieve the most recent reading power for a specific appliance.

    Parameters:
    - appliance_id (str): The ID of the appliance.

    Returns:
    JSON: The most recent reading for the specified appliance.
    """
    user_id = get_jwt_identity()
    return get_most_recent_reading(user_id, appliance_id)
