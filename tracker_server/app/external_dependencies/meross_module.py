from datetime import datetime, timedelta
import logging

from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager

from app.interfaces.plug import Plug


class Meross(Plug):
    """
    Meross for smart plug cloud interaction.
    This class provides methods for controlling Meross smart plug devices, including logging in,
    updating credentials, retrieving devices, and getting device information.

    Attributes:
        day (timedelta): Time interval for daily updates.
        email (str): User's email for Meross account.
        client (MerossHttpClient): Meross HTTP client instance.
        manager (MerossManager): Meross manager instance.
        loggedin (bool): Flag to indicate if the user is logged in.
        first (bool): Flag to indicate if it's the first login.
        prev (datetime): Previous timestamp for daily updates.
        logger (logging.Logger): The logger for logging messages.
    """

    day = timedelta(hours=20)  # to stay on the safe side

    def __init__(self, data):
        """
        Constructor for the Meross class.
        Args:
            data (dict): User information including email.
        """
        self.email = data["email"]
        self.client = None
        self.manager = None
        self.loggedin = None
        self.first = True
        self.prev = datetime.now()
        self.logger = logging.getLogger(__name__)

    async def _inner_login(self, password=None):
        """
        Perform the inner login process for Meross.
        Args:
            password (str, optional): Password for authentication.
        """
        try:
            if password != None:
                self.password = password
            self.client = await MerossHttpClient.async_from_user_password(
                email=self.email, password=self.password
            )
            self.manager = MerossManager(http_client=self.client)
            self.loggedin = True
        except Exception as e:
            self.loggedin = False
            self.logger.error("meross login error", exc_info=True)

    async def _logout(self):
        """
        Log out from the Meross account.
        """
        try:
            self.manager.close()
            await self.client.async_logout()
        except:
            self.logger.error("meross logout error")

    async def update_creds(self):
        """
        Update Meross credentials.
        """
        await self._logout()
        await self._inner_login()

    async def _daily_update_creds(self):
        """
        Perform daily update of Meross credentials.
        """
        current = datetime.now()
        if current - self.prev >= Meross.day:
            await self.update_creds()
            self.prev += Meross.day

    async def login(self, password):
        """
        Log in to the Meross device.
        Args:
            password (str): Password for authentication.

        Returns:
            bool: True if the login is successful, otherwise False.
        """
        if self.first:
            await self._inner_login(password)
            self.first = False
        elif not self.loggedin:
            await self._inner_login(password)
        await self._daily_update_creds()
        return self.loggedin

    async def get_devices(self):
        """
        Retrieve a list of Meross devices.
        Returns:
            list: A list of Meross devices.
        """
        await self.manager.async_init()
        await self.manager.async_device_discovery()
        meross_devices = self.manager.find_devices(device_type="mss310")
        self.logger.info(f"{len(meross_devices)} devices")
        return meross_devices

    async def get_id(self, dev):
        """
        Get the unique identifier for a Meross device.
        Args:
            dev: Device object.
        Returns:
            str: The unique identifier of the device.
        """
        return str(dev.uuid)

    async def get_info(self, dev):
        """
        Get information about a Meross device.
        Args:
            dev: Device information.
        Returns:
            tuple: A tuple containing device status (on/off), connection status, and power consumption.
        """
        try:
            await dev.async_update(timeout=2)
            on_off = dev.is_on()
            connection_status = dev.online_status.value == 1
            reading = await dev.async_get_instant_metrics(timeout=5)
            if reading.power < 0:
                reading.power = 0
            return on_off, connection_status, reading.power
        except Exception:
            self.logger.error("status error", exc_info=True)
            return None, False, None
