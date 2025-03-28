import unittest
from tempfile import TemporaryDirectory

import planetary_computer
import pystac
import rasterio
from pystac.extensions.raster import RasterExtension

from stactools.goes import stac
from tests import (
    PC_CMIP_M_01,
    PC_CMIP_M_02,
    PC_CMIP_M_03,
    PC_CMIP_M_04,
    PC_CMIP_M_05,
    PC_FDC_C,
    PC_GOES_19,
    PC_GOES_19_CMIP,
    PC_LST_C,
    PC_LST_F,
    PC_MCMIP_C,
    PC_RRQPE_F,
    PC_SST_F,
    test_data,
)

TEST_DATA = [
    PC_CMIP_M_01,
    PC_CMIP_M_02,
    PC_CMIP_M_03,
    PC_CMIP_M_04,
    PC_CMIP_M_05,
    PC_FDC_C,
    PC_GOES_19,
    PC_GOES_19_CMIP,
    PC_LST_F,
    PC_LST_C,
    PC_MCMIP_C,
    PC_RRQPE_F,
    PC_SST_F,
]


class RasterExtensionTest(unittest.TestCase):
    def test_raster_values(self):
        for nc_name in TEST_DATA:
            with self.subTest(nc_name):
                with TemporaryDirectory() as cog_dir:
                    path = test_data.get_external_data(nc_name)
                    item = stac.create_item_from_href(path, cog_directory=cog_dir)

                    self.assertTrue(RasterExtension.has_extension(item))

                    for asset_key, asset in item.assets.items():
                        if asset.media_type == pystac.MediaType.COG:
                            raster = RasterExtension.ext(asset)
                            self.assertIsNotNone(raster.bands, msg=asset_key)
                            assert raster.bands
                            self.assertEqual(len(raster.bands), 1)
                            band = raster.bands[0]
                            self.assertIsNotNone(band.nodata)
                            assert band.nodata

                            signed_href = planetary_computer.sign(asset.href)
                            with rasterio.open(signed_href) as ds:
                                dtypes = {
                                    i: dtype for i, dtype in zip(ds.indexes, ds.dtypes)
                                }
                                dtype = dtypes[1]
                                nodata = ds.nodata
                                rough_resolution = ds.transform[0]

                                self.assertEqual(float(band.nodata), nodata)
                                self.assertEqual(band.data_type, str(dtype))
                                self.assertTrue(
                                    abs(band.spatial_resolution - rough_resolution)
                                    < 100,
                                    msg=(
                                        f"KEY {asset_key} "
                                        f"ACTUAL {rough_resolution}, "
                                        f"EXPECTED: {band.spatial_resolution}"
                                    ),
                                )
