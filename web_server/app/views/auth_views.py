from flask import request
from app.controllers.auth_controller import login, signup, logout
from app import app

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
