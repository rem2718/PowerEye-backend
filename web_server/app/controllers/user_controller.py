# app\controllers\goal_controller.py
from flask import jsonify
from app.models.user_model import User
from app.forms.login_form import LoginForm
from app.forms.signup_form import SignupForm


from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()




def login(email, password):
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            token = user.generate_token()
            return jsonify({'token': token}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401

    return jsonify({'message': 'Invalid form submission'}), 400

def signup(email, password, meross_password):
    form = SignupForm()  # Create an instance of the SignupForm

    if form.validate_on_submit():
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # Hash the password
        meross_password = form.meross_password.data

        user = User(email=email, password=password, meross_password=meross_password)
        user.save()
        token = user.generate_token()
        return jsonify({'token': token}), 201

    return jsonify({'message': 'Invalid form submission'}), 400

def logout():
    return jsonify({'message': 'Logout successful'}), 200




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


def get_appliances():
    pass    

def get_rooms():
    # Implementation details for retrieving a list of rooms
    rooms = Room.objects()
    room_list = [{'id': str(room.id), 'name': room.name, 'status': room.status} for room in rooms]
    return {'rooms': room_list}