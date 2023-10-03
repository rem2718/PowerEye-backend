from datetime import datetime, timedelta
from interfaces.task import Task
from recommender import Recommender as PR
# TO-DO: check sync between updater and checker, starting the server, timestamp for energy transfer
# update month energy at the enf of the month
class Updater(Task):
    db = None
    DAY = timedelta(days=1)
    
    def __init__(self, id, db, fcm=None, additional=None):
        self.user_id = id
        self.ts = datetime.now()


    @classmethod
    def set_deps(cls, db):
        cls.db = db
        
        
    def update_month_energy(self, appliances, month_energy):
        # if day is one set to zero
        # loop over appliances energy
        # return sum
        # update month energy
        pass 
    
    
    def run(self):
        docs = []
        # month energy
        users = self.db.get_docs('Users', projection={'appliances._id': 1, 'appliances.energy': 1})
        for user in users: #cancel
            doc = {}
            doc['user'] = user['_id']
            doc['timestamp'] = self.ts
            for app in user['appliances']:
                doc[str(app['_id'])] = app['energy']
            docs.append(doc)
            
        self.update_month_energy(appliances, month_energy) 
        self.db.update_all('Users', 'appliances.$[].energy', 0)
        # get power (specific period)
        # loop over appliances
        PR.fill_na(power, doc)
        self.db.insert_doc('Energys', doc)
        # loop over app
        PR.cluster(app_id, power)
        # get energy (specific period) imputed values
        PR.energy_forecasting(app_id, energy)
        self.ts += self.DAY
        

class Peak():
         
    def __init__(self, user_id):
        self.user_id = user_id
        self.flags = {}
        
    @classmethod    
    def set_db(cls, db):
        cls.db = db
    
    def reset_peak(self):
        # set flags to false
        pass
    
    def run(self):   
        # get appliances (id, name, status, e_type)
        # loop over appliances
        # if flag true continue
        self.flags[id] = PRS.check_peak(app_name, status, e_type)
        # if current time > 4:59
        self.reset_peak()
         

