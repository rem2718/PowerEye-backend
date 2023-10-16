# app\controllers\appliance_controller.py
from flask import jsonify
from app.models.appliance_model import Appliance


def add_appliance(name, cloud_id, type):
    appliance = Appliance(
        name=name,
        cloud_id=cloud_id,
        # e_type=e_type,
        # connection_status=True,
        baseline_threshold=-1,
    )
    appliance.save()
    return jsonify({'message': 'Appliance added successfully'}), 201

def switch_appliance(id, status):
    appliance = Appliance.query.get(id)
    appliance.status = status
    appliance.save()
    return jsonify({'message': 'Appliance status updated successfully'}), 200

def delete_appliance(id):
    # Delete appliance logic
    # Do not forget to delete the appliance from the rooms as well
    return jsonify({'message': 'Appliance deleted successfully'}), 200

def get_power(id):
    # Get power information logic
    return jsonify({'power': ''}), 200
