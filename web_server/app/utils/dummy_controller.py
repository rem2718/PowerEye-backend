from run import cloud_obj
from flask import Blueprint, jsonify

dummy_controller = Blueprint('dummy_controller', __name__)

@dummy_controller.route('/verify')
def verify_credentials():
    # Dummy user information for verification
    user = {
        'id': 1,
        'email': 'mayakhalide2001@gmail.com',
        'password': 'smarthomemaya'
    }

    # Call the verification method
    result = cloud_obj.verify_credentials('meross', user)

    return jsonify({'result': result})