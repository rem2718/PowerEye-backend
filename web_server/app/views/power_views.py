from flask import Blueprint
from app.controllers.power_controller import *
from flask_jwt_extended import jwt_required, get_jwt_identity


# Create a Blueprint to organize  routes
power_views = Blueprint('power_views', __name__)

# Define routes using the imported functions
@power_views.route('/get_most_recent_reading/<appliance_id>', methods=['GET'])
@jwt_required()
def get_most_recent_reading_route(appliance_id):
    user_id = get_jwt_identity()
    return get_most_recent_reading(user_id, appliance_id)
