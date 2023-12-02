from datetime import datetime, timedelta
from bson import ObjectId
import logging

from app.plug_controller import PlugController
from app.types_classes import NotifType
from app.interfaces.task import Task


class Collector(Task):
    """
    Collector task for collecting data from smart plug clouds.
    This class is responsible for collecting data from smart plug devices, checking device status, and notifying the user of disconnections.
    Attributes:
        min (timedelta): Time interval for data collection.
        user_id (str): User identifier.
        db: The database instance.
        fcm: The FCM (Firebase Cloud Messaging) instance.
        cloud: The smart plug controller instance.
        ts (datetime): Timestamp for data collection.
        notified (bool): Flag to indicate if the user has been notified for wrong credentials.
        flags (dict): Flags to track devices disconnections.
        logger (logging.Logger): The logger for logging messages.
    """

    min = timedelta(minutes=1)

    def __init__(self, id, db, fcm, additional: PlugController):
        """
        Constructor for the Collector class.
        Args:
            id: User identifier (not used).
            db: The database instance.
            fcm: The FCM (Firebase Cloud Messaging) instance.
            additional: The additional here is PlugController instance.
        """
        self.user_id = id
        self.db = db
        self.fcm = fcm
        self.cloud = additional
        self.ts = datetime.now() + timedelta(minutes=1)
        self.notified = False
        self.flags = {}
        self.logger = logging.getLogger(__name__)

    def _get_appliances(self):
        """
        Get the appliances associated with the user.
        Returns:
            dict: A dictionary mapping cloud IDs to appliance information.
        """
        map = {}
        projection = {
            "appliances._id": 1,
            "appliances.cloud_id": 1,
            "appliances.is_deleted": 1,
            "appliances.energy": 1,
            "appliances.name": 1,
        }
        appliances = self.db.get_doc(
            "Users", {"_id": ObjectId(self.user_id)}, projection
        )
        appliances = appliances["appliances"]
        for app in appliances:
            if app["is_deleted"]:
                continue
            map[app["cloud_id"]] = {
                "id": str(app["_id"]),
                "name": app["name"],
                "energy": app["energy"],
            }
        return map

    def _to_energy(self, prev_energy, power):
        """
        Calculate energy consumption.
        Args:
            prev_energy: Previous energy consumption.
            power: Current power consumption.
        Returns:
            float: Updated energy consumption.
        """
        if power == None:
            power = 0
        return prev_energy + (power / 1000) * (1 / 60)

    def _check_disconnected(self, id, name, connection_status):
        """
        Check if a device is disconnected and notify the user.
        Args:
            id: Device identifier.
            name: Device name.
            connection_status: Current connection status.
        """
        if not connection_status:
            if id not in self.flags or self.flags[id]:
                self.fcm.notify(
                    self.user_id, NotifType.DISCONNECTION, {"app_name": name}
                )
                self.flags[id] = False
        else:
            self.flags[id] = True

    def _notify_disconnected(self, apps_ids, app_map, updates):
        """
        Notify the user of disconnected devices (that are not detected at all from the cloud).

        Args:
            apps_ids: List of device identifiers.
            app_map: Mapping of cloud IDs to appliance information.
            updates: List of updates to be applied.
        Returns:
            list: Updated list of updates.
        """
        for cloud_id in apps_ids:
            id = app_map[cloud_id]["id"]
            if id not in self.flags or self.flags[id]:
                updates.append((id, {"connection_status": False}))
                name = app_map[cloud_id]["name"]
                self.fcm.notify(
                    self.user_id, NotifType.DISCONNECTION, {"app_name": name}
                )
                self.flags[id] = False
        return updates

    def _get_doc_updates(self, cloud_devices, app_map):
        """
        Get updates for documents and appliance statuses.
        Args:
            cloud_devices: List of smart plug devices.
            app_map: Mapping of cloud IDs to appliance information.
        Returns:
            dict: Updates for documents.
            list: List of updates to be applied.
        """
        doc = {}
        updates = []
        apps_ids = list(app_map.keys())
        for dev in cloud_devices:
            dev_id = self.cloud.get_id(dev)
            if dev_id not in app_map:
                continue
            apps_ids.remove(dev_id)
            id = app_map[dev_id]["id"]
            on_off, connection_status, power = self.cloud.get_info(dev)
            doc[id] = power
            energy = self._to_energy(app_map[dev_id]["energy"], doc[id])
            update = (
                id,
                {
                    "status": on_off,
                    "connection_status": connection_status,
                    "energy": energy,
                },
            )
            updates.append(update)
            self._check_disconnected(id, app_map[dev_id]["name"], connection_status)
        updates = self._notify_disconnected(apps_ids, app_map, updates)
        return doc, updates

    def _save_data(self, doc, updates):
        """
        Save collected data to the database.
        Args:
            doc: Data to be saved to the database.
            updates: List of updates to be applied.
        """
        doc["user"] = ObjectId(self.user_id)
        doc["timestamp"] = self.ts
        self.db.insert_doc("Powers", doc)
        self.db.update_appliances("Users", self.user_id, updates)
        self.logger.critical(f"cloud: {self.ts} -> done")
        self.ts += Collector.min

    def run(self):
        """
        Run the collector task to collect data and manage device status.
        """
        try:
            user = self.db.get_doc(
                "Users", {"_id": ObjectId(self.user_id)}, {"cloud_password": 1}
            )
            if self.cloud.login(user["cloud_password"]):
                self.notified = False
                app_map = self._get_appliances()
                if len(app_map):
                    cloud_devices = self.cloud.get_devices()
                    doc, updates = self._get_doc_updates(cloud_devices, app_map)
                    self._save_data(doc, updates)
            elif not self.notified:
                self.fcm.notify(self.user_id, NotifType.CREDS)
                self.notified = True
        except:
            self.logger.error("cloud error", exc_info=True)
            self.cloud.update_creds()
