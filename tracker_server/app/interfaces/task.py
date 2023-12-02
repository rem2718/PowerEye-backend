from abc import ABC, abstractmethod

from app.external_dependencies.fcm import FCM
from app.interfaces.db import DB


class Task(ABC):
    """
    Abstract base class for Task objects.
    """

    @abstractmethod
    def __init__(self, id: str, db: DB, fcm: FCM, additional=None):
        """
        Constructor for the Task class.
        Args:
            id (str): A unique identifier for the user.
            db (DB): An instance of the DB interface for database interaction.
            fcm (FCM): An instance of the FCM interface for push notifications.
            additional (Any, optional): Additional data or parameters for the task.
        """
        pass

    @abstractmethod
    def run(self):
        """
        Execute the task.
        """
        pass
