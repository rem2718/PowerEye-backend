import math

from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
import pandas as pd


class Recommender:
    """
    A class for providing personalized recommendation based on the user appliances power usage.
    """

    CLUSTER_THRESHOLD = 1000
    SILHOUETTE_THRESHOLD = 0.5
    PEAK_START = 13
    PEAK_END = 17

    @staticmethod
    def check_goal(month_enegry: float, goal: float):
        """
        Check if the monthly energy consumption meets a specified goal.
        Args:
            month_energy (float): The current month energy consumption.
            goal (float): The energy consumption goal.
        Returns:
            int: The percentage of goal achievement as an integer value (0-200).
        """
        percentage = month_enegry / goal
        if percentage > 2:
            percentage += 1
        rounded = math.floor(percentage * 4) / 4
        return int(rounded * 100) if rounded <= 2 else 0

    @staticmethod
    def check_peak(cur_hour, status, e_type, types):
        """
        Check if a shiftable device is on during peak time.
        Args:
            cur_hour (int): Current hour.
            status (boolean): The status (ON/OFF) of the device.
            e_type (int): The energy type of the device.
            types (list): A list of shiftable devices types.
        Returns:
            bool: True if the device is shiftable and on, False otherwise.
        """
        is_peak = Recommender.PEAK_START <= cur_hour < Recommender.PEAK_END
        return is_peak and status and e_type in types

    @staticmethod
    def check_phantom(model, power, status):
        """
        Check if a device is in phantom mode based on a machine learning model prediction.
        Args:
            model (sklearn.cluster.KMeans): The machine learning model (k-mean cluster) for prediction.
            power (float): The power consumption of the device.
            status (boolean): The status (ON/OFF) of the device.
        Returns:
            bool: True if the device is in phantom mode, False otherwise.
        """
        if model and status:
            predicted_labels = model.predict([[0], [power]])
            return predicted_labels[0] == predicted_labels[1]
        return False

    @staticmethod
    def check_baseline(energy, baseline):
        """
        Check if the energy consumption exceeds a baseline threshold.
        Args:
            energy (float): The energy consumption.
            baseline (float): The baseline threshold.
        Returns:
            bool: True if the energy consumption exceeds the baseline, False otherwise.
        """
        return energy > baseline

    @staticmethod
    def cluster(appliance):
        """
        Cluster appliance data using the KMeans algorithm.
        Args:
            appliance (pd.Series): A pandas Series representing the appliance data.
        Returns:
            KMeans or False: If clustering is successful, returns the KMeans model. Otherwise, returns False.
        """
        appliance = appliance.dropna()
        if appliance.shape[0] < Recommender.CLUSTER_THRESHOLD:
            return False

        value_counts = appliance.value_counts()
        total_count = value_counts.sum()
        weights = value_counts / total_count

        appliance = appliance.drop_duplicates()
        if appliance.shape[0] < 2:
            return False
        X = appliance.values.reshape(-1, 1)

        kmeans = KMeans(n_clusters=2, n_init=10)
        kmeans.fit(X, sample_weight=weights)

        score = silhouette_score(X, kmeans.labels_)
        if score < Recommender.SILHOUETTE_THRESHOLD:
            return False

        return kmeans

    @staticmethod
    def _preprocessing(energy):
        pass

    @staticmethod
    def energy_forecast(app, energys):
        return False, -1
