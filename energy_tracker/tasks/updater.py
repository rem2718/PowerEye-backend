from datetime import datetime, timedelta
from PRS import PRS
# rename this class plz
# TO-DO: check sync, starting the server, redisAI, models collection, timestamp for energy transfer
class Updater():
    db = None
    DAY = timedelta(days=1)
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.ts = datetime.now()

    @classmethod    
    def set_db(cls, db):
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
        PRS.fill_na(power, doc)
        self.db.insert_doc('Energys', doc)
        # loop over app
        PRS.cluster(app_id, power)
        # get energy (specific period) imputed values
        PRS.energy_forecasting(app_id, energy)
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
         
