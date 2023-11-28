from enum import Enum
    
class EType(Enum):
    NONE = 1
    SHIFTABLE = 2
    PHANTOM = 3

class ApplianceType(Enum):
    COOLER = 1
    LIGHTING = 2
    HEATER = 3
    COOKER_MAKER = 4
    BLENDER = 5
    ALEXA = 6
    HAIR_DRYER = 7
    CAMERA = 8
    WASHING_MACHINE = 9
    IRON = 10
    VACUUM_CLEANER = 11
    AIR_PURIFIER = 12
    GAMES = 13
    DISPLAYER = 14
    AUDIO_OUTPUT = 15
    PRINTER = 16
    CHARGER = 17
    RECEIVER = 18
    SPORTS_MACHINE = 19
    




class PlugType(Enum):
    MEROSS = 1
    TUYA = 2