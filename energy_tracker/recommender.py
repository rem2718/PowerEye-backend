import math
class Recommender():
    @classmethod  
    def check_goal(cls, month_enegry:float, goal:float):
        percentage = month_enegry / goal 
        rounded = math.floor(percentage * 4) / 4
        return int(rounded * 100) if rounded <= 2 else 0
            
    @classmethod
    def check_phantom(cls, model, power, status):
        if status:
            predicted_labels = model.predict([[0], [power]])
            return predicted_labels[0] == predicted_labels[1]
        return False
         
    @classmethod
    def check_baseline(cls, energy, baseline):
        return energy > baseline

    @classmethod  
    def check_peak(cls, status, e_type, types):
        return status and e_type in types

    @classmethod
    def fill_na(cls, power, doc):
        # fill null values for this day 
        # calculate energy
        # add them doc
        pass

    @classmethod
    def cluster(cls, app_id, power):
        # ---
        pass
    
    @classmethod
    def _preprocessing(cls, energy):
        # ---
        pass
    
    @classmethod
    def energy_forecasting(cls, app_id, energy):
        # ---
        pass
    

    