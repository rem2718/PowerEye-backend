from flask import session
from app.utils.dummy_controller import test_verify_credentials_tuya, test_smartplugs_tuya
from flask import Blueprint
from markupsafe import escape

app = Blueprint("main", __name__)

@app.route('/')
def index():
    if 'user' in session:
        return 'Logged in as %s' % escape(session['user'])
    return 'You are not logged in'

@app.route('/verify')
def verify():
    return test_verify_credentials_tuya()

@app.route('/smartplugs')
def smartplugs():
    return test_smartplugs_tuya()

# @app.route('/logout')
# def logout():
#     session.pop('user', None)  # Remove the 'user' key from the session
#     return jsonify({'message': 'Logged out successfully'})