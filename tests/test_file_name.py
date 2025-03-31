import unittest
from dataclasses import dataclass

from stactools.goes.enums import (
    ImageType,
    MesoscaleImageNumber,
    Mode,
    PlatformId,
    SystemEnvironment,
)
from stactools.goes.file_name import ABIL2FileName
from stactools.goes.product import ProductAcronym


@dataclass
class TestCase:
    __test__ = False

    file_name: str
    expected_result: ABIL2FileName


TEST_CASES = [
    TestCase(
        file_name=(
            "OR_ABI-L2-CMIPM1-M3C01_G17_s20190020100270_e20190020100327_c20190020100370.nc"
        ),
        expected_result=ABIL2FileName(
            system=SystemEnvironment.OR,
            product=ProductAcronym.CMIP,
            image_type=ImageType.MESOSCALE,
            mesoscale_number=MesoscaleImageNumber.ONE,
            mode=Mode.THREE,
            channel=1,
            platform=PlatformId.G17,
            cyclone_id=None,
            start_time="20190020100270",
            end_time="20190020100327",
            created_time="20190020100370",
        ),
    ),
    TestCase(
        file_name=(
            "OR_ABI-L2-FDCC-M3_G17_s20190060357191_e20190060359504_c20190060400028.nc"
        ),
        expected_result=ABIL2FileName(
            system=SystemEnvironment.OR,
            product=ProductAcronym.FDC,
            image_type=ImageType.CONUS,
            mesoscale_number=None,
            mode=Mode.THREE,
            channel=None,
            platform=PlatformId.G17,
            cyclone_id=None,
            start_time="20190060357191",
            end_time="20190060359504",
            created_time="20190060400028",
        ),
    ),
    TestCase(
        file_name=(
            "OR_ABI-L2-LSTF-M3_G16_s20190070400357_e20190070411123_c20190070411409.nc"
        ),
        expected_result=ABIL2FileName(
            system=SystemEnvironment.OR,
            product=ProductAcronym.LST,
            image_type=ImageType.FULL_DISK,
            mesoscale_number=None,
            mode=Mode.THREE,
            channel=None,
            platform=PlatformId.G16,
            cyclone_id=None,
            start_time="20190070400357",
            end_time="20190070411123",
            created_time="20190070411409",
        ),
    ),
    TestCase(
        file_name=(
            "OR_ABI-L2-MCMIPC-M6_G16_s20210131021157_e20210131023536_c20210131024090.nc"
        ),
        expected_result=ABIL2FileName(
            system=SystemEnvironment.OR,
            product=ProductAcronym.MCMIP,
            image_type=ImageType.CONUS,
            mesoscale_number=None,
            mode=Mode.SIX,
            channel=None,
            platform=PlatformId.G16,
            cyclone_id=None,
            start_time="20210131021157",
            end_time="20210131023536",
            created_time="20210131024090",
        ),
    ),
    TestCase(
        file_name=(
            "OR_ABI-L2-RRQPEF-M6_G17_s20200030830361_e20200030839427_c20200030839507.nc"
        ),
        expected_result=ABIL2FileName(
            system=SystemEnvironment.OR,
            product=ProductAcronym.RRQPE,
            image_type=ImageType.FULL_DISK,
            mesoscale_number=None,
            mode=Mode.SIX,
            channel=None,
            platform=PlatformId.G17,
            cyclone_id=None,
            start_time="20200030830361",
            end_time="20200030839427",
            created_time="20200030839507",
        ),
    ),
    # GOES-18
    TestCase(
        file_name=(
            "OR_ABI-L2-CMIPM1-M6C01_G18_s20222090000248_e20222090000305_c20222090000360.nc"
        ),
        expected_result=ABIL2FileName(
            system=SystemEnvironment.OR,
            product=ProductAcronym.CMIP,
            image_type=ImageType.MESOSCALE,
            mesoscale_number=MesoscaleImageNumber.ONE,
            mode=Mode.SIX,
            channel=1,
            platform=PlatformId.G18,
            cyclone_id=None,
            start_time="20222090000248",
            end_time="20222090000305",
            created_time="20222090000360",
        ),
    ),
    TestCase(
        file_name=(
            "OR_ABI-L2-MCMIPF-M6_G18_s20222090000172_e20222090009486_c20222090009581.nc"
        ),
        expected_result=ABIL2FileName(
            system=SystemEnvironment.OR,
            product=ProductAcronym.MCMIP,
            image_type=ImageType.FULL_DISK,
            mesoscale_number=None,
            mode=Mode.SIX,
            channel=None,
            platform=PlatformId.G18,
            cyclone_id=None,
            start_time="20222090000172",
            end_time="20222090009486",
            created_time="20222090009581",
        ),
    ),
    # GOES-19
    TestCase(
        file_name=(
            "OR_ABI-L2-CMIPM1-M6C01_G19_s20250010000280_e20250010000338_c20250010000394.nc"
        ),
        expected_result=ABIL2FileName(
            system=SystemEnvironment.OR,
            product=ProductAcronym.CMIP,
            image_type=ImageType.MESOSCALE,
            mesoscale_number=MesoscaleImageNumber.ONE,
            mode=Mode.SIX,
            channel=1,
            platform=PlatformId.G19,
            cyclone_id=None,
            start_time="20250010000280",
            end_time="20250010000338",
            created_time="20250010000394",
        ),
    ),
    TestCase(
        file_name=(
            "OR_ABI-L2-MCMIPF-M6_G19_s20250010000205_e20250010009519_c20250010010005.nc"
        ),
        expected_result=ABIL2FileName(
            system=SystemEnvironment.OR,
            product=ProductAcronym.MCMIP,
            image_type=ImageType.FULL_DISK,
            mesoscale_number=None,
            mode=Mode.SIX,
            channel=None,
            platform=PlatformId.G19,
            cyclone_id=None,
            start_time="20250010000205",
            end_time="20250010009519",
            created_time="20250010010005",
        ),
    ),
]


class ABIL2FileNameTest(unittest.TestCase):
    def test_parsing(self):
        for test_case in TEST_CASES:
            file_name = test_case.file_name
            expected = test_case.expected_result
            with self.subTest(file_name):
                actual = ABIL2FileName.from_str(file_name)
                self.assertEqual(actual, expected)
                self.assertEqual(actual.to_str(), file_name)
