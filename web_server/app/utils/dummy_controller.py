from flask import jsonify, session, current_app
from app.utils.cloud_interface import cloud, PlugType
import os

# # Set the secret key if it's not already set
# if not current_app.secret_key:
#     current_app.secret_key = os.getenv('SECRET_KEY')

#Meross:
def test_verify_credentials_meross():
    user = {
        'id': '1',
        'email': 'abodayehayat@yahoo.com',
        'password': 'reem00'
    }
    plug_type = PlugType.MEROSS

    print(f"User: {user}")
    print(f"Plug type: {plug_type}")

    result = cloud.verify_credentials(plug_type, user)
    print(f"Verification result: {result}")

    print(result)
    print(cloud)
    return jsonify({'result': result})

def test_smartplugs_meross():
    user = {
        'id': '1',
        'email': 'abodayehayat@yahoo.com',
        'password': 'reem00'
    }
    print(f"User: {user}")

    # Call the get_smartplugs method for Tuya
    result = cloud.get_smartplugs(PlugType.MEROSS, user)
    print(f"Retreiving SmartPlugs result: {result}")

    return jsonify({'smartplugs': result})

def test_switch_meross():
    user = {
        'id': '1',
        'email': 'abodayehayat@yahoo.com',
        'password': 'reem00'
    }
    app_id ='2208110334744551070548e1e9a13839' 
    status = True
    
    print(f"User: {user}, app_id: {app_id}, status: {status}")

    # Call the get_smartplugs method for Tuya
    result = cloud.switch(PlugType.MEROSS, user, app_id, status)
    print(f"Switch Status: {result}")

    return jsonify({'Switch Status': result})

def test_verify_credentials_tuya():
    user = {
        'id': 'ward.najjar@yahoo.com',
        'dev1': 'bf16e0689159efb9c5xibt',
    }
    print(f"User: {user}")

    # Call the verify_credentials method for Tuya
    result = cloud.verify_credentials(PlugType.TUYA, user)
    print(f"Verification result: {result}")

    return jsonify({'User': result})

def test_smartplugs_tuya():
    user = {
        'id': 'ward.najjar@yahoo.com',
        'dev1': 'bf16e0689159efb9c5xibt',
    }
    print(f"User: {user}")

    # Call the get_smartplugs method for Tuya
    result = cloud.get_smartplugs(PlugType.TUYA, user)
    print(f"Retreiving SmartPlugs result: {result}")

    return jsonify({'smartplugs': result})

def test_switch_tuya():
    user = {
        'id': 'ward.najjar@yahoo.com',
        'dev1': 'bf16e0689159efb9c5xibt'
    }
    app_id ='bf16e0689159efb9c5xibt' 
    status = True
    
    print(f"User: {user}, app_id: {app_id}, status: {status}")

    # Call the get_smartplugs method for Tuya
    result = cloud.switch(PlugType.TUYA, user, app_id, status)
    print(f"Switch Status: {result}")

    return jsonify({'Switch Status': result})

   