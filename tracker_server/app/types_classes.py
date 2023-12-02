from enum import Enum


class PlugType(Enum):
    """
    Enumeration representing types (brands) of smart plugs' clouds.
    Attributes:
        MEROSS (int): Meross Cloud (main).
        TUYA (int): Tuya Cloud (additional).
    """

    MEROSS = 1
    TUYA = 2


class EType(Enum):
    """
    Enumeration representing energy types of devices.
    Attributes:
        NONE (int): Represents a device of type "NONE."
        SHIFTABLE (int): Represents a shiftable device.
        PHANTOM (int): Represents a phantom device (all phantom devices are shiftable).
    """

    NONE = 1
    SHIFTABLE = 2
    PHANTOM = 3


class NotifType(Enum):
    """
    Enumeration representing types of notifications.
    Attributes:
        CREDS (int): Represents a notification related to wrong credentials.
        DISCONNECTION (int): Represents a device disconnection related notification.
        GOAL (int): Represents an energy goal-related notification.
        PEAK (int): Represents a peak time-related notification.
        PHANTOM (int): Represents a phantom mode-related notification.
        BASELINE (int): Represents a baseline threshold-related notification.
    """

    CREDS = 1
    DISCONNECTION = 2
    GOAL = 3
    PEAK = 4
    PHANTOM = 5
    BASELINE = 6
