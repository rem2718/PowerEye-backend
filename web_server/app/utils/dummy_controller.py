from flask import jsonify
from app import cloud

def test_verify_credentials():
    user = {
        'id': 1,
        'email': 'mayakhalide2001@gmail.com',
        'password': 'smarthomemaya'
    }
    plug_type = 'meross'
   
    result = cloud.verify_credentials(plug_type, user)
    return jsonify({'result': cloud})
   