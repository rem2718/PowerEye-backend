from datetime import datetime, timedelta
from bson import ObjectId
import logging
import pickle
 
import pandas as pd

from app.recommender import Recommender as PR
from app.interfaces.task import Task
from app.types_classes import EType

# TO-DO: check sync between updater and checker, starting the server, when server crashes

class Updater(Task):
    day = timedelta(days=1)
    
    def __init__(self, id, db, fcm=None, additional=None):
        self.user_id = id
        self.db = db
        self.date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.logger = logging.getLogger(__name__)    
        
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
        return doc   
        
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
        sort = [('timestamp', 1)]
        powers = self.db.get_docs('Powers_test', query, projection, sort)
        return pd.DataFrame(list(powers))
      
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
        sort = [('date', 1)]
        energys = self.db.get_docs('Energys_test', query, projection, sort)
        return pd.DataFrame(list(energys))  
    
    def _dump_model(type, app_id, model):
        file_path = f'tracker_server/models_filesystem/cluster_models/{type}_models/{app_id}.pkl'
        file = open(file_path, "wb")
        pickle.dump(model, file)
        file.close()
 
    def run(self):
        user = self.db.get_doc('Users', {'_id': ObjectId(self.user_id)}, {'current_month_energy': 1, 'appliances._id': 1, 'appliances.energy': 1, 'appliances.e_type': 1})
        doc = self._update_energy(user)
        app_type = {str(app['_id']): app['e_type'] for app in user['appliances']}
        
        powers = self._yesterday_powers()
        energys = self._cur_month_energy()
        for app in powers.columns:
            if powers.shape[0]:
                energy = PR.fill_na(powers[app])
                doc[app]['imputed'] = energy
                if app_type[app] == EType.PHANTOM.value:
                    cluster = PR.cluster(app, powers[app]) #if its one day duration
                    if cluster:
                        self._dump_model('cluster', app, cluster)
                        self.logger(f'cluster_{app} is dumped successfully')
            if energys.shape[0]:
                forcast, threshold = PR.energy_forecasting(app, energys[app])
                if forcast:
                    self._dump_model('forcast', app, forcast)
                    array_filter = [{'elem._id': ObjectId(app)}]
                    self.db.update('Users', self.user_id, 'appliances.$[elem].baseline_threshold', threshold, array_filter)
                    self.logger(f'forcast_{app} is dumped successfully')
                
        self.db.insert_doc('Energys_test', doc)
        self.date += self.day
