from abc import ABC, abstractmethod


class Plug(ABC):
    """
    Abstract base class for smart plugs cloud interactions.
    """

    @abstractmethod
    def __init__(self, user: dict):
        """
        Constructor for the Plug class.
        Args:
            user (dict): A dictionary containing user information.
        """
        pass

    @abstractmethod
    def login(self, password: str = None) -> bool:
        """
        Attempt to log in to the smart plugs cloud.
        Args:
            password (str, optional): password for authentication.
        Returns:
            bool: True if the login is successful, otherwise False.
        """
        pass

    @abstractmethod
    def update_creds(self):
        """
        Update the credentials used to log in to the smart plugs cloud.
        """
        pass

    @abstractmethod
    def get_devices(self) -> list:
        """
        Retrieve a list of devices(smart plugs) associated with the cloud.
        Returns:
            list: A list of device objects.
        """
        pass

    @abstractmethod
    def get_id(self, dev) -> str:
        """
        Get the unique identifier for a given device.
        Args:
            dev: The device object for which to retrieve the identifier.
        Returns:
            str: The unique identifier of the device.
        """
        pass

    @abstractmethod
    def get_info(self, dev) -> tuple[bool, bool, float]:
        """
        Get information about a specific device.
        Args:
            dev: The device for which to retrieve information.
        Returns:
            tuple: A tuple containing information about the device.
                - bool: The ON/OFF status of the device.
                - bool: The connectivity status of the device.
                - float: The power consumption of the device.
        """
        pass
