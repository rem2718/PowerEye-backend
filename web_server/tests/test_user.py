# from flask import Flask
# import json
# from mongoengine import connect
# from app.controllers.user_controller import *

# # Define a default connection
# connect(db='flask_test_database', host='mongodb+srv://219410523:Maya2001@hems.kcuurlg.mongodb.net/flask_test_database')

# # Create Flask app and push context
# app = Flask(__name__)
# app.config['DEBUG'] = True  # Set DEBUG mode
# app.app_context().push()

# def test_signup():
#         email = "test77@example.com"
#         power_eye_password = "TestPassword1253!"
#         meross_password = "MerossPassword1253!"

#         response, status_code = signup(email, power_eye_password, meross_password)

#         # Assuming response is a Flask response object
#         response_content = response.get_json()

#         # Format the JSON content with indentation
#         formatted_response = json.dumps(response_content, indent=4)

#         # Print the formatted response
#         print(formatted_response)

# if __name__ == "__main__":  
#     test_signup()
