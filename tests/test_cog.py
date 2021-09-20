import os.path
from tempfile import TemporaryDirectory
import unittest

from stactools.goes import cog, CogifyError
from tests import CORRUPT_FILE_NAME, test_data, CMIP_FILE_NAME


class CogTest(unittest.TestCase):
    def test_cogify(self):
        path = test_data.get_external_data(CMIP_FILE_NAME)
        with TemporaryDirectory() as directory:
            cogs = cog.cogify(nc_href=path, directory=directory)

            data_path = cogs["CMI"]
            self.assertEqual(
                os.path.basename(data_path),
                os.path.splitext(os.path.basename(path))[0] + "_CMI.tif")

            dqf_path = cogs["DQF"]
            self.assertEqual(
                os.path.basename(dqf_path),
                os.path.splitext(os.path.basename(path))[0] + "_DQF.tif")

    def test_cogify_corrupt(self):
        path = test_data.get_external_data(CORRUPT_FILE_NAME)
        with TemporaryDirectory() as directory:
            with self.assertRaises(CogifyError):
                cog.cogify(nc_href=path, directory=directory)
