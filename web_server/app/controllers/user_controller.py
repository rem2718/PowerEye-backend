# app\controllers\user_controller.py
from flask import jsonify
from app.models.user_model import User,CloudType
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()



# Function to validate PowerEye system password
def validate_password(password):
    try:
        # Define complexity criteria
        if (
            len(password) < 8
            or not any(char.isupper() for char in password)
            or not any(char.islower() for char in password)
            or not any(char.isdigit() for char in password)
            or not any(char in '!@#$%^&*()-_+=<>,.?/:;{}[]~' for char in password)
        ):
            return False, jsonify({'message': 'Password should contain at least 8 characters, including at least one uppercase letter, one lowercase letter, one digit, and one special character'}), 400

        # Return True if the password meets the complexity criteria
        return True, None, None

    except Exception as e:
        return False, jsonify({'message': f'Error occurred while validating password: {str(e)}'}), 500
    
    
# Function to validate Meross credentials (email and password)
def validate_meross_credentials(email, password):
    try:
        # Implement validation using Meross interface
        # Return True if valid, False otherwise
        return True  # Placeholder, replace with actual validation logic

    except Exception as e:
        return False, jsonify({'message': f'Error occurred while validating Meross credentials: {str(e)}'}), 500


def signup(email, power_eye_password, meross_password):
    try:
        # Validate PowerEye system password
        is_valid_pass, error_response, status_code = validate_password(power_eye_password)
        if not is_valid_pass:
            return error_response, status_code

        # Validate Meross credentials
        if not validate_meross_credentials(email, meross_password):
            return jsonify({'error': 'Invalid Meross credentials.'}), 400

        # Check if the email is already associated with a non-deleted user
        existing_user = User.objects(email=email, is_deleted=False).first()
        if existing_user:
            return jsonify({'error': 'Email is already registered.'}), 400

        # Encrypt the Power Eye password
        hashed_password = bcrypt.generate_password_hash(power_eye_password).decode('utf-8')
        
        # Create and save the user
        user = User(
            email=email,
            password=hashed_password,
            cloud_password=meross_password,
        )
        user.save()

        return jsonify({'message': 'User created successfully.'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500



def login(email, password):
    try:
        # Validate if email is provided
        if not email:
            return jsonify({'error': 'Email is required.'}), 400

        # Validate if password is provided
        if not password:
            return jsonify({'error': 'Password is required.'}), 400

        # Find the user by email
        user = User.objects(email=email).first()

        if not user:
            return jsonify({'error': 'Invalid email or password.'}), 401

        # Validate the password
        if not user.check_password(password):
            return jsonify({'error': 'Invalid email or password.'}), 401

        # If email and password are valid, generate and return a token
        token = generate_token(user)
        
        return jsonify({'token': token}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def logout():
    return jsonify({'message': 'Logged out successfully.'}), 200


def get_user_info(user_id):
    try:
        # Find the user by ID
        user = User.objects(id=user_id).first()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        user_info = {
            'email': user.email,
            'username': user.username,
            'current_month_energy': user.current_month_energy,
            'energy_goal': user.energy_goal,
            # Add other user fields as needed
        }

        return jsonify({'user_info': user_info}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def update_user_info(user_id, meross_password=None, power_eye_password=None, username=None, profile_picture=None):
    try:
        # Find the user by ID
        user = User.objects(id=user_id).first()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Update user information if provided
        if meross_password is not None:
            user.cloud_password = meross_password

        if power_eye_password is not None:
            if not validate_power_eye_password(power_eye_password):
                return jsonify({'error': 'Invalid PowerEye system password.'}), 400
            user.password = power_eye_password

        if username is not None:
            user.username = username

        if profile_picture is not None:
            user.profile_picture = profile_picture

        user.save()

        return jsonify({'message': 'User information updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def delete_user(user_id):
    try:
        # Find the user by ID
        user = User.objects(id=user_id).first()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Soft delete the user
        user.is_deleted = True
        user.save()

        return jsonify({'message': 'User deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



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



def get_rooms():
    # Implementation details for retrieving a list of rooms
    rooms = Room.objects()
    room_list = [{'id': str(room.id), 'name': room.name, 'status': room.status} for room in rooms]
    return {'rooms': room_list}