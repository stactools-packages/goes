import os.path
from tempfile import TemporaryDirectory
import unittest

from stactools.goes import Dataset, CogifyError
from tests import CORRUPT_FILE_NAME, NO_LONG_DESC, test_data, CMIP_FILE_NAME


class DatasetTest(unittest.TestCase):
    def test_cogify(self):
        path = test_data.get_external_data(CMIP_FILE_NAME)
        dataset = Dataset(path)
        with TemporaryDirectory() as directory:
            cogs = dataset.cogify(directory)

            data_path = cogs["CMI"]
            self.assertEqual(
                os.path.basename(data_path),
                os.path.splitext(os.path.basename(path))[0] + "_CMI.tif")

            dqf_path = cogs["DQF"]
            self.assertEqual(
                os.path.basename(dqf_path),
                os.path.splitext(os.path.basename(path))[0] + "_DQF.tif")

    def test_read_href_modifier(self):
        did_it = False

        def modify_href(href: str) -> str:
            nonlocal did_it
            did_it = True
            return href

        path = test_data.get_external_data(CMIP_FILE_NAME)
        Dataset(path, read_href_modifier=modify_href)
        self.assertTrue(did_it)

    def test_cog_file_names(self):
        path = test_data.get_external_data(CMIP_FILE_NAME)
        dataset = Dataset(path)
        cog_file_names = dataset.cog_file_names()
        self.assertEqual(
            set(cog_file_names),
            set([
                "OR_ABI-L2-CMIPM1-M6C02_G16_s20211231619248_e20211231619306_c20211231619382_CMI.tif",  # noqa
                "OR_ABI-L2-CMIPM1-M6C02_G16_s20211231619248_e20211231619306_c20211231619382_DQF.tif"
            ]))

    def test_cogify_corrupt(self):
        path = test_data.get_external_data(CORRUPT_FILE_NAME)
        dataset = Dataset(path)
        with TemporaryDirectory() as directory:
            with self.assertRaises(CogifyError):
                dataset.cogify(directory)

    def test_read_file_with_no_long_description(self):
        path = test_data.get_external_data(NO_LONG_DESC)
        dataset = Dataset(path)
        self.assertTrue(dataset.variables)

    def test_satellite_number(self):
        path = test_data.get_external_data(CMIP_FILE_NAME)
        dataset = Dataset(path)
        self.assertEqual(dataset.satellite_number, 16)
