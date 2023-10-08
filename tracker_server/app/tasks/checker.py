from datetime import datetime, timedelta
from bson import ObjectId
import pickle

from app.recommender import Recommender as PR
from app.types_classes import NotifType, EType
from app.interfaces.task import Task

class Checker(Task):
    shiftable = [EType.SHIFTABLE.value, EType.PHANTOM.value]
    hour = timedelta(hours=1)
    peak_start = 13
    peak_end = 17
    
    def __init__(self, id, db, fcm, additional=None):
        self.user_id = id
        self.db = db
        self.fcm = fcm
        self.goal_flags = {i:True for i in range(25, 225, 25)} 
        self.peak_flags = {} 
        self.phantom_flags = {} 
        self.baseline_flags = {} 
            
    def _get_apps(self, appliances):
        apps = {
            str(app['_id']):{
                'name': app['name'], 
                'e_type': app['e_type'], 
                'energy': app['energy'],
                'status': app['status'], 
                'threshold': app['baseline_threshold']
                } 
            for app in appliances 
            if not app['is_deleted']}
        return apps 
    
    def _get_powers(self, apps):
        projection = {key:1 for key, value in apps.items() if value['e_type'] == EType.PHANTOM.value}
        projection['_id'] = 0
        if len(projection):
            return self.db.get_doc('Powers_test', {'user': ObjectId(self.user_id)}, projection=projection, sort=[("timestamp", -1)])
        else:
            return {}
        
    #check what happens if the worker delayed 
    def reset_flags(self):        
        cur_time = datetime.now().replace(second=0, microsecond=0)
        if cur_time.time() == datetime.min.time():
            if cur_time.day == 1:
                self.goal_flags = {i:True for i in range(25, 225, 25)} 
            self.peak_flags.clear()
            self.baseline_flags.clear()
                
    def _is_peak_hour(self, cur_hour):
        return self.peak_start <= cur_hour < self.peak_end

    # DONT TEST 
    def _get_model(self, app_id):
        # file_path = f'./models_filesystem/cluster_models/{app_id}.pkl'
        file_path = 'tracker_server/models_filesystem/cluster_models/64d1605493d44252699aa216.pkl'
        file = open(file_path, "rb")
        model = pickle.load(file)
        file.close()
        return model

    def _notify_goal_check(self, user, cur_energy):
        goal = user['energy_goal']
        if goal != -1:
            month_enegry = user['current_month_energy'] + cur_energy
            percentage = PR.check_goal(month_enegry, goal)
            if percentage and self.goal_flags[percentage]:
                self.fcm.notify(self.user_id, NotifType.GOAL, {'percentage':percentage})
                self.goal_flags[percentage] = False
    
    def _notify_peak_check(self, id, status, e_type, name):
        cur_hour = datetime.now().hour
        if id not in self.peak_flags:
            self.peak_flags[id] = True
        if self.peak_flags[id] and self._is_peak_hour(cur_hour): 
            if PR.check_peak(status, e_type, self.shiftable):
                self.fcm.notify(self.user_id, NotifType.BASELINE, {'app_name': name})
                self.peak_flags[id] = False
    
    # DONT TEST THIS
    def _notify_phantom_check(self, id, pow, status, name):
            if id not in self.phantom_flags:
                self.phantom_flags[id] = [True, datetime.now()]
            if datetime.now() - self.phantom_flags[id][1] > self.hour:
                self.phantom_flags[id][0] = True
            if self.phantom_flags[id][0]:
                model = self._get_model(id)
                if PR.check_phantom(model, pow, status):
                    self.fcm.notify(self.user_id, NotifType.PHANTOM, {'app_name': name})
                    self.phantom_flags[id][0] = False
                    
    def _notify_baseline_check(self, id, energy, threshold, name):
        if id not in self.baseline_flags:
            self.baseline_flags[id] = True
        if threshold > 0 and self.baseline_flags[id]:
            if PR.check_baseline(energy, threshold):
                self.fcm.notify(self.user_id, NotifType.BASELINE, {'app_name': name})
                self.baseline_flags[id] = False          
                        
    def run(self):
        user = self.db.get_doc('Users', {'_id': ObjectId(self.user_id)}, {'energy_goal': 1, 
                                    'current_month_energy':1, 'appliances': 1}) 
        appliances = user['appliances']
        self.reset_flags()
        
        if len(appliances):
            apps = self._get_apps(appliances)
            cur_energy = 0
            for id, app in apps.items():
                cur_energy += app['energy']
                self._notify_peak_check(id, app['status'], app['e_type'], app['name'])
                self._notify_baseline_check(id, app['energy'], app['threshold'], app['name'])
            
            self._notify_goal_check(user, cur_energy) 
            powers = self._get_powers(apps)
            if powers:
                for id, pow in powers.items():
                    self._notify_phantom_check(id, pow, apps[id]['status'], apps[id]['name'])       
        