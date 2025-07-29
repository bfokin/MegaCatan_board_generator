from PyQt6.QtGui import QColor

# All default values come from the classic base game of catan.

RESOURCE_COLORS = {
    "water": QColor(64, 164, 223),
    "desert": QColor(0, 0, 0),
    "wood": QColor(34, 139, 34),
    "brick": QColor(232, 87, 9),
    "wheat": QColor(240, 230, 140),
    "ore": QColor(150, 150, 150),
    "sheep": QColor(255, 255, 255),
}

LAND_RESOURCES = ["sheep", "wood", "wheat", "brick", "ore", "desert"]


LAND_RESOURCE_RATIOS = {
    "desert": 1, 
    "ore"   : 3,
    "brick" : 3,
    "wheat" : 4,
    "sheep" : 4,
    "wood"  : 4
}

NUMBER_RATIOS = {
    2   : 1,
    3   : 2,
    4   : 2,
    5   : 2,
    6   : 2,
    8   : 2,
    9   : 2,
    10  : 2,
    11  : 2,
    12  : 1
}

RED_NUMBERS = [6, 8]

HARBOR_SYMBOLS = {
    "generic": "3 : 1",
    "sheep": "S",
    "wood": "W",
    "wheat": "Wh",
    "ore": "O",
    "brick": "B"
}

HARBOR_RATIOS = {
    "generic"   : 4,
    "sheep"     : 1,
    "wood"      : 1,
    "wheat"     : 1,
    "ore"       : 1,
    "brick"     : 1
}