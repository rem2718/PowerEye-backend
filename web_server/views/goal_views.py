from flask import request
from app.controllers.goal_controller import set_goal, get_goal, delete_goal
from app import app

@app.route('/goal', methods=['POST'])
def set_goal_route():
    energy = request.json.get('energy')
    return set_goal(energy)

@app.route('/goal', methods=['GET'])
def get_goal_route():
    return get_goal()

@app.route('/goal', methods=['DELETE'])
def delete_goal_route():
    return delete_goal()
