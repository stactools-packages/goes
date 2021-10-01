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

PC_CMIP_M_01 = (
    "OR_ABI-L2-CMIPM1-M6C01_G17_s20200111504255_e20200111504313_c20200111504367.nc"
)
PC_CMIP_M_02 = (
    "OR_ABI-L2-CMIPM1-M6C02_G16_s20211451816238_e20211451816295_c20211451816361.nc"
)
PC_CMIP_M_03 = (
    "OR_ABI-L2-CMIPM1-M6C03_G16_s20211451810267_e20211451810324_c20211451810387.nc"
)
PC_CMIP_M_04 = (
    "OR_ABI-L2-CMIPM1-M6C04_G16_s20211451811238_e20211451811295_c20211451811353.nc"
)
PC_CMIP_M_05 = (
    "OR_ABI-L2-CMIPM1-M6C05_G16_s20211451800267_e20211451800324_c20211451800393.nc"
)
PC_FDC_C = (
    "OR_ABI-L2-FDCC-M6_G17_s20211451831177_e20211451833549_c20211451834144.nc")
PC_LST_F = (
    "OR_ABI-L2-LSTF-M3_G17_s20190090500381_e20190090511148_c20190090511362.nc")
PC_LST_C = (
    "OR_ABI-L2-LSTC-M6_G17_s20210040301178_e20210040303551_c20210040304296.nc")
PC_LST_M = (
    "OR_ABI-L2-LSTM2-M6_G17_s20211451800593_e20211451801050_c20211451801259.nc"
)
PC_MCMIP_F = (
    "OR_ABI-L2-MCMIPF-M3_G16_s20180100500410_e20180100511183_c20180100511270.nc"
)
PC_MCMIP_F_17 = (
    "OR_ABI-L2-MCMIPF-M6_G17_s20212582320319_e20212582329396_c20212582329540.nc"
)
PC_MCMIP_C = (
    "OR_ABI-L2-MCMIPC-M6_G16_s20211451801159_e20211451803532_c20211451804034.nc"
)
PC_MCMIP_M = (
    "OR_ABI-L2-MCMIPM2-M6_G17_s20200211641555_e20200211642024_c20200211642086.nc"
)
PC_RRQPE_F = (
    "OR_ABI-L2-RRQPEF-M6_G17_s20210040310320_e20210040319387_c20210040319489.nc"
)
PC_SST_F = (
    "OR_ABI-L2-SSTF-M6_G17_s20193550800326_e20193550859393_c20193550904140.nc")

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
    PC_MCMIP_F_17: {
        "url":
        ("https://goeseuwest.blob.core.windows.net/noaa-goes17/"
         "ABI-L2-MCMIPF/2021/258/23/"
         "OR_ABI-L2-MCMIPF-M6_G17_s20212582320319_e20212582329396_c20212582329540.nc"
         ),
        "planetary_computer":
        True
    },
    PC_MCMIP_C: {
        "url":
        ("https://goeseuwest.blob.core.windows.net/noaa-goes16/"
         "ABI-L2-MCMIPC/2021/145/18/"
         "OR_ABI-L2-MCMIPC-M6_G16_s20211451801159_e20211451803532_c20211451804034.nc"
         ),
        "planetary_computer":
        True
    },
    PC_MCMIP_M: {
        "url":
        ("https://goeseuwest.blob.core.windows.net/noaa-goes17/"
         "ABI-L2-MCMIPM/2020/021/16/"
         "OR_ABI-L2-MCMIPM2-M6_G17_s20200211641555_e20200211642024_c20200211642086.nc"
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
    },
    PC_CMIP_M_01: {
        "url":
        ("https://goeseuwest.blob.core.windows.net/noaa-goes17/"
         "ABI-L2-CMIPM/2020/011/15/"
         "OR_ABI-L2-CMIPM1-M6C01_G17_s20200111504255_e20200111504313_c20200111504367.nc"
         ),
        "planetary_computer":
        True
    },
    PC_CMIP_M_02: {
        "url":
        ("https://goeseuwest.blob.core.windows.net/noaa-goes16/"
         "ABI-L2-CMIPM/2021/145/18/"
         "OR_ABI-L2-CMIPM1-M6C02_G16_s20211451816238_e20211451816295_c20211451816361.nc"
         ),
        "planetary_computer":
        True
    },
    PC_CMIP_M_03: {
        "url":
        ("https://goeseuwest.blob.core.windows.net/noaa-goes16/"
         "ABI-L2-CMIPM/2021/145/18/"
         "OR_ABI-L2-CMIPM1-M6C03_G16_s20211451810267_e20211451810324_c20211451810387.nc"
         ),
        "planetary_computer":
        True
    },
    PC_CMIP_M_04: {
        "url":
        ("https://goeseuwest.blob.core.windows.net/noaa-goes16/"
         "ABI-L2-CMIPM/2021/145/18/"
         "OR_ABI-L2-CMIPM1-M6C04_G16_s20211451811238_e20211451811295_c20211451811353.nc"
         ),
        "planetary_computer":
        True
    },
    PC_CMIP_M_05: {
        "url":
        ("https://goeseuwest.blob.core.windows.net/noaa-goes16/"
         "ABI-L2-CMIPM/2021/145/18/"
         "OR_ABI-L2-CMIPM1-M6C05_G16_s20211451800267_e20211451800324_c20211451800393.nc"
         ),
        "planetary_computer":
        True
    },
    PC_LST_F: {
        "url":
        ("https://goeseuwest.blob.core.windows.net/noaa-goes17/"
         "ABI-L2-LSTF/2019/009/05/"
         "OR_ABI-L2-LSTF-M3_G17_s20190090500381_e20190090511148_c20190090511362.nc"
         ),
        "planetary_computer":
        True
    },
    PC_LST_C: {
        "url":
        ("https://goeseuwest.blob.core.windows.net/noaa-goes17/"
         "ABI-L2-LSTC/2021/004/03/"
         "OR_ABI-L2-LSTC-M6_G17_s20210040301178_e20210040303551_c20210040304296.nc"
         ),
        "planetary_computer":
        True
    },
    PC_LST_M: {
        "url":
        ("https://goeseuwest.blob.core.windows.net/noaa-goes17/"
         "ABI-L2-LSTM/2021/145/18/"
         "OR_ABI-L2-LSTM2-M6_G17_s20211451800593_e20211451801050_c20211451801259.nc"
         ),
        "planetary_computer":
        True
    },
    PC_RRQPE_F: {
        "url":
        ("https://goeseuwest.blob.core.windows.net/noaa-goes17/"
         "ABI-L2-RRQPEF/2021/004/03/"
         "OR_ABI-L2-RRQPEF-M6_G17_s20210040310320_e20210040319387_c20210040319489.nc"
         ),
        "planetary_computer":
        True
    },
    PC_SST_F: {
        "url":
        ("https://goeseuwest.blob.core.windows.net/noaa-goes17/"
         "ABI-L2-SSTF/2019/355/08/"
         "OR_ABI-L2-SSTF-M6_G17_s20193550800326_e20193550859393_c20193550904140.nc"
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
