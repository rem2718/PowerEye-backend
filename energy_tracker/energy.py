from datetime import datetime, timedelta
from PRS import reset_peak, fill_na, cluster, energy_forecasting

class Energy():
    db = None
    DAY = timedelta(days=1)
    def __init__(self, db):
        self.db = db
        self.ts = datetime.now()
  
    def run(self):
        docs = []
        users = self.db.get_docs('Users', projection={'appliances._id': 1, 'appliances.energy': 1})
        for user in users:
            doc = {}
            doc['user'] = user['_id']
            doc['timestamp'] = self.ts
            for app in user['appliances']:
                doc[str(app['_id'])] = app['energy']
            docs.append(doc)
        self.db.update_all('Users', 'appliances.$[].energy', 0)
        self.db.insert_docs('Energys', docs)
        self.ts += self.DAY
        

    


