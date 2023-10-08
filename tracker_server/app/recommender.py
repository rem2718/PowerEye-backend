import math
class Recommender():
    @staticmethod  
    def check_goal(month_enegry:float, goal:float):
        percentage = month_enegry / goal 
        rounded = math.floor(percentage * 4) / 4
        return int(rounded * 100) if rounded <= 2 else 0
            
    @staticmethod
    def check_phantom(model, power, status):
        if status:
            predicted_labels = model.predict([[0], [power]])
            return predicted_labels[0] == predicted_labels[1]
        return False
         
    @staticmethod
    def check_baseline(energy, baseline):
        return energy > baseline

    @staticmethod  
    def check_peak(status, e_type, types):
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
    

    