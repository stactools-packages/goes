import os.path
import unittest
from tempfile import TemporaryDirectory

import rasterio
from rasterio.crs import CRS

from stactools.goes import CogifyError, cog
from tests import CMIP_FILE_NAME, CORRUPT_FILE_NAME, test_data


class CogTest(unittest.TestCase):
    def test_cogify(self):
        path = test_data.get_external_data(CMIP_FILE_NAME)
        with TemporaryDirectory() as directory:
            cogs = cog.cogify(nc_href=path, directory=directory)

            data_path = cogs["CMI"]
            self.assertEqual(
                os.path.basename(data_path),
                os.path.splitext(os.path.basename(path))[0] + "_CMI.tif",
            )

            dqf_path = cogs["DQF"]
            self.assertEqual(
                os.path.basename(dqf_path),
                os.path.splitext(os.path.basename(path))[0] + "_DQF.tif",
            )

    def test_cogify_reproject(self):
        path = test_data.get_external_data(CMIP_FILE_NAME)
        with TemporaryDirectory() as directory:
            cogs = cog.cogify(
                nc_href=path,
                directory=directory,
                target_srs="epsg:3857",
                additional_suffix="wm",
            )

            cmi_path = cogs["CMI"]
            self.assertEqual(
                os.path.basename(cmi_path),
                os.path.splitext(os.path.basename(path))[0] + "_CMI_wm.tif",
            )

            dqf_path = cogs["DQF"]
            self.assertEqual(
                os.path.basename(dqf_path),
                os.path.splitext(os.path.basename(path))[0] + "_DQF_wm.tif",
            )

            with rasterio.open(cmi_path) as ds:
                self.assertTrue(ds.crs == CRS.from_epsg(3857))

    def test_cogify_subset(self):
        path = test_data.get_external_data(CMIP_FILE_NAME)
        with TemporaryDirectory() as directory:
            cogs = cog.cogify(
                nc_href=path, directory=directory, variables_to_include=["DQF"]
            )

            self.assertNotIn("CMI", cogs)

            dqf_path = cogs["DQF"]
            self.assertEqual(
                os.path.basename(dqf_path),
                os.path.splitext(os.path.basename(path))[0] + "_DQF.tif",
            )

    def test_cogify_corrupt(self):
        path = test_data.get_external_data(CORRUPT_FILE_NAME)
        with TemporaryDirectory() as directory:
            with self.assertRaises(CogifyError):
                cog.cogify(nc_href=path, directory=directory)
