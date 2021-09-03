import dateutil
import math
import os.path
from tempfile import TemporaryDirectory
import unittest

from shapely.geometry import shape
from pystac import MediaType
from pystac.extensions.projection import ProjectionExtension

from stactools.goes import stac, __version__
from tests import test_data, CMIP_FILE_NAME, CMIP_FULL_FILE_NAME


class CreateItemTest(unittest.TestCase):
    def test_create_item(self):
        path = test_data.get_external_data(CMIP_FILE_NAME)
        item = stac.create_item(path)
        self.assertEqual(
            item.id,
            "OR_ABI-L2-CMIPM1-M6C02_G16_s20211231619248_e20211231619306_c20211231619382"
        )
        self.assertTrue(item.geometry)
        self.assertTrue(item.bbox)
        self.assertEqual(item.datetime,
                         dateutil.parser.parse("2021-05-03T16:19:38.2Z"))
        self.assertEqual(item.common_metadata.start_datetime,
                         dateutil.parser.parse("2021-05-03T16:19:24.8Z"))
        self.assertEqual(item.common_metadata.end_datetime,
                         dateutil.parser.parse("2021-05-03T16:19:30.6Z"))
        self.assertTrue(
            "https://stac-extensions.github.io/processing/v1.0.0/schema.json"
            in item.stac_extensions)
        self.assertDictEqual(item.properties["processing:software"],
                             {"stactools-goes": __version__})
        self.assertEqual(item.properties["goes:production-site"], "NSOF")
        self.assertEqual(item.properties["goes:production-environment"], "OE")
        self.assertEqual(item.properties["goes:orbital-slot"], "GOES-East")
        self.assertEqual(item.properties["goes:platform-id"], "G16")
        self.assertEqual(item.properties["goes:instrument-type"],
                         "GOES R Series Advanced Baseline Imager")
        self.assertEqual(item.properties["goes:scene-id"], "Mesoscale")
        self.assertEqual(item.properties["goes:instrument-id"], "FM1")
        self.assertEqual(item.properties["goes:timeline-id"], "ABI Mode 6")
        self.assertEqual(item.properties["goes:production-data-source"],
                         "Realtime")
        self.assertEqual(item.properties["goes:id"],
                         "68870b76-0238-4542-aeb2-a035f93990ed")

        data = item.assets["data"]
        self.assertEqual(data.href, path)
        self.assertEqual(data.title, "ABI L2 Cloud and Moisture Imagery")
        self.assertEqual(data.media_type, "application/netcdf")
        self.assertEqual(data.roles, ["data"])

        projection = ProjectionExtension.ext(item)
        self.assertIsNone(projection.epsg)
        self.assertIsNotNone(projection.wkt2)
        self.assertIsNotNone(projection.shape, [2000, 2000])
        expected_transform = [
            501.0043288718852, 0.0, -2224459.203445637, 0.0,
            -501.0043288718852, 4068155.14931683, 0.0, 0.0, 1.0
        ]
        for actual, expected in zip(projection.transform, expected_transform):
            self.assertAlmostEqual(actual, expected, delta=1e-4)

        item.validate()

    def test_read_href_modifier(self):
        did_it = False

        def modify_href(href: str) -> str:
            nonlocal did_it
            did_it = True
            return href

        path = test_data.get_external_data(CMIP_FILE_NAME)
        _ = stac.create_item(path, modify_href)
        self.assertTrue(did_it)

    def test_cog_directory(self):
        path = test_data.get_external_data(CMIP_FILE_NAME)
        with TemporaryDirectory() as tmp_dir:
            item = stac.create_item(path, cog_directory=tmp_dir)
            cog_asset = item.assets["CMI"]
            self.assertTrue(os.path.exists(cog_asset.href))
            self.assertEqual(
                cog_asset.title,
                "ABI L2+ Cloud and Moisture Imagery reflectance factor")
            self.assertEqual(cog_asset.roles, ["data"])
            self.assertEqual(cog_asset.media_type, MediaType.COG)

    def test_different_product(self):
        path = test_data.get_path(
            "data-files/"
            "OR_ABI-L2-LSTM2-M6_G16_s20211381700538_e20211381700595_c20211381701211.nc"
        )
        item = stac.create_item(path)
        item.validate()

    def test_full_product_geometry(self):
        # https://github.com/stactools-packages/goes/issues/4
        path = test_data.get_external_data(CMIP_FULL_FILE_NAME)
        item = stac.create_item(path)
        geometry = shape(item.geometry)
        self.assertFalse(math.isnan(geometry.area),
                         f"This geometry has a NaN area: {geometry}")
