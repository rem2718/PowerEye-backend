from flask import session
from app.utils.dummy_controller import *
from flask import Blueprint
from markupsafe import escape

dummy_views = Blueprint("dummy_views", __name__)

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

@dummy_views.route('/switch')
def switch():
    return test_switch_tuya()
