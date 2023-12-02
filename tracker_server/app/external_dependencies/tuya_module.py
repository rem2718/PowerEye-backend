import logging
import os

from dotenv import load_dotenv
import tinytuya

from app.interfaces.plug import Plug


class Tuya(Plug):
    """
    Tuya for smart plugs cloud interaction.
    This class provides methods for controlling Tuya smart plug devices, including logging in,
    updating credentials, retrieving devices, and getting device information.

    Attributes:
        API_KEY (str): Tuya CLoud API key.
        API_SECRET (str): Tuya Cloud API secret.
        dev1 (str): Device identifier, any device ID to specify the user.
        first (bool): Flag to indicate if it's the first login.
        cloud (tinytuya.Cloud): Tuya Cloud instance.
        logger (logging.Logger): The logger for logging messages.
    """

    def __init__(self, data):
        """
        Constructor for the Tuya class.
        Args:
            data (dict): User information including device details.
        """
        load_dotenv(os.path.join(".secrets", ".env"))
        self.API_KEY = os.getenv("API_KEY")
        self.API_SECRET = os.getenv("API_SECRET")
        self.dev1 = data["dev1"]
        self.first = True
        self.logger = logging.getLogger(__name__)

    def update_creds(self):
        """
        Update Tuya credentials (Not importnant).
        """
        pass

    def login(self, password=None):
        """
        Log in to the Tuya device.

        Args:
            password (str, optional): not important here.

        Returns:
            bool: True if the login is successful, otherwise False.
        """
        if self.first:
            self.cloud = tinytuya.Cloud(
                apiRegion="eu",
                apiKey=self.API_KEY,
                apiSecret=self.API_SECRET,
                apiDeviceID=self.dev1,
            )
            self.first = False
        return True

    def get_devices(self):
        """
        Retrieve a list of Tuya devices.
        Returns:
            list: A list of Tuya devices.
        """
        tuya_devices = self.cloud.getdevices()
        self.logger.info(f"{len(tuya_devices)} devices")
        return tuya_devices

    def get_id(self, dev):
        """
        Get the unique identifier for a Tuya device.
        Args:
            dev (dict): Device obejct.
        Returns:
            str: The unique identifier of the device.
        """
        return dev["id"]

    def get_info(self, dev):
        """
        Get information about a Tuya device.
        Args:
            dev (dict): Device information.
        Returns:
            tuple: A tuple containing device status (on/off), connection status, and power consumption.
        """
        try:
            connection_status = self.cloud.getconnectstatus(dev["id"])
            result = self.cloud.getstatus(dev["id"])
            power = (result["result"][4]["value"]) / 10.0
            if power < 0:
                power = 0
            on_off = result["result"][0]["value"]
            return on_off, connection_status, power
        except:
            self.logger.error("status error", exc_info=True)
            return None, False, None
