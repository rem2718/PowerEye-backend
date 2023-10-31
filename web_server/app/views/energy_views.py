# #app\views\energy_views.py
# from flask import request, session, jsonify
# from app.controllers.energy_controller import get_appliance_daily_energy, get_appliance_weekly_energy, get_appliance_monthly_energy,get_appliance_yearly_energy, get_room_daily_energy,get_room_weekly_energy,get_room_monthly_energy,get_room_yearly_energy, get_total_daily_energy, get_total_weekly_energy,get_total_monthly_energy, get_total_yearly_energy

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

# @energy_views.route('/total/daily/<time_since_current>', methods=['GET'])
# def get_total_daily_energy_route(time_since_current):
#     return get_total_daily_energy(time_since_current)

# @energy_views.route('/total/weekly/<time_since_current>', methods=['GET'])
# def get_total_weekly_energy_route(time_since_current):
#     return get_total_weekly_energy(time_since_current)

# @energy_views.route('/total/monthly/<time_since_current>', methods=['GET'])
# def get_total_monthly_energy_route(time_since_current):
#     return get_total_monthly_energy(time_since_current)

# @energy_views.route('/total/yearly/<time_since_current>', methods=['GET'])
# def get_total_yearly_energy_route(time_since_current):
#     return get_total_yearly_energy(time_since_current)
