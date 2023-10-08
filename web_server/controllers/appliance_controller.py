# app\controllers\appliance_controller.py
from flask import jsonify
from app.models.appliance_model import Appliance


# May be added to user, not here 
# def get_smartPlugs():
#     pass

# def get_appliances():
#     pass    

def add_appliance(name, type):
    appliance = Appliance(name=name, type=type)
    appliance.save()
    return jsonify({'message': 'Appliance added successfully'}), 201

def switch_appliance(id, status):
    appliance = Appliance.query.get(id)
    appliance.status = status
    appliance.save()
    return jsonify({'message': 'Appliance status updated successfully'}), 200

def delete_appliance(id):
    # Delete appliance logic
    return jsonify({'message': 'Appliance deleted successfully'}), 200

def get_power(id):
    # Get power information logic
    return jsonify({'power': ''}), 200
