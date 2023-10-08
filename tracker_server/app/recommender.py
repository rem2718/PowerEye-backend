import math
# NOT COMPLETE YET
class Recommender():
    """
    A class for providing personalized recommendation based on the user appliances power usage.
    """
    @staticmethod  
    def check_goal(month_enegry:float, goal:float):
        """
        Check if the monthly energy consumption meets a specified goal.
        Args:
            month_energy (float): The current month energy consumption.
            goal (float): The energy consumption goal.
        Returns:
            int: The percentage of goal achievement as an integer value (0-200).
        """
        percentage = month_enegry / goal 
        rounded = math.floor(percentage * 4) / 4
        return int(rounded * 100) if rounded <= 2 else 0
            
    @staticmethod
    def check_phantom(model, power, status):
        """
        Check if a device is in phantom mode based on a machine learning model prediction.
        Args:
            model: The machine learning model (k-mean cluster) for prediction.
            power: The power consumption of the device.
            status: The status (ON/OFF) of the device.
        Returns:
            bool: True if the device is in phantom mode, False otherwise.
        """
        if status:
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
    def check_peak(status, e_type, types):
        """
        Check if a shiftable device is on during peak time.
        Args:
            status: The status (ON/OFF) of the device.
            e_type: The energy type of the device.
            types: A list of shiftable devices types.
        Returns:
            bool: True if the device is shiftable and on, False otherwise.
        """
        return status and e_type in types

    # DONT TEST 
    @staticmethod
    def fill_na(powers):
        energy = (powers * 1/60) / 1000
        return energy.sum()
    
    # DONT TEST 
    @staticmethod
    def cluster(app_id, power):
        return False
    
    # DONT TEST 
    @staticmethod
    def _preprocessing(energy):
        pass
    
    # DONT TEST 
    @staticmethod
    def energy_forecasting(app, energys):
        return False, -1
    

    