from enum import Enum

class Mode(Enum):
    DAILY = "DAILY"
    TRACK = "TRACK"
    MUD = "MUD"
    MANUAL = "MANUAL"

MODE_ORDER = [
    Mode.DAILY,
    Mode.TRACK,
    Mode.MUD,
    Mode.MANUAL,
]

LEGACY_MODE_MAP = {
    "COMFORT": "DAILY",
    "DYNAMIC": "TRACK",
    "RACE": "TRACK",
    "DRIFT": "TRACK",
    "OFFROAD": "MUD",
}
