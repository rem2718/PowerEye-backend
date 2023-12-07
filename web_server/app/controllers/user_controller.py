# app\controllers\user_controller.py
from flask import jsonify, request, send_file
from app.models.user_model import User
from app.models.room_model import Room
from app.models.notified_device_model import NotifiedDevice
from app.utils.enums import PlugType
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
from app.config import Config
from app.utils.cloud_interface import cloud
import traceback
from app.utils.image_sys import *
from werkzeug.utils import secure_filename
import mimetypes
import os
from mongoengine.errors import DoesNotExist


# Function to validate PowerEye system password
def validate_password(password):
    try:
        # Define complexity criteria
        if (
            len(password) < 8
            or not any(char.isupper() for char in password)
            or not any(char.islower() for char in password)
            or not any(char.isdigit() for char in password)
            or not any(char in "!@#$%^&*()-_+=<>,.?/:;{}[]~" for char in password)
        ):
            return (
                False,
                jsonify(
                    {
                        "message": "Password should contain at least 8 characters, including at least one uppercase letter, one lowercase letter, one digit, and one special character"
                    }
                ),
                400,
            )

        # Return True if the password meet the complexity criteria
        return True, None, None

    except Exception as e:
        traceback.print_exc()
        return (
            False,
            jsonify({"message": f"Error occurred while validating password: {str(e)}"}),
            500,
        )



def signup(email, power_eye_password, cloud_password):
    try:
        # Validate PowerEye system password
        is_valid_pass, error_response, status_code = validate_password(
            power_eye_password
        )
        if not is_valid_pass:
            return error_response, status_code

        # Validate Meross credentials

        cloud_user = {"email": email, "password": cloud_password}  # Create user object
        is_valid_meross, error_response, status_code = cloud.verify_credentials(
            PlugType.MEROSS, cloud_user
        )
        if not is_valid_meross:
            return error_response, status_code

        # Check if the email is already associated with a non-deleted user
        existing_user = User.objects(email=email, is_deleted=False).first()
        if existing_user:
            return jsonify({"error": "Email is already registered."}), 400

        # Encrypt the Power Eye password
        hashed_password = bcrypt.generate_password_hash(power_eye_password).decode(
            "utf-8"
        )

        # Create and save the user
        user = User(
            email=email,
            password=hashed_password,
            cloud_password=cloud_password,
            appliances=[],
        )

        user.save()

        # Return the ID of the newly created user
        return (
            jsonify({"message": "User created successfully.", "user_id": str(user.id)}),
            201,
        )

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def login(email, password):
    try:
        # Validate if email is provided
        if not email:
            return jsonify({"error": "Email is required."}), 400

        # Validate if password is provided
        if not password:
            return jsonify({"error": "Password is required."}), 400

        # Find the user by email
        user = User.objects(email=email, is_deleted=False).first()
        if not user:
            return jsonify({"error": "Invalid email or password."}), 401

        # Validate the password
        if not user.check_password(password):
            return jsonify({"error": "Invalid email or password."}), 401

        # If email and password are valid, generate and return a token
        token = user.generate_token()

        return jsonify({"token": token}), 200
    except DoesNotExist:
        return jsonify({"message": "User not found."}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def logout(user_id, device_id):
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return jsonify({"message": "User not found."}), 404

        # Check if the device_id already exists in the notified_devices list
        notified_device = next(
            (nd for nd in user.notified_devices if nd.device_id == device_id), None
        )

        if notified_device:
            # Remove the NotifiedDevice from the list
            user.notified_devices.remove(notified_device)

            # Save the user document with the updated notified_devices
            user.save()

            return jsonify({"message": "Logged out successfully"}), 200
        else:
            return jsonify({"message": "Device not found in notified devices list."}), 404

    except DoesNotExist:
        return jsonify({"message": "User not found."}), 404
    except Exception as e:
        traceback.print_exc()
        return (
            jsonify({"message": f"Error occurred while Logging out {str(e)}"}),
            500,
        )



def get_user_info(user_id):
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return jsonify({"message": "User not found."}), 404

        user_info = {
            "email": user.email,
            "username": user.username,
            "current_month_energy": user.current_month_energy,
            "energy_goal": user.energy_goal,
            # Add other user fields as needed
        }

        return jsonify({"user_info": user_info}), 200
    except DoesNotExist:
        return jsonify({"message": "User not found."}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def update_user_info(
    user_id, cloud_password=None, power_eye_password=None, username=None
):
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)

        if not user:
            return jsonify({"message": "User not found."}), 404

        # Update user information if provided
        if cloud_password is not None:
            # Validate Meross credentials
            cloud_user = {
                "email": user.email,
                "password": cloud_password,
            }  # Create user object
            is_valid_meross, error_response, status_code = cloud.verify_credentials(
                PlugType.MEROSS, cloud_user
            )
            if not is_valid_meross:
                return error_response, status_code
            user.cloud_password = cloud_password

        if power_eye_password is not None:
            is_valid_pass, error_response, status_code = validate_password(
                power_eye_password
            )
            if not is_valid_pass:
                return error_response, status_code


            hashed_password = bcrypt.generate_password_hash(power_eye_password).decode(
                "utf-8"
            )

            user.password = hashed_password


        if username is not None:
            user.username = username

        user.save()

        return jsonify({"message": "User information updated successfully"}), 200
    except DoesNotExist:
        return jsonify({"message": "User not found."}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def delete_user(user_id):
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)

        if not user:
            return jsonify({"message": "User not found."}), 404

        # Delete rooms associated with the user
        Room.objects(user_id=user.id).delete()

        # Soft delete the user
        user.is_deleted = True
        user.save()

        return jsonify({"message": "User deleted successfully"}), 200

    except DoesNotExist:
        return jsonify({"message": "User not found."}), 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def get_goal(user_id):
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)

        if not user:
            return jsonify({"message": "User not found."}), 404

        goal = user.energy_goal
        return jsonify({"energy_goal": goal}), 200

    except DoesNotExist:
        return jsonify({"message": "User not found."}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def set_goal(user_id, energy):
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)

        if not user:
            return jsonify({"message": "User not found."}), 404

        # Validate the energy input

        energy = float(energy)
        if energy < 0:
            return jsonify({"message": "Energy goal must be a positive value."}), 400

        # Check if the input is greater than or equal to the total energy cost incurred
        if energy < user.current_month_energy:
            return (
                jsonify(
                    {
                        "message": "Energy goal must be greater than or equal to the total energy cost incurred this month."
                    }
                ),
                400,
            )

        # Set the energy goal and save the user
        user.energy_goal = energy
        user.save()

        return jsonify({"message": "Goal set successfully"}), 201

    except ValueError:
        return jsonify({"message": "Energy goal must be a numeric value."}), 400
    except DoesNotExist:
        return jsonify({"message": "User not found."}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def delete_goal(user_id):
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return jsonify({"message": "User not found."}), 404

        user.energy_goal = None
        user.save()
        return jsonify({"message": "Goal deleted successfully"}), 200
    except DoesNotExist:
        return jsonify({"message": "User not found."}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def upload_profile_pic(user_id, file, filename_with_extension):
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)

        if not user:
            return jsonify({"message": "User not found."}), 404

        if not file:
            return jsonify({"error": "No image data provided"}), 400

        if not filename_with_extension:
            return jsonify({"error": "No filename provided"}), 400

        # Generate a unique filename to avoid conflicts
        filename = f"{user_id}.png"

        # Save the uploaded profile picture file to the file system.
        if save_base64_image(file, filename):
            return jsonify({"message": "Profile picture uploaded successfully"}), 200
        else:
            return jsonify({"error": "Failed to save profile picture"}), 500
    except DoesNotExist:
        return jsonify({"message": "User not found."}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def get_profile_pic(user_id):
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return jsonify({"message": "User not found."}), 404


        # Try all allowed extensions
        for extension in ALLOWED_EXTENSIONS:
            filename = f"{user_id}.{extension}"
            file_path = os.path.join(UPLOADS_FOLDER, filename)
            # Guess the mimetype of the file based on the file path
            mimetype, _ = mimetypes.guess_type(file_path)
            if mimetype:
                # If mimetype is available, return the file with the specified mimetype
                return jsonify({"image": file_to_base64(file_path)}), 200
            else:
                # If mimetype is not available, return the file without specifying a mimetype
                return jsonify({"image": file_to_base64(file_path)}), 200
    except FileNotFoundError:
        return jsonify({"error": "Profile picture not found"}), 404
    except DoesNotExist:
        return jsonify({"message": "User not found."}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def set_fcm_token(user_id, device_id, fcm_token):
    try:
        # Retrieve the user by ID and make sure they are not deleted
        user = User.objects.get(id=user_id, is_deleted=False)
        if not user:
            return jsonify({"message": "User not found."}), 404

        # Check if the device_id already exists in the notified_devices list
        notified_device = next(
            (nd for nd in user.notified_devices if nd.device_id == device_id), None
        )

        if notified_device:
            # Update the fcm_token for the existing device_id
            notified_device.fcm_token = fcm_token
        else:
            # Create a new Notified_Device and append it to the user's notified_devices list
            new_device = NotifiedDevice(device_id=device_id, fcm_token=fcm_token)
            user.notified_devices.append(new_device)

        # Save the user document with the updated/added notified_devices
        user.save()

        return jsonify({"message": "FCM token set successfully"}), 200

    except DoesNotExist:
        return jsonify({"message": "User not found."}), 404
    except Exception as e:
        traceback.print_exc()
        return (
            jsonify({"message": f"Error occurred while setting FCM token: {str(e)}"}),
            500,
        )
