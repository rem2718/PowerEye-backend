from flask import session
from app.utils.dummy_controller import *
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
    return test_verify_credentials_meross()

@app.route('/smartplugs')
def smartplugs():
    return test_smartplugs_meross()

@app.route('/switch')
def switch():
    return test_switch_meross()
