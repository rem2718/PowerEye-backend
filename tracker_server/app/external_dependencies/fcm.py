from bson import ObjectId
import logging

from firebase_admin import credentials, messaging
import firebase_admin

from app.types_classes import NotifType
from app.interfaces.db import DB


class FCM:
    """
    Firebase Cloud Messaging (FCM) service for sending notifications.
    This class provides methods for initializing FCM, mapping notification messages based on types,
    and sending notifications to users.

    Attributes:
        app (firebase_admin.App): firebase app.
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
        self.app = firebase_admin.initialize_app(creds)
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
        title = body = ""

        # Map notification types to user-friendly titles and bodies
        match type:
            case NotifType.CREDS:
                title = "Update Your Password"
                body = "Please update your login information for Meross."
            case NotifType.DISCONNECTION:
                title = "We can't reach your smart plug!"
                body = f'Your {data["app_name"]} is currently disconnected. Check its connection and fix it for better recommendations'
            case NotifType.GOAL:
                title = "Monthly Energy Goal"
                body = f"You're close to reach {data['percentage']}% of your monthly energy goal."
            case NotifType.PEAK:
                title = "Peak Usage Alert!"
                body = f'Try to postpone using {data["app_name"]} after 5 PM. Click here to turn it off.'
            case NotifType.PHANTOM:
                title = "Phantom Mode Active!"
                body = (
                    f'{data["app_name"]} is in phantom mode. Click here to turn it off.'
                )
            case NotifType.BASELINE:
                title = "Appliance Energy Consumption Increased!"
                body = f'{data["app_name"]} is used more than it should today. Try to use it less.'

        return title, body

    def notify(self, user, type, data={}):
        """
        Send a notification to a user.
        Args:
            user (str): The user's identifier.
            type (NotifType): The type of notification.
            data (dict, optional): Additional data for customizing the message.
        Returns:
            list: List of all responses
        """
        # Get the user's registration token from the database
        self.logger.info(
            f"Sending a notification:\nuser: {user}\ntype: {type}\ndata: {data}"
        )
        devices = self.db.get_doc(
            "Users", {"_id": ObjectId(user)}, {"notified_devices": 1}
        )
        devices = devices.get("notified_devices", [])
        title, body = self.map_message(type, data)
        responses = []
        # Log the notification
        self.logger.info(f"notify: {type} {data}")
        for dev in devices:
            try:
                alert = messaging.ApsAlert(title=title, body=body)
                aps = messaging.Aps(alert=alert, sound="default")
                payload = messaging.APNSPayload(aps)
                token = dev["fcm_token"]
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data={
                        "title": title,
                        "body": body,
                    },
                    token=token,
                    apns=messaging.APNSConfig(payload=payload),
                )
                response = messaging.send(message)
                self.logger.info(f"Notification sent with response: {response}")
            except:
                response = False
                self.logger.info("Notification failed to send")
            responses.append(response)
        return responses