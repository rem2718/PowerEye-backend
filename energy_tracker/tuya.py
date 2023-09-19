import tinytuya
import pymongo
import os
from datetime import datetime, timedelta
from bson import ObjectId
from dotenv import load_dotenv

dotenv_path = os.path.join('.secrets', '.env')
load_dotenv(dotenv_path)

URL = os.getenv("DB_URL")
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
API_DEVICE = [os.getenv("API_DEVICE_10"), os.getenv("API_DEVICE_20"), os.getenv("API_DEVICE_30")]
INTERVAL = timedelta(seconds=60)
timestamp = datetime.now()

    
dev_map = {
    'fridge_10': '64d160d293d44252699aa218',
    'charger_10': '64d1609b93d44252699aa217',
    'food_processor_10': '64d15f9393d44252699aa215',
    'tv_10': '64d1605493d44252699aa216',
    
    'fridge_11': '64d161e193d44252699aa219',
    'lamp_10': '64d161fd93d44252699aa21a',
    'office_strip_10': '64d1629393d44252699aa21b',
    'tv_11': '64d162bf93d44252699aa21c',
    
    'fridge_20': '64d1646b93d44252699aa221',
    'coffee_maker_20': '64d1641a93d44252699aa220',
    'lamp_20': '64d1648093d44252699aa222',
    'charger_20': '64d162ff93d44252699aa21d',
    'fan_20': '64d1638293d44252699aa21e',
    'hair_dryer_20': '64d163dd93d44252699aa21f',
    
    'cooler_30': '64d1656693d44252699aa225',
    'toaster_30': '64d1685693d44252699aa22b',
    'charger_30': '64d1682993d44252699aa22a',
    'lamp_30': '64d1659d93d44252699aa226',
    'air_fryer_30': '64d1650b93d44252699aa223',
    'camera_30': '64d167a193d44252699aa228',
    'speaker_30': '64d167e593d44252699aa229',
    'tv_30': '64d1687493d44252699aa22c',
    'office_strip_30': '64d165e693d44252699aa227',
}
ids = ['64d1548894895e0b4c1bc07f','64d154d494895e0b4c1bc081','64d154bc94895e0b4c1bc080']

def get_pow(user):
    doc = {}
    cloud = tinytuya.Cloud(
            apiRegion="eu", 
            apiKey=API_KEY, 
            apiSecret=API_SECRET, 
            apiDeviceID=API_DEVICE[user])
    
    devices = cloud.getdevices() 
    doc['user'] = ObjectId(ids[user])
    try:
        for dev in devices:
            connected = cloud.getconnectstatus(dev['id'])
            if connected:
                result = cloud.getstatus(dev['id'])
                state = result['result'][4]['value']
                doc[dev_map[dev['name']]] = state/10.0
            else:
                doc[dev_map[dev['name']]] = None
        print(doc)
                
    except Exception as e:
        print(f'tuya error: {repr(e)}') 
        
            
# def insert_into_db():
#     client = pymongo.MongoClient(URL)
#     db = client['hemsproject']
#     collection = db['pp']
#     doc['timestamp'] = timestamp
    
#     try:    
#         collection.insert_one(doc)   
#     except Exception as e:
#         print(f'mongodb error: {repr(e)}') 
        
#     print(f'{doc["timestamp"]}: done')
#     doc.clear()
#     timestamp += INTERVAL