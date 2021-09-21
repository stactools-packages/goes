import logging
import sys

from stactools.testing import TestData

CMIP_FILE_NAME = (
    "OR_ABI-L2-CMIPM1-M6C02_G16_s20211231619248_e20211231619306_c20211231619382.nc"
)
CMIP_FULL_FILE_NAME = (
    "OR_ABI-L2-CMIPF-M6C02_G16_s20210201540193_e20210201549501_c20210201549575.nc"
)
MCMIP_FILE_NAME = (
    "OR_ABI-L2-MCMIPM1-M6_G16_s20211451800267_e20211451800324_c20211451800407.nc"
)
CORRUPT_FILE_NAME = (
    "OR_ABI-L2-MCMIPC-M6_G17_s20193431636197_e20193431638581_c20193431640028.nc"
)
NO_LONG_DESC = (
    "OR_ABI-L2-FDCC-M3_G16_s20173481837220_e20173481839593_c20173481840255.nc")

PC_MCMIP_F = (
    "OR_ABI-L2-MCMIPF-M3_G16_s20180100500410_e20180100511183_c20180100511270.nc"
)

PC_FDC_C = (
    "OR_ABI-L2-FDCC-M6_G17_s20211451831177_e20211451833549_c20211451834144.nc")

EXTERNAL_DATA = {
    CMIP_FILE_NAME: {
        "url":
        ("https://noaa-goes16.s3.amazonaws.com/ABI-L2-CMIPM/2021/123/16"
         "/OR_ABI-L2-CMIPM1-M6C02_G16_s20211231619248_e20211231619306_c20211231619382.nc"
         ),
        "compress":
        "none",
    },
    CMIP_FULL_FILE_NAME: {
        "url":
        ("https://noaa-goes16.s3.amazonaws.com/ABI-L2-CMIPF"
         "/2021/020/15/OR_ABI-L2-CMIPF-M6C02_G16_s20210201540193_e20210201549501_c20210201549575.nc"
         ),
        "compress":
        "none",
    },
    MCMIP_FILE_NAME: {
        "url":
        ("https://noaa-goes16.s3.amazonaws.com/ABI-L2-MCMIPM/2021/145/18/"
         "OR_ABI-L2-MCMIPM1-M6_G16_s20211451800267_e20211451800324_c20211451800407.nc"
         ),
        "compress":
        "none",
    },
    CORRUPT_FILE_NAME: {
        "url":
        ("https://noaa-goes17.s3.amazonaws.com/ABI-L2-MCMIPC/2019/343/16/"
         "OR_ABI-L2-MCMIPC-M6_G17_s20193431636197_e20193431638581_c20193431640028.nc"
         ),
        "compress":
        "none",
    },
    NO_LONG_DESC: {
        "url":
        ("https://goeseuwest.blob.core.windows.net/noaa-goes16/"
         "ABI-L2-FDCC/2017/348/18/"
         "OR_ABI-L2-FDCC-M3_G16_s20173481837220_e20173481839593_c20173481840255.nc"
         ),
        "planetary_computer":
        True,
    },
    PC_MCMIP_F: {
        "url":
        ("https://goeseuwest.blob.core.windows.net/noaa-goes16/"
         "ABI-L2-MCMIPF/2018/010/05/"
         "OR_ABI-L2-MCMIPF-M3_G16_s20180100500410_e20180100511183_c20180100511270.nc"
         ),
        "planetary_computer":
        True
    },
    PC_FDC_C: {
        "url":
        ("https://goeseuwest.blob.core.windows.net/noaa-goes17/"
         "ABI-L2-FDCC/2021/145/18/"
         "OR_ABI-L2-FDCC-M6_G17_s20211451831177_e20211451833549_c20211451834144.nc"
         ),
        "planetary_computer":
        True
    }
}

test_data = TestData(__file__, EXTERNAL_DATA)


class TestLogging:
    _set: bool = False

    @staticmethod
    def setup_logging() -> None:
        if not TestLogging._set:
            for package in ["tests", "stactools"]:
                logger = logging.getLogger(package)
                logger.setLevel(logging.INFO)
                formatter = logging.Formatter(
                    "[%(levelname)s] %(asctime)s - %(message)s")

                ch = logging.StreamHandler(sys.stdout)
                ch.setLevel(logging.INFO)
                ch.setFormatter(formatter)
                logger.addHandler(ch)


TestLogging.setup_logging()
