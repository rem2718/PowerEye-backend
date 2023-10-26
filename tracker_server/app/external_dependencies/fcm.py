import logging
from firebase_admin import credentials, messaging
import firebase_admin
from app.interfaces.db import DB
from app.types_classes import NotifType

class FCM:
    """
    Firebase Cloud Messaging (FCM) service for sending notifications.
    This class provides methods for initializing FCM, mapping notification messages based on types,
    and sending notifications to users.

    Attributes:
        db (DB): An instance of the database connection.
        logger (logging.Logger): The logger for logging messages.
    """
    
    def __init__(self, cred, db: DB):
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

        # Map notification types to user-friendly titles and bodies
        match type:
            case NotifType.CREDS:
                title = 'Update Your Login'
                body = 'Please update your login information for Meross.'
            case NotifType.DISCONNECTION:
                title = 'Device Not Working'
                body = f'Your {data["app_name"]} is currently not working. Check its connection and fix it for better suggestions.'
            case NotifType.GOAL:
                title = 'Monthly Usage Goal'
                body = f"You're close to reaching {data['percentage']}% of your monthly usage goal."
            case NotifType.PEAK:
                title = 'Peak Usage Alert'
                body = f'Try not to use {data["app_name"]} after 5 PM. Click here to turn it off.'
            case NotifType.PHANTOM:
                title = 'Ghost Mode Active'
                body = f'{data["app_name"]} is in ghost mode. Click here to turn it off.'
            case NotifType.BASELINE:
                title = 'Using Too Much'
                body = f'{data["app_name"]} used more than it should today. Try to use it less.'

        return title, body

    def notify(self, user, type, data={}):
        """
        Send a notification to a user.
        Args:
            user (str): The user's identifier.
            type (NotifType): The type of notification.
            data (dict, optional): Additional data for customizing the message.
        """
        # Get the user's registration token from the database
        token = self.db.get_doc('Users', {'_id': user}, {'registration_token': 1})

        # Map the notification type to a title and body
        title, body = self.map_message(type, data)

        # Log the notification
        self.logger.info(f'notify: {type} {data}')  # Combined 'type' and 'data' in a single f-string

        # Create a message with the title and body
        message = messaging.Message(
        data={
            "title": title,
            "body": body,
            },
        token=token,
        )
        response = messaging.send(message)

        # Log response status
        self.logger.info(f"Notification sent with response: {response}")

