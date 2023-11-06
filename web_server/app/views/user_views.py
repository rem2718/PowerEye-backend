# app\views\user_views.py
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.user_controller import *
from app.utils.img_sys import *
from werkzeug.utils import secure_filename
import os

# Create a Blueprint to organize routes
user_views = Blueprint('user_views', __name__)

# Define routes using the imported functions
@user_views.route('/signup', methods=['POST'])
def signup_route():
    data = request.get_json()
    email = data['email']
    power_eye_password = data['power_eye_password']
    cloud_password = data['cloud_password']
    return signup(email, power_eye_password, cloud_password)

@user_views.route('/login', methods=['POST'])
def login_route():
    data = request.get_json()
    email = data['email']
    password = data['password']
    return login(email, password)

@user_views.route('/logout', methods=['POST'])
@jwt_required()
def logout_route():
    return logout()

@user_views.route('/user', methods=['GET'])
@jwt_required()
def get_user_info_route():
    user_id = get_jwt_identity()
    return get_user_info(user_id)

@user_views.route('/user', methods=['PUT'])
@jwt_required()
def update_user_info_route():
    user_id = get_jwt_identity()
    data = request.get_json()
    meross_password = data.get('meross_password')
    power_eye_password = data.get('power_eye_password')
    username = data.get('username')
    profile_picture = data.get('profile_picture')
    return update_user_info(user_id, meross_password, power_eye_password, username, profile_picture)

@user_views.route('/user', methods=['DELETE'])
@jwt_required()
def delete_user_route():
    user_id = get_jwt_identity()
    return delete_user(user_id)

@user_views.route('/goal', methods=['GET'])
@jwt_required()
def get_goal_route():
    user_id = get_jwt_identity()
    return get_goal(user_id)

@user_views.route('/goal', methods=['POST'])
@jwt_required()
def set_goal_route():
    user_id = get_jwt_identity()
    data = request.get_json()
    energy = data['energy_goal']
    return set_goal(user_id,energy)

@user_views.route('/goal', methods=['DELETE'])
@jwt_required()
def delete_goal_route():
    user_id = get_jwt_identity()
    return delete_goal(user_id)

@user_views.route('/profile-pic', methods=["GET", "POST"])
@jwt_required()
def upload_profile_pic():
    user_id = get_jwt_identity()
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file extension'}), 400

        # Generate a unique filename to avoid conflicts
        filename = secure_filename(file.filename)
        #generates the full file path by appending the UPLOADS_FOLDER and filename together, 
        # ensuring that the correct path is formed regardless of the operating system using(/ or \)
        save_path = os.path.join(UPLOADS_FOLDER, filename)

        #save the uploaded profile picture file to the file system.
        try:
            file.save(save_path)
            return jsonify({'message': 'Profile picture uploaded successfully', 'user_id': user_id})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'GET':
        filename = request.args.get('filename')
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400

        try:
            return send_from_directory(UPLOADS_FOLDER, filename)
        except FileNotFoundError:
            return jsonify({'error': 'Profile picture not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500



