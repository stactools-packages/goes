from enum import Enum


class PlatformId(Enum):
    G16 = "G16"
    G17 = "G17"
    G18 = "G18"
    G19 = "G19"

    @staticmethod
    def to_stac_value(v: "PlatformId") -> str:
        if v == PlatformId.G16:
            return "GOES-16"
        elif v == PlatformId.G17:
            return "GOES-17"
        elif v == PlatformId.G18:
            return "GOES-18"
        elif v == PlatformId.G19:
            return "GOES-19"
        else:
            return v.value


class ProductionEnvironment(Enum):
    OE = "OE"
    ITE = "ITE"
    DE = "DE"


class SystemEnvironment(Enum):
    OR = "OR"
    """operational system real-time data"""

    OT = "OT"
    """operational system test data"""

    IR = "IR"
    """test system real-time data"""

    IT = "IT"
    """test system test data"""

    IP = "IP"
    """test system playback data"""

    IS = "IS"
    """test system simulated data"""


class ImageType(Enum):
    FULL_DISK = "F"
    """Full Disk coverage region.

    Near hemispheric earth region centered at the longitude of
    the sensing satellite.

    Values are strings as they are represented in GOES-R ABI L2 file names.
    """

    CONUS = "C"
    """
    Continental United States coverage region

    An approximately 3000 km x 5000 km region intended to cover
    the continental United States within the constraints of viewing
    angle from the sensing satellite.
    """

    MESOSCALE = "M"
    """Mesoscale coverage region.

    An approximately 1000 km x 1000 km dynamically centered region in the
    instrument’s field of regard. The particular coverage region associated
    with a mesoscale product is operator-selected to support high-rate
    temporal analysis of environmental conditions in regions of interest.
    """

    @staticmethod
    def to_stac_value(image_type: "ImageType") -> str:
        """Converts a ImageType Enum to the value represented in STAC"""
        if image_type == ImageType.FULL_DISK:
            return "FULL DISK"
        elif image_type == ImageType.CONUS:
            return "CONUS"
        elif image_type == ImageType.MESOSCALE:
            return "MESOSCALE"
        else:
            return image_type.value


class Mode(Enum):
    THREE = "3"
    """Mode 3

    Consists of one observation of the full disk scene of the earth,
    three observations of the continental United States (CONUS) scene,
    and thirty observations for each of two distinct mesoscale scenes
    every fifteen minutes, during nominal operations
    """

    FOUR = "4"
    """Mode 4

    Consists of the observation of the full disk scene every five minutes.
    """

    SIX = "6"
    """Mode 6

    Consists of one observation of the full disk scene of the earth,
    two observations of the continental United States (CONUS) scene,
    and twenty observations for each of two distinct mesoscale
    scenes every ten minutes, during nominal operations
    """


class MesoscaleImageNumber(Enum):
    ONE = "1"
    """Region 1"""

    TWO = "2"
    """Region 2"""


class ProductAcronym(Enum):
    ACHA = "ACHA"
    """Cloud Top Height"""

    ACHT = "ACHT"
    """Cloud Top Height"""

    ACM = "ACM"
    """Clear Sky Masks"""

    ACTP = "ACTP"
    """Clear Top Phase"""

    ADP = "ADP"
    """Aerosol Detection"""

    AOD = "AOD"
    """Aerosol Optical Depth"""

    CMIP = "CMIP"
    """Cloud Moisture & Imagery"""

    MCMIP = "MCMIP"
    """Cloud & Moisture Imagery Multiband"""

    COD = "COD"
    """Cloud Optical Depth"""

    CPS = "CPS"
    """Cloud Particle Size Distribution"""

    CTP = "CTP"
    """Cloud Top Pressure"""

    DMW = "DMW"
    """Derived Motion Winds for ABI bands 2, 7, 8, 9, 10 & 14"""

    DMWV = "DMWV"
    """Derived Motion Winds for ABI bands 8"""

    DSI = "DSI"
    """Derived Stability Indices"""

    DSR = "DSR"
    """Downward Shortwave Radiation: Surface"""

    FDC = "FDC"
    """Fire / Hot Spot Characterization"""

    FSC = "FSC"
    """Snow Cover"""

    HIE = "HIE"
    """Hurricane Intensity"""

    LST = "LST"
    """Land Surface (Skin) Temperature"""

    LVMP = "LVMP"
    """Legacy Vertical Moisture Profile"""

    LVTP = "LVTP"
    """Legacy Vertical Temperature Profile"""

    RRQPE = "RRQPE"
    """Rainfall Rate/QPE"""

    RSR = "RSR"
    """Reflected Shortwave Radiation: TOA"""

    SST = "SST"
    """Sea Surface (Skin) Temperature"""

    TPW = "TPW"
    """Total Precipitable Water"""

    VAA = "VAA"
    """Volcanic Ash: Detection & Height"""
