"""
enums.py - Enumeration definitions for appliance and smart plug types.

This module defines several Enum classes to represent different types of 
energies, appliances and smart plug connections.
"""
from enum import Enum

class EType(Enum):
    """Enumeration representing types of Energy types of appliances."""
    NONE = 1
    SHIFTABLE = 2
    PHANTOM = 3

class ApplianceType(Enum):
    """Enumeration representing types of appliances."""
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
    """Enumeration representing types of smart plug connections."""
    MEROSS = 1
    TUYA = 2
