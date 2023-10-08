from flask import request
from app.controllers.user_controller import update_user_info, delete_user, get_user_info, user_logout
from app import app

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


