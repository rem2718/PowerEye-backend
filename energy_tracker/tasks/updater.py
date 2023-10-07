from datetime import datetime, timedelta
from bson import ObjectId

import pandas as pd

from recommender import Recommender as PR
from interfaces.task import Task

# TO-DO: check sync between updater and checker, starting the server, logs file, 
# clear docs or anything for the ram

class Updater(Task):
    day = timedelta(days=1)
    
    def __init__(self, id, db, fcm=None, additional=None):
        self.user_id = id
        self.db = db
        self.date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
    def _update_energy(self, user):
        doc = {}
        doc['user'] = user['_id']
        doc['date'] = self.date
        cur_time = datetime.now()
        if cur_time.day == 1:
            self.db.update('Users', self.user_id, 'current_month_energy', 0) #check
        cur_energy = 0
        for app in user['appliances']:
            doc[str(app['_id'])] = {'real': app['energy']}
            cur_energy += app['energy']
        month_energy = user['current_month_energy'] + cur_energy
        self.db.update('Users', self.user_id, 'appliances.$[].energy', 0)
        self.db.update('Users', self.user_id, 'current_month_energy', month_energy)
               
    def _yesterday_powers(self):
        previous_day = self.date - self.day
        query = {
            'user': ObjectId(self.user_id),
            'timestamp': {
                '$gte': previous_day.replace(hour=0, minute=0, second=0),
                '$lt': previous_day.replace(hour=23, minute=59, second=59)
            }
        }
        projection = {'timestamp':0, 'user':0, '_id':0}
        sort = [('timestamp', -1)]
        powers = self.db.get_docs('Powers', query, projection, sort)
        return powers  
      
    # check last day of month
    def _cur_month_energy(self):
        first_day = self.date.replace(day=1)
        yesterday = self.date - self.day
        last_day= self.date.replace(
            day= yesterday.day,
            hour=23,
            minute=59,
            second=59,
            microsecond=999
        )
        query = {
            'user': ObjectId(self.user_id),
            'timestamp': {
                '$gte': first_day,
                '$lt': last_day
            }
        }
        projection = {'date':0, 'user':0, '_id':0}
        sort = [('date', -1)]
        powers = self.db.get_docs('Energys', query, projection, sort)
        return powers  
        
    def run(self):
        user = self.db.get_docs('Users', {'_id': ObjectId(self.user_id)}, {'current_month_energy': 1, 'appliances._id': 1, 'appliances.energy': 1})
        doc = self._update_energy(user)
        
        powers = pd.Dataframe(self._yesterday_powers())
        energys = pd.Dataframe(self._cur_month_energy())
        for app in powers.columns:
            energy = PR.fill_na(powers[app])
            doc[app]['imputed'] = energy
            PR.cluster(app, powers[app]) #if its one day duration
            PR.energy_forecasting(app, energys[app])
        self.db.insert_doc('Energys', doc)
        self.date += self.day
