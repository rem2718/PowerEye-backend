from datetime import datetime, timedelta
from bson import ObjectId
import pickle

from recommender import Recommender as PR
from types_classes import NotifType
from interfaces.task import Task
class Checker(Task):
    HOUR = timedelta(hours=1)
    
    def __init__(self, id, db, fcm, additional=None):
        self.user_id = id
        self.db = db
        self.fcm = fcm
        self.goal_flags = [False] * 8
        self.phantom_ts = {}
        self.baseline_flags = {}
            
    def _sum_energy(self, appliances):
        energy = 0
        for app in appliances:
            energy += app['energy']
        return energy
    
    #  delete models when appliance is deleted
    def _get_model(self, type, app_id):
        file_path = f'models_filesystem/{type}_models/{app_id}'
        file = open(file_path, "rb")
        model = pickle.load(file)
        file.close()
        return model
    
    def run(self):
        user = self.db.get_doc('Users', {'_id': ObjectId(self.user_id)}, {'energy_goal': 1, 
                                    'current_month_energy':1, 'appliances': 1}) 
        
        goal = user['energy_goal']
        if goal != -1:
            appliances = user['appliances']
            month_enegry = self._sum_energy(appliances) + user['current_month_energy']
            percentage = PR.check_goal(month_enegry, goal, self.goal_flags)
            if percentage:
                self.fcm.notify(self.user_id, NotifType.GOAL, {'percentage':percentage})
            
        # app_ids = {str(app['_id']):1 for app in appliances if app['e_type'] == 3}
        
        # powers = Checker.db.get_doc('Powers', projection ={app_ids}, sort=[("timestamp", -1)]) 
        # for id, pow in powers.items():
        #     if datetime.now() - self.phantom_ts['id'] > self.HOUR:
        #         model = self._get_model('cluster', id)
        #         PR.check_phantom(pow, model)
        # # get power docs for type_3 only
        # loop over appliances
        # if flag = true continue
        # get cluster models (type cluster)
        # check if res == None or not

        # loop over appliances (same loop above)
        # if flag = true continue
        # if baseline = -1 continue
        # self.baseline_flags = PRS.check_baseline(energy, baseline, app_name)
        # check_peak()
        