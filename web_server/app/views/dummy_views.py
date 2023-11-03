from flask import session
from app.utils.dummy_controller import test_verify_credentials_tuya, test_smartplugs_tuya
from flask import Blueprint
from markupsafe import escape

dummy_views = Blueprint("dummy", __name__)

@dummy_views.route('/')
def index():
    if 'user' in session:
        return 'Logged in as %s' % escape(session['user'])
    return 'You are not logged in'

@dummy_views.route('/verify')
def verify():
    return test_verify_credentials_tuya()

@dummy_views.route('/smartplugs')
def smartplugs():
    return test_smartplugs_tuya()

# @app.route('/logout')
# def logout():
#     session.pop('user', None)  # Remove the 'user' key from the session
#     return jsonify({'message': 'Logged out successfully'})