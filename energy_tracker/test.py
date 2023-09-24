from mongo import Mongo
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId
import os

load_dotenv(os.path.join('.secrets', '.env'))
URL = os.getenv('DB_URL')
db = Mongo(URL, 'hemsproject')

def to_energy(prev_energy, power):
    if power == None:
        power = 0
    return prev_energy + (power * 1/60) / 1000 
    
target_date = datetime(2023, 9, 24, 0, 0, 0)
users = ['64d1548894895e0b4c1bc07f','64d154d494895e0b4c1bc081','64d154bc94895e0b4c1bc080']

for user in users:
    li = []
    app = {}
    query = {'user': ObjectId(user), "timestamp": {"$gte": target_date}}
    projection = {'_id': 0, 'user': 0, 'timestamp': 0}
    results = db.get_docs('Powers', query, projection)
    first = True
    for res in results:
        if first:
            for field, value in res.items():
                app[field] = to_energy(0, value)
            first = False
        else:
            for field, value in res.items():
                app[field] = to_energy(app[field], value)
                
    for field, value in app.items():
        li.append((field, {'energy': value}))
        
    db.update_appliances('Users', ObjectId(user), li)
                
         
        

