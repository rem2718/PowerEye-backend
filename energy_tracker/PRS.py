from datetime import datetime, timedelta
class PRS():
    HOUR = timedelta(hours=1)
    
    @classmethod  
    def check_goal(cls, month_enegry, goal, flags):
        # calcuate percentage
        # switch for the percentage
        # notify for each case
        # modify flags
        pass
    
    @classmethod
    def check_phantom(cls, power, model):
        # model.predict(power)
        # if phantom -> 
        # if current - ts > HOUR
        # notify and return new ts
        # else return same ts
        pass
    
    @classmethod
    def check_baseline(cls, energy, baseline, app_name):
        # if energy > baseline -> notify
        # return true 
        # else false
        pass
    
    @classmethod  
    def check_peak(cls, app_name, status, e_type):
        # if e_type == type_2 and status = on
        # notify() and return true
        # else false 
        pass
    
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
    

    