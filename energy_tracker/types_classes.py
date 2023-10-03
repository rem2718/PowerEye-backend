from enum import Enum

class PlugType(Enum):
    MEROSS = 1
    TUYA = 2
 

class EType(Enum):
    NONE = 1
    SHIFTABLE = 2
    PHANTOM = 3 #all phantom are shiftable