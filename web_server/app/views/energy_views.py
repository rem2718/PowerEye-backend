# app\views\energy_views.py
# from app import app
from flask import request, session, jsonify
from app.utils.dummy_controller import test_verify_credentials_tuya, test_smartplugs_tuya
# from app.controllers.energy_controller import get_appliance_daily_energy, get_appliance_weekly_energy, get_appliance_monthly_energy,get_appliance_yearly_energy, get_room_daily_energy,get_room_weekly_energy,get_room_monthly_energy,get_room_yearly_energy, get_total_daily_energy, get_total_weekly_energy,get_total_monthly_energy, get_total_yearly_energy
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

# @app.route('/get_smartplugs')
# def getPlugs():
#     return test_get_smartplugs()

# @app.route('/logout')
# def logout():
#     session.pop('user', None)  # Remove the 'user' key from the session
#     return jsonify({'message': 'Logged out successfully'})

# @app.route('/energy/appliance/<string:timeframe>/<int:timeSinceCurrent>', methods=['GET']) 
# def appliance_energy_route(time_frame, time_since_current):
#     if time_frame == "Daily":
#         return get_appliance_daily_energy(time_since_current)
#     elif time_frame == "Weekly":
#         return get_appliance_weekly_energy(time_since_current)
#     elif time_frame == "Monthly":
#         return get_appliance_monthly_energy(time_since_current)
#     elif time_frame == "Yearly":
#         return get_appliance_yearly_energy(time_since_current)
#     else:
#         return {'error': 'Invalid timeframe specified'}

# @app.route('/energy/room/<string:timeframe>/<int:timeSinceCurrent>', methods=['GET']) 
# def room_energy_route(time_frame, time_since_current):
#     if time_frame == "Daily":
#         return get_room_daily_energy(time_since_current)
#     elif time_frame == "Weekly":
#         return get_room_weekly_energy(time_since_current)
#     elif time_frame == "Monthly":
#         return get_room_monthly_energy(time_since_current)
#     elif time_frame == "Yearly":
#         return get_room_yearly_energy(time_since_current)
#     else:
#         return {'error': 'Invalid timeframe specified'}

# @app.route('/energy/total/<string:timeframe>/<int:timeSinceCurrent>', methods=['GET'])  
# def total_energy_route(time_frame, time_since_current):
#     if time_frame == "Daily":
#         return get_total_daily_energy(time_since_current)
#     elif time_frame == "Weekly":
#         return get_total_weekly_energy(time_since_current)
#     elif time_frame == "Monthly":
#         return get_total_monthly_energy(time_since_current)
#     elif time_frame == "Yearly":
#         return get_total_yearly_energy(time_since_current)
#     else:
#         return {'error': 'Invalid timeframe specified'}