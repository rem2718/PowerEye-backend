from PRS import PRS 
class Checker():
    db = None
    
    def __init__(self, user_id):
        self.user_id
        self.goal_flags = [False * 8] # 25% - 200%
        self.phantom_ts = {}
        self.baseline_flags = {}
    
    @classmethod    
    def set_db(cls, db):
        cls.db = db
        
    def sum_energy(self, appliances):
        # loop over appliances energy
        # return sum
        pass 
    
    def run(self):
        # get user appliances (user: goal month_energy, appliance: name, energy, baseline e_type)
        month_enegry += self.sum_energy()
   
        PRS.check_goal(month_enegry, goal, self.goal_flags)
        # get power docs for type_3 only
        # loop over appliances
        # if flag = true continue
        # get cluster models (type cluster)
        # check if res == None or not
        self.flag[app] = PRS.check_phantom(power, model, app_name, self.phantom_ts[app])
        # loop over appliances (same loop above)
        # if flag = true continue
        # if baseline = -1 continue
        self.baseline_flags = PRS.check_baseline(energy, baseline, app_name)
        