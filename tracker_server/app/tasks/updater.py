from datetime import datetime, timedelta
from bson import ObjectId
import logging
import pickle
import os

import pandas as pd

from app.recommender import Recommender as EPR
from app.interfaces.task import Task
from app.types_classes import EType


class Updater(Task):
    """
    Updater task for updating appliance energy data and models.
    This class is responsible for updating appliance energy data and models, such as phantom mode cluster models and
    baseline threshold models.
    Attributes:
        day (timedelta): Time interval of one day.
        user_id (str): User identifier.
        db: The database instance.
        date: The current date.
        logger: The logger instance.
    """

    day = timedelta(days=1)
    day_threshold = 12 * 60

    def __init__(self, id, db, fcm=None, additional=None):
        """
        Constructor for the Updater class.
        Args:
            id: User identifier (not used here).
            db: The database instance.
            fcm: The FCM (Firebase Cloud Messaging) instance (not used here).
            additional: Additional data (not used here).
        """
        self.user_id = id
        self.db = db
        self.date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.logger = logging.getLogger(__name__)

    def _powers(self):
        """
        Get recent power consumption data for shiftable appliances.
        Returns:
            DataFrame: A DataFrame for appliances' power consumption data.
        """
        query = {"user": ObjectId(self.user_id)}
        projection = {"user": 0, "_id": 0}
        data = self.db.get_docs("Powers", query, projection)
        data = list(data)
        if len(data):
            powers = pd.DataFrame(data)
            powers["timestamp"] = pd.to_datetime(powers["timestamp"], errors="coerce")
            powers["timestamp"] = powers["timestamp"].apply(
                lambda x: x.replace(second=0, microsecond=0)
            )
            powers = powers.sort_values(by=["timestamp"])
            powers = powers.set_index("timestamp")
            return powers
        else:
            return pd.DataFrame()

    def _yesterday_energys(self, appliances):
        """
        Generate a dictionary of energy values for each appliance based on yesterday power data.
        Args:
            appliances (list): List of dictionaries representing appliances data.
        Returns:
            dict: Appliance IDs mapped to corresponding energy values. If an appliance has excessive missing
            data, its energy value is set to negative.
        """
        energys = {}
        for app in appliances:
            if app["is_deleted"]:
                continue
            app_id = str(app["_id"])
            energys[app_id] = app["energy"]
        return energys

    def _update_energy(self, energys, cur_energy, cur_date):
        """
        Update user energy-related information based on daily and monthly energy consumption.
        Args:
            energys (dict): Appliance IDs and their corresponding energy values.
            cur_energy (float): The current energy consumption for the month.
            cur_date (datetime): The current date.
        """
        yesterday_energy = sum(value for value in energys.values())
        month_energy = yesterday_energy + cur_energy
        self.db.update("Users", self.user_id, "appliances.$[].energy", 0)
        if cur_date.day == 1:
            self.db.update("Users", self.user_id, "current_month_energy", 0)
        else:
            self.db.update("Users", self.user_id, "current_month_energy", month_energy)

    def _dump_model(self, type, app_id, model):
        """
        Dump machine learning model to a file.
        Args:
            type: Model type ('cluster' or 'forecast').
            app_id: Appliance identifier.
            model: Machine learning model object.
        """
        folder_path = f"models_filesystem/{type}_models/{self.user_id}"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path, f"{app_id}.pkl")
        file = open(file_path, "wb")
        pickle.dump(model, file)
        file.close()

    def _apply_cluster(self, app_id, e_type, powers):
        """
        Apply clustering to the power consumption data for a specific appliance.
        Args:
            app_id (str): The identifier of the appliance.
            e_type (str): The energy type of the appliance.
            powers (dict): Appliance IDs maps to power consumption data.
        """
        if e_type == EType.PHANTOM.value:
            cluster = EPR.cluster(powers)
            if cluster:
                self._dump_model("cluster", app_id, cluster)
                self.logger.info(f"cluster_{app_id} is dumped successfully")

    def _apply_forecast(self, app_id, powers):
        """
        Find the best parameters for the forecasting model.
        Args:
            app_id (str): Appliance identifier.
            powers (dict): Appliance IDs and their corresponding energy values.
        """
        params, threshold = EPR.best_params(powers)
        if params != None:
            self._dump_model("forecast", app_id, params)
            self.db.update(
                "Users",
                self.user_id,
                "appliances.$[elem].baseline_threshold",
                threshold,
                [{"elem._id": ObjectId(app_id)}],
            )
            self.logger.info(f"forecast_{app_id} is dumped successfully")

    def run(self):
        """
        Run the updater task to update appliance energy data and models.
        """
        projection = {"current_month_energy": 1, "appliances": 1}
        user = self.db.get_doc("Users", {"_id": ObjectId(self.user_id)}, projection)
        appliances = user["appliances"]
        appliances = [app for app in appliances if not app["is_deleted"]]

        yesterday_energys = self._yesterday_energys(appliances)
        self._update_energy(
            yesterday_energys, user["current_month_energy"], datetime.now()
        )
        yesterday_energys["user"] = ObjectId(self.user_id)
        yesterday_energys["date"] = self.date
        self.db.insert_doc("Energys", yesterday_energys)
        self.logger.critical(f"energy: {self.date} -> done")
        self.date += self.day

        day = datetime.now().weekday()
        if day == 6:
            powers = self._powers()
            if powers.shape[0] > 0:
                for app in appliances:
                    app_id = str(app["_id"])
                    self._apply_cluster(app_id, app["e_type"], powers[app_id])
                    self._apply_forecast(app_id, powers[app_id])
