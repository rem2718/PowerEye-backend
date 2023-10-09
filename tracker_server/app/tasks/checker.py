from datetime import datetime, timedelta
from bson import ObjectId
import pickle

from app.recommender import Recommender as PR
from app.types_classes import NotifType, EType
from app.interfaces.task import Task

class Checker(Task):
    """
    Checker task for checking device status and notifying users.
    This class is responsible for checking device status, calculating energy consumption, 
    and notifying users about various events.

    Attributes:
        shiftable (list): List of energy types for devices.
        hour (timedelta): Time interval for hourly checks.
        peak_start (int): Start hour of peak energy consumption.
        peak_end (int): End hour of peak energy consumption.
        user_id (str): User identifier.
        db: The database instance.
        fcm: The FCM (Firebase Cloud Messaging) instance.
        goal_flags (dict): Flags to track goal notifications.
        peak_flags (dict): Flags to track peak hour notifications.
        phantom_flags (dict): Flags to track phantom mode notifications.
        baseline_flags (dict): Flags to track baseline threshold notifications.
    """
    shiftable = [EType.SHIFTABLE.value, EType.PHANTOM.value]
    hour = timedelta(hours=1)
    peak_start = 13
    peak_end = 17
    
    def __init__(self, id, db, fcm, additional=None):
        """
        Constructor for the Checker class.
        Args:
            id: User identifier.
            db: The database instance.
            fcm: The FCM (Firebase Cloud Messaging) instance.
            additional: Additional parameters (not used here).
        """
        self.user_id = id
        self.db = db
        self.fcm = fcm
        self.goal_flags = {i:True for i in range(25, 225, 25)} 
        self.peak_flags = {} 
        self.phantom_flags = {} 
        self.baseline_flags = {} 
            
    def _get_apps(self, appliances):
        """
        Get information about user's appliances.
        Args:
            appliances: List of user's appliances.
        Returns:
            dict: A dictionary mapping appliance IDs to appliance information.
        """
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
        """
        Get recent power consumption data for shiftable appliances.
        Args:
            apps: Dictionary of appliances.
        Returns:
            dict: A dictionary mapping appliance IDs to recent power consumption data.
        """
        projection = {key:1 for key, value in apps.items() if value['e_type'] == EType.PHANTOM.value}
        projection['_id'] = 0
        sort = [("timestamp", -1)]
        if len(projection):
            return self.db.get_doc('Powers_test', {'user': ObjectId(self.user_id)}, projection=projection, sort=sort)
        else:
            return {}
        
    #check what happens if the worker delayed 
    def reset_flags(self): 
        """
        Reset notification flags at the start of the day.
        """       
        cur_time = datetime.now().replace(second=0, microsecond=0)
        if cur_time.time() == datetime.min.time():
            if cur_time.day == 1:
                self.goal_flags = {i:True for i in range(25, 225, 25)} 
            self.peak_flags.clear()
            self.baseline_flags.clear()
                
    def _is_peak_hour(self, cur_hour):
        """
        Check if the current hour is within the peak hours.
        Args:
            cur_hour: Current hour.
        Returns:
            bool: True if the current hour is within the peak hours, False otherwise.
        """
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
        """
        Notify the user about reaching their energy consumption goal.
        Args:
            user: User document.
            cur_energy: Current energy consumption for the day.
        """
        goal = user['energy_goal']
        if goal != -1:
            month_enegry = user['current_month_energy'] + cur_energy
            percentage = PR.check_goal(month_enegry, goal)
            if percentage and self.goal_flags[percentage]:
                self.fcm.notify(self.user_id, NotifType.GOAL, {'percentage':percentage})
                self.goal_flags[percentage] = False
    
    def _notify_peak_check(self, id, status, e_type, name):
        """
        Notify the user about peak hour energy consumption for an appliance.
        Args:
            id: Appliance ID.
            status: Appliance status.
            e_type: Appliance energy type.
            name: Appliance name.
        """
        cur_hour = datetime.now().hour
        if id not in self.peak_flags:
            self.peak_flags[id] = True
        if self.peak_flags[id] and self._is_peak_hour(cur_hour): 
            if PR.check_peak(status, e_type, self.shiftable):
                self.fcm.notify(self.user_id, NotifType.BASELINE, {'app_name': name})
                self.peak_flags[id] = False
    
    # DONT TEST THIS
    def _notify_phantom_check(self, id, pow, status, name):
        """
        Notify the user of phantom mode appliance usage.
        Args:
            id: Appliance identifier.
            pow: Power consumption data.
            status: Appliance status.
            name: Appliance name.
        """
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
        """
        Notify the user of baseline threshold condition.
        Args:
            id: Appliance identifier.
            energy: Energy consumption data.
            threshold: Baseline threshold value.
            name: Appliance name.
        """
        if id not in self.baseline_flags:
            self.baseline_flags[id] = True
        if threshold > 0 and self.baseline_flags[id]:
            if PR.check_baseline(energy, threshold):
                self.fcm.notify(self.user_id, NotifType.BASELINE, {'app_name': name})
                self.baseline_flags[id] = False          
                        
    def run(self):
        """
        Run the checker task to check appliance statuses and notify users of relevant conditions.
        """
        projections = {'energy_goal': 1, 'current_month_energy':1, 'appliances': 1}
        user = self.db.get_doc('Users', {'_id': ObjectId(self.user_id)}, projections) 
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
        