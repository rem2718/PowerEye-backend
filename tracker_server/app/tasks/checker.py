from datetime import datetime, timedelta
from bson import ObjectId
import logging
import pickle

import pandas as pd

from app.recommender import Recommender as EPR
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
        self.goal_flags = {i: True for i in range(25, 225, 25)}
        self.peak_flags = {}
        self.phantom_flags = {}
        self.baseline_flags = {}
        self.logger = logging.getLogger(__name__)

    def _get_apps(self, appliances):
        """
        Get information about user's appliances.
        Args:
            appliances: List of user's appliances.
        Returns:
            dict: A dictionary mapping appliance IDs to appliance information.
        """
        apps = {
            str(app["_id"]): {
                "name": app["name"],
                "e_type": app["e_type"],
                "energy": app["energy"],
                "status": app["status"],
                "baseline_threshold": app["baseline_threshold"],
            }
            for app in appliances
            if not app["is_deleted"]
        }
        return apps

    def _get_recent_powers(self, apps):
        """
        Get recent power consumption data for shiftable appliances.
        Args:
            apps: Dictionary of appliances.
        Returns:
            dict: A dictionary mapping appliance IDs to recent power consumption data.
        """
        projection = {
            key: 1
            for key, value in apps.items()
            if value["e_type"] == EType.PHANTOM.value
        }
        projection["_id"] = 0
        sort = [("timestamp", -1)]
        if len(projection):
            return self.db.get_doc(
                "Powers",
                {"user": ObjectId(self.user_id)},
                projection=projection,
                sort=sort,
            )
        else:
            return {}

    def _get_powers(self):
        """
        Get recent power consumption data for shiftable appliances.
        Returns:
            DataFrame: A DataFrame for appliances' power consumption data.
        """
        query = {
            "user": ObjectId(self.user_id),
            "timestamp": {
                "$lt": datetime.now().replace(minute=0, second=0, microsecond=0)
            },
        }
        projection = {"_id": 0, "user": 0}
        data = self.db.get_docs(
            "Powers",
            query,
            projection=projection,
        )
        data = list(data)
        if len(data):
            powers = pd.DataFrame(data)
            powers["timestamp"] = pd.to_datetime(powers["timestamp"], errors="coerce")
            powers["timestamp"] = powers["timestamp"].apply(
                lambda x: x.replace(second=0, microsecond=0)
            )
            powers = powers.sort_values(by=['timestamp'])
            powers = powers.set_index("timestamp")
            return powers
        else:
            return pd.DataFrame()

    def _reset_flags(self, cur_time):
        """
        Reset notification flags at the start of the day.
        Args:
            cur_time: Current time.
        """
        cur_time = cur_time.replace(second=0, microsecond=0)
        if cur_time.time() == datetime.min.time():
            if cur_time.day == 1:
                self.goal_flags = {i: True for i in range(25, 225, 25)}
            self.peak_flags.clear()
            self.baseline_flags.clear()

    def _is_hour_elapsed(self, app_id):
        """
        Check if an hour is elapsed for a specific appliance after phantom notification.
        Args:
            app_id (str): Appliance identifier.
        Returns:
            bool: True if an hour has elapsed, False otherwise.
        """
        return datetime.now() - self.phantom_flags[app_id][1] > self.hour

    def _get_model(self, app_id, type):
        """
         Retrieve a machine learning model associated with a specific app.
        Args:
            app_id (str): Appliance identifier.
            type (str): Model type.
        Returns:
            object or bool: The machine learning model if found, or False if an error occurs.
        """
        try:
            file_path = f"./models_filesystem/{type}_models/{self.user_id}/{app_id}.pkl"
            file = open(file_path, "rb")
            model = pickle.load(file)
            file.close()
            return model
        except:
            return False

    def _notify_goal(self, user, cur_energy):
        """
        Notify the user about reaching their energy consumption goal.
        Args:
            user: User document.
            cur_energy: Current energy consumption for the day.
        """
        goal = user["energy_goal"]
        if goal > 0:
            month_enegry = user["current_month_energy"] + cur_energy
            percentage = EPR.check_goal(month_enegry, goal)
            if percentage and self.goal_flags[percentage]:
                self.fcm.notify(
                    self.user_id, NotifType.GOAL, {"percentage": percentage}
                )
                self.goal_flags[percentage] = False

    def _notify_peak(self, app_id, app):
        """
        Notify the user about peak hour energy consumption for an appliance.
        Args:
            id: Appliance identifier.
            app: Appliance data.
        """
        status = app["status"]
        e_type = app["e_type"]
        name = app["name"]
        if app_id not in self.peak_flags:
            self.peak_flags[app_id] = True
        if self.peak_flags[app_id]:
            if EPR.check_peak(datetime.now().hour, status, e_type, self.shiftable):
                self.fcm.notify(self.user_id, NotifType.PEAK, {"app_name": name})
                self.peak_flags[app_id] = False

    def _notify_phantom(self, app_id, app, power):
        """
        Notify the user of phantom mode appliance usage.
        Args:
            id: Appliance identifier.
            app: Appliance data.
            power: Power consumption data.
        """
        status = app["status"]
        name = app["name"]
        if app_id not in self.phantom_flags:
            self.phantom_flags[app_id] = [True, datetime.now()]
        if not self.phantom_flags[app_id][0] and self._is_hour_elapsed(app_id):
            self.phantom_flags[app_id][0] = True
        if self.phantom_flags[app_id][0]:
            model = self._get_model(app_id, "cluster")
            if model and EPR.check_phantom(model, power, status):
                self.fcm.notify(self.user_id, NotifType.PHANTOM, {"app_name": name})
                self.phantom_flags[app_id][0] = False
                self.phantom_flags[app_id][1] = datetime.now()

    def _notify_baseline(self, app_id, app, powers):
        """
        Notify the user of baseline threshold condition.
        Args:
            id: Appliance identifier.
            app: Appliance data.
            powers: powers data
        """
        baseline = app["baseline_threshold"]
        name = app["name"]
        if app_id not in self.baseline_flags:
            self.baseline_flags[app_id] = True
        if baseline > 0 and self.baseline_flags[app_id]:
            params = self._get_model(app_id, "forecast")
            if params and EPR.check_baseline(baseline, powers, params):
                self.fcm.notify(self.user_id, NotifType.BASELINE, {"app_name": name})
                self.baseline_flags[app_id] = False

    def run(self):
        """
        Run the checker task to check appliance statuses and notify users of relevant conditions.
        """
        projections = {"energy_goal": 1, "current_month_energy": 1, "appliances": 1}
        user = self.db.get_doc("Users", {"_id": ObjectId(self.user_id)}, projections)
        appliances = user["appliances"]
        appliances = self._get_apps(appliances)
        self._reset_flags(datetime.now())
        min = datetime.now().minute
        if min == 0:
            powers = self._get_powers()
        if len(appliances):
            power = self._get_recent_powers(appliances)
            cur_energy = 0
            for id, app in appliances.items():
                cur_energy += app["energy"]
                self._notify_peak(id, app)
                if id in power:
                    self._notify_phantom(id, app, power[id])
                if min == 0 and powers.shape[0] > 0:
                    self._notify_baseline(id, app, powers[id])

            self._notify_goal(user, cur_energy)
