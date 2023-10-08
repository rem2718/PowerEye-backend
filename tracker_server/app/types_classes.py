from enum import Enum
class PlugType(Enum):
    MEROSS = 1
    TUYA = 2
class EType(Enum):
    NONE = 1
    SHIFTABLE = 2
    PHANTOM = 3 #all phantom are shiftable

class NotifType(Enum):
    CREDS = 1
    DISCONNECTION = 2
    GOAL = 3
    PEAK = 4
    PHANTOM = 5
    BASELINE = 6
