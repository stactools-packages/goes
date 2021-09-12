from enum import Enum


class OrbitalSlot(Enum):
    EAST = "GOES-East"
    WEST = "GOES-West"
    TEST = "GOES-Test"
    STORAGE = "GOES-Storage"


class PlatformId(Enum):
    G16 = "G16"
    G17 = "G17"


class ProductionEnvironment(Enum):
    OE = "OE"
    ITE = "ITE"
    DE = "DE"


class ProductionDataSource(Enum):
    REALTIME = "Realtime"
    SIMULATED = "Simulated"
    PLAYBACK = "Playback"
    TEST = "Test"
    NA = "n/a"


class ImageType(Enum):
    FULL_DISK = "Full Disk"
    CONUS = "CONUS"
    MESOSCALE = "Mesoscale"


class Mode(Enum):
    ABI_MODE_3 = "ABI Mode 3"
    ABI_MODE_4 = "ABI Mode 4"
    ABI_MODE_6 = "ABI Mode 6"


class MesoscaleImageNumber(Enum):
    ONE = 1
    TWO = 2
