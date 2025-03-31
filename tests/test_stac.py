import dataclasses
import math
import os.path
import unittest
from datetime import datetime, timezone
from tempfile import TemporaryDirectory
from typing import Any, Callable, List

import planetary_computer
from pystac import MediaType
from pystac.extensions.eo import EOExtension
from pystac.extensions.projection import ProjectionExtension
from shapely.geometry import box, shape

from stactools.goes import __version__, stac
from stactools.goes.enums import ProductAcronym
from stactools.goes.errors import GOESMissingExtentError, GOESRProductHrefsError
from stactools.goes.file_name import ABIL2FileName
from stactools.goes.stac import ProductHrefs
from tests import (
    CMIP_FILE_NAME,
    CMIP_FULL_FILE_NAME,
    EXTERNAL_DATA,
    INVALID_LAT_LNG,
    MCMIP_FILE_NAME,
    PC_FDC_C,
    PC_LST_M,
    PC_MCMIP_C,
    PC_MCMIP_F,
    PC_MCMIP_F_17,
    test_data,
)
from tests.test_mpc import MicrosoftPCData

US_CENTER = shape(
    {
        "type": "Polygon",
        "coordinates": [
            [
                [-101.25, 34.59704151614417],
                [-88.24218749999999, 34.59704151614417],
                [-88.24218749999999, 41.244772343082076],
                [-101.25, 41.244772343082076],
                [-101.25, 34.59704151614417],
            ]
        ],
    }
)


class CreateItemFromHrefTest(unittest.TestCase):
    def test_create_item(self):
        path = test_data.get_external_data(CMIP_FILE_NAME)
        item = stac.create_item_from_href(path)

        self.assertEqual(item.id, "OR_ABI-L2-M1-M6_G16_s20211231619248")
        self.assertTrue(item.geometry)
        self.assertTrue(item.bbox)
        self.assertEqual(
            item.datetime, datetime(2021, 5, 3, 16, 19, 24, 800000, timezone.utc)
        )

        self.assertEqual(item.common_metadata.platform, "GOES-16")
        self.assertEqual(item.common_metadata.instruments, ["ABI"])

        self.assertTrue(
            "https://stac-extensions.github.io/processing/v1.0.0/schema.json"
            in item.stac_extensions
        )
        self.assertDictEqual(
            item.properties["processing:software"], {"stactools-goes": __version__}
        )

        self.assertEqual(item.properties["goes:image-type"], "MESOSCALE")
        self.assertEqual(item.properties["goes:mode"], "6")
        self.assertEqual(item.properties["goes:mesoscale-image-number"], 1)

        data = item.assets["CMIP_C02-nc"]
        self.assertEqual(data.href, path)
        self.assertEqual(
            data.title, "Cloud and Moisture Imagery reflectance factor - Band 02"
        )
        self.assertEqual(data.media_type, "application/netcdf")
        self.assertEqual(data.roles, ["data"])

        projection = ProjectionExtension.ext(item)
        self.assertIsNone(projection.epsg)
        self.assertIsNotNone(projection.wkt2)
        self.assertIsNotNone(projection.shape, [2000, 2000])
        expected_transform = [
            501.0043288718852,
            0.0,
            -2224459.203445637,
            0.0,
            -501.0043288718852,
            4068155.14931683,
            0.0,
            0.0,
            1.0,
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
        _ = stac.create_item_from_href(path, modify_href)
        self.assertTrue(did_it)

    def test_backoff_fn(self):
        did_it = False

        def with_backoff(fn: Callable[[], Any]) -> Any:
            nonlocal did_it
            did_it = True
            return fn()

        path = test_data.get_external_data(CMIP_FILE_NAME)
        _ = stac.create_item_from_href(path, backoff_func=with_backoff)
        self.assertTrue(did_it)

    def test_cog_directory(self):
        path = test_data.get_external_data(CMIP_FILE_NAME)
        with TemporaryDirectory() as tmp_dir:
            item = stac.create_item_from_href(path, cog_directory=tmp_dir)
            cog_asset = item.assets["CMIP_C02"]
            self.assertTrue(os.path.exists(cog_asset.href))
            self.assertEqual(
                cog_asset.title,
                "Cloud and Moisture Imagery reflectance factor - Band 02",
            )
            self.assertEqual(cog_asset.roles, ["data"])
            self.assertEqual(cog_asset.media_type, MediaType.COG)

    def test_different_product(self):
        path = test_data.get_path(
            "data-files/"
            "OR_ABI-L2-LSTM2-M6_G16_s20211381700538_e20211381700595_c20211381701211.nc"
        )
        item = stac.create_item_from_href(path)
        self.assertEqual(item.properties["goes:mesoscale-image-number"], 2)
        item.validate()

    def test_full_product_geometry(self):
        for path in [
            test_data.get_external_data(CMIP_FULL_FILE_NAME),
            test_data.get_external_data(PC_MCMIP_F_17),
        ]:
            with self.subTest(path):

                item = stac.create_item_from_href(path)
                self.assertNotIn("goes:mesoscale-image-number", item.properties)
                self.assertEqual(item.properties.get("goes:image-type"), "FULL DISK")
                geometry = shape(item.geometry)
                self.assertTrue(geometry.is_valid)

                # https://github.com/stactools-packages/goes/issues/4
                self.assertFalse(
                    math.isnan(geometry.area),
                    f"This geometry has a NaN area: {geometry}",
                )

                # Test is in a sane location
                bbox = box(*item.bbox)
                self.assertTrue(bbox.covers(geometry))
                self.assertTrue(geometry.contains(US_CENTER))

    def test_conus_product_geometry(self):
        path = test_data.get_external_data(PC_MCMIP_C)
        item = stac.create_item_from_href(path)
        self.assertNotIn("goes:mesoscale-image-number", item.properties)
        self.assertEqual(item.properties.get("goes:image-type"), "CONUS")
        geometry = shape(item.geometry)
        self.assertTrue(geometry.is_valid)
        self.assertFalse(
            math.isnan(geometry.area), f"This geometry has a NaN area: {geometry}"
        )

    def test_mcmip_eo(self):
        path = test_data.get_external_data(MCMIP_FILE_NAME)
        with TemporaryDirectory() as tmp_dir:
            item = stac.create_item_from_href(path, cog_directory=tmp_dir)
            data = item.assets["MCMIP-nc"]
            eo = EOExtension.ext(data)
            assert eo.bands
            self.assertEqual(len(eo.bands), 16)
            for band in eo.bands:
                self.assertIsNotNone(band.name)
                self.assertIsNotNone(band.center_wavelength)
            for channel in range(1, 17):
                cmi = item.assets[f"CMI_C{channel:0>2d}_2km"]
                eo = EOExtension.ext(cmi)
                assert eo.bands
                self.assertEqual(len(eo.bands), 1)
                self.assertEqual(eo.bands[0].name, f"ABI Band {channel}")
                dqf = item.assets[f"CMI_C{channel:0>2d}_DQF_2km"]
                eo = EOExtension.ext(dqf)
                self.assertIsNone(eo.bands)

    def test_fdc(self):
        path = test_data.get_external_data(PC_FDC_C)
        with TemporaryDirectory() as tmp_dir:
            item = stac.create_item_from_href(path, cog_directory=tmp_dir)
            self.assertEqual(item.properties.get("goes:image-type"), "CONUS")

            # All assets have the same shape, so none should have projection info
            self.assertIn("proj:shape", item.properties)
            for asset in item.assets.values():
                self.assertNotIn("proj:shape", asset.extra_fields)

            # Assert geometry is valid
            g = shape(item.geometry)
            self.assertTrue(g.is_valid)

    def test_lst_m(self):
        path = test_data.get_external_data(PC_LST_M)
        with TemporaryDirectory() as tmp_dir:
            item = stac.create_item_from_href(path, cog_directory=tmp_dir)
            self.assertEqual(item.properties.get("goes:image-type"), "MESOSCALE")

            # All assets have the same shape, so none should have projection info
            self.assertIn("proj:shape", item.properties)
            for asset in item.assets.values():
                self.assertNotIn("proj:shape", asset.extra_fields)

            # Assert geometry is valid
            g = shape(item.geometry)
            self.assertTrue(g.is_valid)

    def test_invalid_lat_lng(self):
        path = test_data.get_external_data(INVALID_LAT_LNG)
        with self.assertRaises(GOESMissingExtentError):
            stac.create_item_from_href(path)


class CreateItemTest(unittest.TestCase):
    def test_validate_product_hrefs(self) -> None:
        product_hrefs: List[ProductHrefs] = []

        mcmip_path = test_data.get_external_data(PC_MCMIP_F)
        mcmip_file_name = ABIL2FileName.from_href(mcmip_path)

        product_hrefs.append(ProductHrefs(nc_href=mcmip_path, cog_hrefs=None))

        cmip_name_different_start_date = dataclasses.replace(
            mcmip_file_name,
            product=ProductAcronym.CMIP,
            channel=1,
            start_time="20180100500416",
        )
        cmip_path = os.path.join(
            os.path.dirname(mcmip_path), cmip_name_different_start_date.to_str()
        )
        product_hrefs.append(ProductHrefs(nc_href=cmip_path, cog_hrefs=None))
        with self.assertRaises(GOESRProductHrefsError):
            _ = stac.create_item(product_hrefs)

    def test_combined_item(self) -> None:
        product_hrefs: List[ProductHrefs] = []

        mcmip_href = EXTERNAL_DATA[PC_MCMIP_C]["url"]
        mpc_data = MicrosoftPCData(mcmip_href)

        for product in [ProductAcronym.MCMIP, ProductAcronym.FDC]:
            # Use local path for main netCDF file
            nc_href = mpc_data.get_nc_href(product)
            if nc_href == mcmip_href:
                nc_href = test_data.get_external_data(PC_MCMIP_C)
            product_hrefs.append(
                ProductHrefs(nc_href=nc_href, cog_hrefs=mpc_data.get_cog_hrefs(product))
            )

        for channel in range(1, 17):
            product_hrefs.append(
                ProductHrefs(
                    nc_href=mpc_data.get_nc_href(ProductAcronym.CMIP, channel),
                    cog_hrefs=mpc_data.get_cog_hrefs(ProductAcronym.CMIP, channel),
                )
            )

        item = stac.create_item(
            product_hrefs, read_href_modifier=planetary_computer.sign
        )

        item.validate()

        # Ensure all expected assets are there

        expected_assets = set(["MCMIP-nc"])
        for band_idx in range(1, 17):
            expected_assets.add(f"CMIP_C{band_idx:0>2d}-nc")
            expected_assets.add(f"CMI_C{band_idx:0>2d}_2km")
            expected_assets.add(f"CMI_C{band_idx:0>2d}_DQF_2km")
            if band_idx in [1, 3, 5]:
                expected_assets.add(f"CMI_C{band_idx:0>2d}_1km")
                expected_assets.add(f"CMI_C{band_idx:0>2d}_DQF_1km")
            if band_idx == 2:
                expected_assets.add(f"CMI_C{band_idx:0>2d}_0.5km")
                expected_assets.add(f"CMI_C{band_idx:0>2d}_DQF_0.5km")

        expected_assets.add("FDC-nc")
        expected_assets.add("FDC_Mask")
        expected_assets.add("FDC_Temp")
        expected_assets.add("FDC_Area")
        expected_assets.add("FDC_Power")
        expected_assets.add("FDC_DQF")

        self.assertEqual(set(item.assets.keys()), expected_assets)

        # Validate some properties

        # CMIP COG assets with higher resolution should have a different
        # transform and shape than the one pulled from MCMIP.
        c2_full_res = item.assets["CMI_C02_0.5km"]
        c5_2km = item.assets["CMI_C05_2km"]
        self.assertNotEqual(
            ProjectionExtension.ext(c2_full_res).shape,
            ProjectionExtension.ext(c5_2km).shape,
        )

        # Ensure that the shape isn't set on the asset for assets that should match the item
        self.assertNotIn("proj:shape", c5_2km.extra_fields)
