import  logging

from firebase_admin import credentials
from firebase_admin import messaging
import firebase_admin

from app.interfaces.db import DB
from app.types_classes import NotifType

# NOT COMPLETE YET
class FCM():
    """
    Firebase Cloud Messaging (FCM) service for sending notifications.
    This class provides methods for initializing FCM, mapping notification messages based on types,
    and sending notifications to users.

    Attributes:
        db (DB): An instance of the database connection.
        logger (logging.Logger): The logger for logging messages.
    """
    
    def __init__(self, cred, db:DB):
        """
        Constructor for the FCM class.
        Args:
            cred (str): The path to the Firebase credentials file.
            db (DB): An instance of the database connection.
        """
        creds = credentials.Certificate(cred)
        firebase_admin.initialize_app(creds)
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def map_message(self, type, data=None):
        """
        Map notification messages based on the notification type and data.
        Args:
            type (NotifType): The type of notification.
            data (dict, optional): Additional data for customizing the message.
        Returns:
            tuple: A tuple containing the title and body of the notification message.
        """
        title = body = ''
        
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
        """
        Send a notification to a user.
        Args:
            user (str): The user's identifier.
            type (NotifType): The type of notification.
            data (dict, optional): Additional data for customizing the message.
        """
        token = self.db.get_doc('Users', {'_id': user}, {'registration_token': 1})
        title, body = self.map_message(type, data)
        
        self.logger.info(f'notify: {type}', data)
        # message = messaging.Message(
        #     data = {
        #         "title": title,
        #         "body": body,
        #     },
        #     token = token,
        # )

        # response = messaging.send(message)
        
        # self.logger.info()
        # self.logger.error()
        # check all responses status

 
