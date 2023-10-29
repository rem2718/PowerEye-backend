from flask import Blueprint, request, jsonify
from app.controllers.appliance_controller import *

# Create a Blueprint to organize your routes
power_views = Blueprint('power_views', __name__)

# Define routes using the imported functions
@power_views.route('/get_most_recent_reading/<user_id>/<appliance_id>', methods=['GET'])
def get_most_recent_reading_route(user_id, appliance_id):
    return get_most_recent_reading(user_id, appliance_id)
