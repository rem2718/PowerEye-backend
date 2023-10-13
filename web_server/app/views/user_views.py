from app import app
from flask import request
from app.controllers.user_controller import login, signup, logout,update_user_info, delete_user, get_user_info,set_goal, get_goal,delete_goal,get_rooms,get_appliances


@app.route('/user/login', methods=['POST'])
def login_route():
    email = request.json.get('email')
    password = request.json.get('password')
    return login(email, password)

@app.route('/user/signup', methods=['POST'])
def signup_route():
    email = request.json.get('email')
    password = request.json.get('password')
    meross_password = request.json.get('meross_password')
    return signup(email, password, meross_password)

@app.route('/user/logout', methods=['GET'])
def logout_route():
    return logout()


@app.route('/user/info', methods=['GET'])
def get_user_info_route():
    return get_user_info()

@app.route('/user/info', methods=['PUT'])
def update_user_info_route():
    username = request.json.get('username')
    password = request.json.get('password')
    meross_password = request.json.get('meross_password')
    profile_pic = request.json.get('profile_pic')
    return update_user_info(username, password, meross_password, profile_pic)

@app.route('/user/delete', methods=['DELETE'])
def delete_user_route():
    return delete_user()


@app.route('/user/goal', methods=['POST'])
def set_goal_route():
    energy = request.json.get('energy')
    return set_goal(energy)

@app.route('/user/goal', methods=['GET'])
def get_goal_route():
    return get_goal()

@app.route('/user/goal', methods=['DELETE'])
def delete_goal_route():
    return delete_goal()


@app.route('/user/rooms', methods=['GET'])
def get_rooms():
    return get_rooms()


@app.route('/user/appliances', methods=['GET'])
def get_appliances():
    return get_appliances()