from datetime import datetime, timedelta
class Recommender():
    HOUR = timedelta(hours=1)
    @classmethod  
    def check_goal(cls, month_enegry:float, goal:float, flags:list):
        percentage = month_enegry / goal 
        match percentage:
            case p if p >= 0.25 and not flags[0]: 
                flags[0] = True 
                return 25
            case p if p >= 0.5 and not flags[1]: 
                flags[1] = True 
                return 50
            case p if p >= 0.75 and not flags[2]: 
                flags[2] = True 
                return 75
            case p if p >= 1 and not flags[3]: 
                flags[3] = True 
                return 100
            case p if p >= 1.25 and not flags[4]: 
                flags[4] = True 
                return 125
            case p if p >= 1.5 and not flags[5]: 
                flags[5] = True 
                return 150
            case p if p >= 1.75 and not flags[6]: 
                flags[6] = True 
                return 175
            case p if p >= 2 and not flags[7]: 
                flags[7] = True 
                return 200
            case _: return 0 
            
            
    @classmethod
    def check_phantom(cls, power:float, model):
        # model.predict(power)
        # if phantom -> 
        # if current - ts > HOUR
        # notify and return new ts
        # else return same ts
        pass
    
    @classmethod
    def check_baseline(cls, energy, baseline):
        if energy > baseline:
            return True 
        else:
            return False

    
    @classmethod  
    def check_peak(cls, status, e_type):
        if e_type == 2 and status:
            return True
        else:
            return False 

    
    @classmethod
    def reset_goal(cls,):
        # reset flags monthly
        pass

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
    

    