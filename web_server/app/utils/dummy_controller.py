from flask import jsonify, session, current_app
from app.utils.cloud_interface import cloud, PlugType
import os

# # Set the secret key if it's not already set
# if not current_app.secret_key:
#     current_app.secret_key = os.getenv('SECRET_KEY')

#Meross:
# def test_verify_credentials():
#     user = {
#         'id': '1',
#         'email': 'abodayehayat@yahoo.com',
#         'password': 'reem00'
#     }
#     plug_type = PlugType.MEROSS.value

#     print(f"User: {user}")
#     print(f"Plug type: {plug_type}")

#     result = cloud.verify_credentials(plug_type, user)
#     print(f"Verification result: {result}")

#     if result in session:
#          session['plug_type'] = plug_type # store plug_type in the session
#          session['user'] = user # store user data in the session

#     print(result)
#     print(cloud)
#     return jsonify({'result': result})

def test_verify_credentials_tuya():
    user = {
        'id': 'ward.najjar@yahoo.com',
        'dev1': 'bf16e0689159efb9c5xibt',
        'plug_type': PlugType.TUYA.value
    }
    # user = {
    #     'id': 'Qnadaff2@gmail.com',
    #     'dev1': '64d162ff93d44252699aa21d',
    #     'plug_type': PlugType.TUYA.value
    # }
    print(f"User: {user}")

    # Call the verify_credentials method for Tuya
    result = cloud.verify_credentials(PlugType.TUYA.value, user)
    print(f"Verification result: {result}")

    return jsonify({'User': result})

def test_smartplugs_tuya():
    user = {
        'id': 'ward.najjar@yahoo.com',
        'dev1': 'bf16e0689159efb9c5xibt',
        'plug_type': PlugType.TUYA
    }
    print(f"User: {user}")

    # Call the get_smartplugs method for Tuya
    result = cloud.get_smartplugs(PlugType.TUYA, user)
    print(f"Retreiving SmartPlugs result: {result}")

    return jsonify({'smartplugs': result})

# def test_get_smartplugs():
#     plug_type = PlugType.MEROSS.value
    
#     result = cloud.get_smartplugs(plug_type, user)
#     return str(result)
