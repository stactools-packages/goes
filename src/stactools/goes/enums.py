import enum
from enum import Enum


class ImageType(Enum):
    FULL_DISK = enum.auto()
    CONUS = enum.auto()
    MESOSCALE = enum.auto()


class Mode(Enum):
    ABI_MODE_3 = 3
    ABI_MODE_4 = 4
    ABI_MODE_6 = 6
