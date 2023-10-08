# app\controllers\goal_controller.py
from flask import jsonify
from app.models.user_model import User

def get_user_info():
    # Get user information logic
    return jsonify({'username': 'JohnDoe', 'profile': 'profile_url', 'goal': '5000'}), 200

def update_user_info(username, password, meross_password, profile_pic):
    # Update user information logic
    return jsonify({'message': 'User info updated successfully'}), 200

def delete_user():
    # Delete user logic
    return jsonify({'message': 'User deleted successfully'}), 200


def get_goal():
    goal = Goal.query.first()
    return jsonify({'energy_goal': goal.energy}), 200

def set_goal(energy):
    goal = Goal(energy=energy)
    goal.save()
    return jsonify({'message': 'Goal set successfully'}), 201

def delete_goal():
    # Delete goal logic
    return jsonify({'message': 'Goal deleted successfully'}), 200
