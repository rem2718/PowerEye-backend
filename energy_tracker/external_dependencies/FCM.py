from firebase_admin import credentials
from firebase_admin import messaging
from mongo import Mongo
import firebase_admin

class FCM():
    
    def __init__(self, cred, db:Mongo):
        creds = credentials.Certificate(cred)
        default_app = firebase_admin.initialize_app(creds)
        self.db = db
    
    
    def map_message(self, type, data=None):
        # fix these 
        title = ''
        body = ''
        match type:
            case 'creds': pass
            case 'disconnection': data['app_name']
            case 'goal': pass
            case 'peak': pass
            case 'phantom': pass
            case 'baseline': pass
        return title, body  
        
        
    def notify(self, user, type, data):
        token = self.db.get_doc('Users', {'_id': user}, {'registration_token': 1})
        title, body = self.map_message(type, data)
        
        message = messaging.Message(
            data = {
                "title": title,
                "body": body,
            },
            token = token,
        )

        response = messaging.send(message)
        print("Successfully sent message:", response)
        # check all responses status

 
