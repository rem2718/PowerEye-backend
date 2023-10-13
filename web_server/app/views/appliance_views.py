from app import app
from flask import request
from app.controllers.appliance_controller import add_appliance, switch_appliance, delete_appliance, get_power, get_smartPlugs, get_appliances


@app.route('/smartplug', methods=['get'])
def get_smartPlugs_route():
    return get_smartPlugs()

@app.route('/appliance', methods=['get'])
def get_appliances_route():
    return get_appliances()


@app.route('/appliance', methods=['POST'])
def add_appliance_route():
    name = request.json.get('name')
    type = request.json.get('type')
    return add_appliance(name, type)

@app.route('/appliance/<int:id>', methods=['PUT'])
def switch_appliance_route(id):
    status = request.json.get('status')
    return switch_appliance(id, status)

@app.route('/appliance/<int:id>', methods=['DELETE'])
def delete_appliance_route(id):
    return delete_appliance(id)

@app.route('/power/<int:id>', methods=['GET'])
def get_power_route(id):
    return get_power(id)
