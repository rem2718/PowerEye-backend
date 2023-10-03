import  logging

from firebase_admin import credentials
from firebase_admin import messaging
import firebase_admin

from external_dependencies.mongo import Mongo
from types_classes import NotifType

class FCM():
    
    def __init__(self, cred, db:Mongo):
        creds = credentials.Certificate(cred)
        firebase_admin.initialize_app(creds)
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def map_message(self, type, data=None):
        match type:
            case NotifType.CREDS: 
                title = 'Credentials Update Required' 
                body = 'Your Meross credentials need updating.'
            case NotifType.DISCONNECTION: 
                title = f'{data["app_name"]} is Offline' 
                body = 'Please check its connection and try to reconnect it as soon as possible for improved personalized recommendations.'
            case NotifType.GOAL: 
                title = 'Monthly Goal'
                body = f'Your current bill reach {data["percentage"]}% of your monthly goal'
            case NotifType.PEAK: 
                title = 'Peak Time'
                body = f'Try to postpone using {data["app_name"]} after 5 PM, click here to turn it off.'
            case NotifType.PHANTOM: 
                title = 'Phantom Mode'
                body = f'Your {data["app_name"]} is on phantom mode, click here to turn it off.'
            case NotifType.BASELINE: 
                title = ''
                body = f'Your {data["app_name"]} exceeds its daily baseline try to reduse using it today.'
        return title, body  
        
    def notify(self, user, type, data={}):
        token = self.db.get_doc('Users', {'_id': user}, {'registration_token': 1})
        title, body = self.map_message(type, data)
        
        print(f'notify: {type}', data)
        # message = messaging.Message(
        #     data = {
        #         "title": title,
        #         "body": body,
        #     },
        #     token = token,
        # )

        # response = messaging.send(message)
        # logger.info
        # logger.error
        # check all responses status

 
